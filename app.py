from flask import Flask, render_template, request, redirect, url_for, session, make_response

app = Flask(__name__)
app.secret_key = "secret_key_123"  # Chave insegura proposital

# Banco de dados "fake" em memória
users = {
    "admin": "123456",              # Senha fraca
    "secure_user": "P@ssw0rd!2024"  # Senha forte
}

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Vulnerabilidade 1: Verificação insegura
        if username in users and users[username] == password:
            session["logged_in"] = True
            response = make_response(redirect(url_for("dashboard")))
            # Vulnerabilidade 2: Cookie não seguro
            response.set_cookie("session_id", "insecure_cookie", httponly=False, secure=False)
            return response
        return "Login falhou!", 401

    return render_template("login.html") 

@app.route("/dashboard")
def dashboard():
    if session.get("logged_in"):
        return "<h1>Parabéns! Você hackeou o sistema! 🎉</h1>"
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)  # Debug ativado (inseguro)