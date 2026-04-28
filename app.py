from flask import Flask, render_template, request, redirect, url_for, session, make_response, abort
from datetime import datetime, timedelta
import threading, time, json, os, csv, sqlite3, io

app = Flask(__name__)
app.secret_key = "secret_key_123"

users = {
    "admin": "123456",
    "secure_user": "P@ssw0rd!2024"
}

# ------------------------------------------------------------
# CONFIGURAÇÕES GLOBAIS
# ------------------------------------------------------------
MAX_LOGS = 2000
REPORT_PATH = "../reports/report.json"   # caminho corrigido

# Rate limiter global
rate_limit_enabled = True
RATE_LIMIT_RPS_GLOBAL = 10.0
AUTO_RPS_GLOBAL = False

# Rate limiter por IP
rate_limit_per_ip_enabled = False
RATE_LIMIT_RPS_PER_IP_DEFAULT = 5.0
AUTO_RPS_PER_IP = False
per_ip_rps = {}

# Auto-ban
AUTO_BAN_ENABLED = False
AUTO_BAN_THRESHOLD = 100
AUTO_BAN_PATTERNS = True

# Estruturas de controle
rate_limit_lock = threading.Lock()
last_request_time = 0
ip_timestamps = {}

request_logs = []
BANNED_IPS = set()
AUTO_BANNED_IPS = set()

# ------------------------------------------------------------
# MIDDLEWARE
# ------------------------------------------------------------
@app.before_request
def log_and_block():
    global last_request_time
    ip = request.remote_addr

    # Bloqueia IPs banidos (manual ou auto)
    if ip in BANNED_IPS or ip in AUTO_BANNED_IPS:
        if not request.path.startswith('/admin'):
            abort(403)

    # Log
    if not request.path.startswith('/static'):
        log_entry = {
            "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
            "method": request.method,
            "path": request.path,
            "ip": ip,
            "user_agent": request.headers.get("User-Agent", "")[:80],
            "status": None
        }
        request_logs.append(log_entry)
        if len(request_logs) > MAX_LOGS:
            request_logs.pop(0)

    # Rate limiting global
    if rate_limit_enabled and not request.path.startswith('/admin'):
        with rate_limit_lock:
            now = time.time()
            rps = compute_auto_rps_global() if AUTO_RPS_GLOBAL else RATE_LIMIT_RPS_GLOBAL
            if rps > 0:
                interval = 1.0 / rps
                if now - last_request_time < interval:
                    time.sleep(interval - (now - last_request_time))
            last_request_time = time.time()

    # Rate limiting por IP
    if rate_limit_per_ip_enabled and not request.path.startswith('/admin'):
        with rate_limit_lock:
            now = time.time()
            ip_timestamps.setdefault(ip, [])
            ip_timestamps[ip] = [t for t in ip_timestamps[ip] if now - t < 60]
            ip_timestamps[ip].append(now)

            if ip in per_ip_rps:
                rps_ip = per_ip_rps[ip]
            else:
                rps_ip = compute_auto_rps_per_ip(ip) if AUTO_RPS_PER_IP else RATE_LIMIT_RPS_PER_IP_DEFAULT
                per_ip_rps[ip] = rps_ip

            if rps_ip > 0 and len(ip_timestamps[ip]) > 1:
                recent = [t for t in ip_timestamps[ip] if now - t < 1.0]
                if len(recent) >= rps_ip:
                    time.sleep(1.0 / rps_ip)

    # Detecção de padrões de pentest (auto-ban) – executa após rate limits
    if AUTO_BAN_ENABLED and not request.path.startswith('/admin'):
        detect_pentest_patterns(ip)

@app.after_request
def update_log(response):
    if request.path.startswith('/static'):
        return response
    if request_logs:
        request_logs[-1]["status"] = response.status_code
    return response

# ------------------------------------------------------------
# FUNÇÕES AUXILIARES
# ------------------------------------------------------------
def compute_auto_rps_global():
    recent = [log for log in request_logs[-50:] if not log["path"].startswith('/admin')]
    if len(recent) < 5:
        return 5.0
    try:
        t1 = datetime.strptime(recent[-5]["timestamp"], "%H:%M:%S.%f")
        t2 = datetime.strptime(recent[-1]["timestamp"], "%H:%M:%S.%f")
        delta = (t2 - t1).total_seconds()
        if delta <= 0:
            return 5.0
        return max(0.1, min(100.0, round(5 / delta, 1)))
    except:
        return 5.0

def compute_auto_rps_per_ip(ip):
    now = time.time()
    recent = [t for t in ip_timestamps.get(ip, []) if now - t < 10]
    if len(recent) < 3:
        return 5.0
    rate = len(recent) / 10.0
    return max(0.1, min(50.0, round(rate, 1)))

def detect_pentest_patterns(ip):
    """Auto-ban se o IP ultrapassar limites ou apresentar comportamento suspeito."""
    now = time.time()
    recent_logs = [log for log in request_logs if log["ip"] == ip and now - datetime.strptime(log["timestamp"], "%H:%M:%S.%f").timestamp() < 60]
    req_count = len(recent_logs)

    # Ban por volume (limite em 1 minuto)
    if req_count > AUTO_BAN_THRESHOLD:
        if ip not in AUTO_BANNED_IPS:
            AUTO_BANNED_IPS.add(ip)
            request_logs.append({
                "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                "method": "SYSTEM",
                "path": f"/admin (auto-ban: {ip})",
                "ip": "0.0.0.0",
                "user_agent": "AutoBan",
                "status": None
            })
        return

    # Padrões adicionais (se ativado)
    if AUTO_BAN_PATTERNS:
        paths = [log["path"] for log in recent_logs]
        statuses = [log.get("status", 0) for log in recent_logs]

        # Muitos 404 em sequência
        if statuses.count(404) > req_count * 0.5 and req_count > 20:
            if ip not in AUTO_BANNED_IPS:
                AUTO_BANNED_IPS.add(ip)
            return

        # Enumeração de diretórios (muitos paths únicos)
        if len(set(paths)) > 30 and req_count > 30:
            if ip not in AUTO_BANNED_IPS:
                AUTO_BANNED_IPS.add(ip)
            return

def ip_requests_per_minute(ip):
    """Retorna a contagem de requisições do IP nos últimos 60 segundos."""
    now = time.time()
    if ip not in ip_timestamps:
        return 0
    return len([t for t in ip_timestamps[ip] if now - t < 60])

def all_active_ips():
    """Retorna conjunto de IPs que fizeram requisições nos últimos 60 segundos."""
    active = set()
    now = time.time()
    for ip, stamps in ip_timestamps.items():
        if any(now - t < 60 for t in stamps):
            active.add(ip)
    return active

# ------------------------------------------------------------
# ROTAS PÚBLICAS
# ------------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username in users and users[username] == password:
            session["logged_in"] = True
            response = make_response(redirect(url_for("dashboard")))
            response.set_cookie("session_id", "insecure_cookie", httponly=False, secure=False)
            return response
        return "Login falhou!", 401
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if session.get("logged_in"):
        return render_template("dashboard.html")
    return redirect(url_for("login"))

# ------------------------------------------------------------
# ADMIN PANEL
# ------------------------------------------------------------
@app.route("/admin")
def admin_panel():
    active_ips = list(all_active_ips())
    ip_data = []
    now = time.time()
    for ip in active_ips:
        rpm = ip_requests_per_minute(ip)
        current_rps = per_ip_rps.get(ip, RATE_LIMIT_RPS_PER_IP_DEFAULT)
        ip_data.append({
            "ip": ip,
            "rpm": rpm,
            "rps": current_rps,
            "auto": ip not in per_ip_rps and not AUTO_RPS_PER_IP  # modo padrão/auto
        })
    return render_template("admin.html",
                          logs=request_logs[-200:],
                          total_logs=len(request_logs),
                          banned_ips=sorted(BANNED_IPS | AUTO_BANNED_IPS),
                          auto_banned_ips=sorted(AUTO_BANNED_IPS),
                          rate_enabled=rate_limit_enabled,
                          rate_rps_global=RATE_LIMIT_RPS_GLOBAL,
                          auto_rps_global=AUTO_RPS_GLOBAL,
                          current_rps_global=compute_auto_rps_global() if AUTO_RPS_GLOBAL else RATE_LIMIT_RPS_GLOBAL,
                          rate_per_ip_enabled=rate_limit_per_ip_enabled,
                          rate_rps_default=RATE_LIMIT_RPS_PER_IP_DEFAULT,
                          auto_rps_per_ip=AUTO_RPS_PER_IP,
                          auto_ban_enabled=AUTO_BAN_ENABLED,
                          auto_ban_threshold=AUTO_BAN_THRESHOLD,
                          ip_data=ip_data,
                          stats=calculate_stats(),
                          report=load_security_report())

# Toggles e configurações (mantidos iguais ao último código funcional)
@app.route("/admin/toggle-rate", methods=["POST"])
def toggle_rate():
    global rate_limit_enabled
    rate_limit_enabled = not rate_limit_enabled
    return redirect(url_for("admin_panel"))

@app.route("/admin/toggle-auto-global", methods=["POST"])
def toggle_auto_global():
    global AUTO_RPS_GLOBAL
    AUTO_RPS_GLOBAL = not AUTO_RPS_GLOBAL
    return redirect(url_for("admin_panel"))

@app.route("/admin/toggle-rate-per-ip", methods=["POST"])
def toggle_rate_per_ip():
    global rate_limit_per_ip_enabled
    rate_limit_per_ip_enabled = not rate_limit_per_ip_enabled
    return redirect(url_for("admin_panel"))

@app.route("/admin/toggle-auto-per-ip", methods=["POST"])
def toggle_auto_per_ip():
    global AUTO_RPS_PER_IP
    AUTO_RPS_PER_IP = not AUTO_RPS_PER_IP
    return redirect(url_for("admin_panel"))

@app.route("/admin/set-rps-global", methods=["POST"])
def set_rps_global():
    global RATE_LIMIT_RPS_GLOBAL
    try:
        RATE_LIMIT_RPS_GLOBAL = max(0.1, min(100.0, round(float(request.form.get("rps", 10.0)), 1)))
    except:
        pass
    return redirect(url_for("admin_panel"))

@app.route("/admin/set-rps-per-ip-default", methods=["POST"])
def set_rps_per_ip_default():
    global RATE_LIMIT_RPS_PER_IP_DEFAULT
    try:
        RATE_LIMIT_RPS_PER_IP_DEFAULT = max(0.1, min(50.0, round(float(request.form.get("rps", 5.0)), 1)))
    except:
        pass
    return redirect(url_for("admin_panel"))

@app.route("/admin/set-ip-rps", methods=["POST"])
def set_ip_rps():
    ip = request.form.get("ip", "").strip()
    try:
        rps = float(request.form.get("rps", 5.0))
        rps = max(0.1, min(50.0, round(rps, 1)))
        if ip:
            per_ip_rps[ip] = rps
    except:
        pass
    return redirect(url_for("admin_panel"))

@app.route("/admin/reset-ip-rps", methods=["POST"])
def reset_ip_rps():
    ip = request.form.get("ip", "").strip()
    if ip and ip in per_ip_rps:
        del per_ip_rps[ip]
    return redirect(url_for("admin_panel"))

@app.route("/admin/toggle-auto-ban", methods=["POST"])
def toggle_auto_ban():
    global AUTO_BAN_ENABLED
    AUTO_BAN_ENABLED = not AUTO_BAN_ENABLED
    return redirect(url_for("admin_panel"))

@app.route("/admin/set-auto-ban-threshold", methods=["POST"])
def set_auto_ban_threshold():
    global AUTO_BAN_THRESHOLD
    try:
        AUTO_BAN_THRESHOLD = max(10, min(1000, int(request.form.get("threshold", 100))))
    except:
        pass
    return redirect(url_for("admin_panel"))

@app.route("/admin/clear-logs", methods=["POST"])
def clear_logs():
    global request_logs
    request_logs = []
    return redirect(url_for("admin_panel"))

@app.route("/admin/ban-ip", methods=["POST"])
def ban_ip():
    ip = request.form.get("ip", "").strip()
    if ip:
        BANNED_IPS.add(ip)
    return redirect(url_for("admin_panel"))

@app.route("/admin/unban-ip", methods=["POST"])
def unban_ip():
    ip = request.form.get("ip", "").strip()
    BANNED_IPS.discard(ip)
    AUTO_BANNED_IPS.discard(ip)
    return redirect(url_for("admin_panel"))

# Exportação (mesma lógica anterior)
@app.route("/admin/export/<format>")
def export_data(format):
    if format == "json":
        return export_json()
    elif format == "csv":
        return export_csv()
    elif format == "sql":
        return export_sql()
    elif format == "md":
        return export_md()
    elif format == "txt":
        return export_txt()
    return "Formato inválido", 400

def export_json():
    data = {
        "exported_at": datetime.now().isoformat(),
        "total_logs": len(request_logs),
        "banned_ips": list(BANNED_IPS | AUTO_BANNED_IPS),
        "rate_limits": {
            "global_rps": RATE_LIMIT_RPS_GLOBAL,
            "per_ip_rps_default": RATE_LIMIT_RPS_PER_IP_DEFAULT,
            "auto_ban": AUTO_BAN_ENABLED
        },
        "logs": request_logs[-500:] if request_logs else []
    }
    return app.response_class(
        response=json.dumps(data, indent=2),
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment;filename=admin_export.json'}
    )

def export_csv():
    si = io.StringIO()
    writer = csv.writer(si)
    writer.writerow(["timestamp", "method", "path", "ip", "status", "user_agent"])
    for log in (request_logs[-500:] if request_logs else []):
        writer.writerow([log.get(k, "") for k in ["timestamp", "method", "path", "ip", "status", "user_agent"]])
    return app.response_class(
        response=si.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=admin_logs.csv'}
    )

def export_sql():
    si = io.StringIO()
    si.write("CREATE TABLE IF NOT EXISTS logs (timestamp TEXT, method TEXT, path TEXT, ip TEXT, status INTEGER, user_agent TEXT);\n")
    for log in (request_logs[-500:] if request_logs else []):
        si.write(f"INSERT INTO logs VALUES ('{log['timestamp']}', '{log['method']}', '{log['path']}', '{log['ip']}', {log.get('status',0)}, '{log.get('user_agent','')}');\n")
    return app.response_class(
        response=si.getvalue(),
        mimetype='text/sql',
        headers={'Content-Disposition': 'attachment;filename=admin_logs.sql'}
    )

def export_md():
    lines = ["# Admin Logs", f"Exported: {datetime.now().isoformat()}", "", "| Timestamp | Method | Path | IP | Status |", "|---|---|---|---|---|"]
    logs_slice = request_logs[-200:] if request_logs else []
    for log in logs_slice:
        lines.append(f"| {log['timestamp']} | {log['method']} | {log['path']} | {log['ip']} | {log.get('status','')} |")
    return app.response_class(
        response="\n".join(lines),
        mimetype='text/markdown',
        headers={'Content-Disposition': 'attachment;filename=admin_logs.md'}
    )

def export_txt():
    lines = ["Admin Logs Export", f"Exported: {datetime.now().isoformat()}", ""]
    logs_slice = request_logs[-200:] if request_logs else []
    for log in logs_slice:
        lines.append(f"{log['timestamp']} {log['method']} {log['path']} {log['ip']} {log.get('status','')}")
    return app.response_class(
        response="\n".join(lines),
        mimetype='text/plain',
        headers={'Content-Disposition': 'attachment;filename=admin_logs.txt'}
    )

# ------------------------------------------------------------
# ESTATÍSTICAS (sem alterações)
# ------------------------------------------------------------
def calculate_stats():
    if not request_logs:
        return {}
    total = len(request_logs)
    ips = {}
    methods = {}
    statuses = {}
    paths = {}
    for log in request_logs:
        ip = log["ip"]
        ips[ip] = ips.get(ip, 0) + 1
        m = log["method"]
        methods[m] = methods.get(m, 0) + 1
        s = log.get("status", 0)
        statuses[s] = statuses.get(s, 0) + 1
        p = log["path"]
        paths[p] = paths.get(p, 0) + 1

    suspicious_ips = [ip for ip, count in ips.items() if count > 50]
    high_404 = statuses.get(404, 0) > total * 0.2
    high_403 = statuses.get(403, 0) > total * 0.1
    avg_req_per_ip = total / max(len(ips), 1)

    suggestions = generate_suggestions(total, statuses, suspicious_ips, avg_req_per_ip)
    return {
        "total": total,
        "unique_ips": len(ips),
        "top_ips": sorted(ips.items(), key=lambda x: x[1], reverse=True)[:5],
        "methods": methods,
        "statuses": statuses,
        "errors_404": statuses.get(404, 0),
        "errors_403": statuses.get(403, 0),
        "suspicious_ips": suspicious_ips,
        "high_404": high_404,
        "high_403": high_403,
        "avg_req_per_ip": round(avg_req_per_ip, 1),
        "suggestions": suggestions
    }

def generate_suggestions(total, statuses, suspicious_ips, avg_req_per_ip):
    sugg = []
    if statuses.get(404, 0) > total * 0.3:
        sugg.append(f"Muitos erros 404 ({statuses[404]}) – possível enumeração de diretórios. Aumente rate limit ou ative auto-ban.")
    if statuses.get(403, 0) > total * 0.1:
        sugg.append(f"Muitos erros 403 ({statuses[403]}) – possível ataque de força bruta ou acesso não autorizado.")
    if suspicious_ips:
        sugg.append(f"IPs suspeitos: {', '.join(suspicious_ips[:3])}. Considere banir ou monitorar.")
    if total > 500:
        sugg.append("Alto volume de tráfego – monitore possíveis ataques DDoS ou scan intensivo.")
    if avg_req_per_ip > 50:
        sugg.append(f"Média alta de requisições por IP ({avg_req_per_ip}) – possível ataque concentrado.")
    return sugg

def load_security_report():
    try:
        path = os.path.join(os.path.dirname(__file__), REPORT_PATH)
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
            return {
                "target": data.get("target", "N/A"),
                "generated_at": data.get("generated_at", ""),
                "open_ports": data.get("open_ports", []),
                "endpoints_count": len(data.get("endpoints", [])),
                "findings_count": len(data.get("findings", [])),
                "high_findings": [f for f in data.get("findings", []) if f.get("severity") == "high"],
                "suggestions": data.get("suggestions", [])
            }
    except:
        pass
    return None

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
