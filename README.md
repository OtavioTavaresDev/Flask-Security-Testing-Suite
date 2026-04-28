# 🧪 Flask Security Testing Suite

> Aplicação web vulnerável construída com **Flask** e **Tailwind CSS** para testes de segurança ofensiva, simulações de ataque e validação de ferramentas de reconhecimento.  
> Alvo oficial do **Pentest Recon Engine**.

---

## 📖 Sobre o Projeto

A **Flask Security Testing Suite** é uma aplicação web intencionalmente vulnerável, projetada para:

- Servir como **alvo de testes** para scanners de segurança, pipelines de reconhecimento e ferramentas de brute force.
- Demonstrar **vulnerabilidades comuns** em aplicações web (credenciais fracas, debug exposto, cookies inseguros, chave secreta hardcoded).
- Fornecer um **painel administrativo** com controle de rate limiting, auto‑ban, monitoramento de requisições e exportação de logs — permitindo estudar também o **lado defensor**.
- Integrar‑se perfeitamente com o [Pentest Recon Engine](https://github.com/OtavioTavaresDev/Pentest-Recon-Engine), que automatiza a descoberta e exploração dessas vulnerabilidades.

---

## 🔗 Projetos Relacionados

| Projeto | Descrição |
|---------|-----------|
| [Pentest Recon Engine](https://github.com/OtavioTavaresDev/Pentest-Recon-Engine) | Engine de reconhecimento ofensivo com pipeline modular, GUI, brute force adaptativo e exportação profissional. |
| [Flask Security Testing Suite](https://github.com/OtavioTavaresDev/Flask-Security-Testing-Suite) | Esta aplicação vulnerável. |

---

## 🧩 Funcionalidades

### Páginas Públicas
- **`/`** — Tela de login com formulário POST (campos `username` e `password`). Design moderno com Tailwind CSS.
- **`/dashboard`** — Dashboard protegido por sessão. Exibe mensagem de boas‑vindas após login bem‑sucedido.

### Painel Administrativo (`/admin`)
- **Indicadores em tempo real** de RPS global e IPs banidos.
- **Rate Limiter Global**:
  - Ativar/desativar.
  - Modo manual (RPS float configurável) ou automático (adaptativo).
- **Rate Limiter por IP**:
  - Lista de IPs ativos com requisições por minuto (RPM) e RPS atual.
  - Campo para definir RPS individual.
  - Botão "Reset" para voltar ao padrão.
  - Botão "Banir".
- **Auto‑Ban (Detecção de Pentest)**:
  - Threshold configurável (req/min).
  - Detecção de padrões: volume excessivo, muitos 404, enumeração de diretórios.
  - IPs auto‑banidos aparecem em destaque.
- **IPs Banidos**: lista com opção de desbanir.
- **Monitoramento de Requisições**: logs em tempo real (timestamp, método, status, path, IP, User‑Agent). Botão "Banir" em cada linha.
- **Estatísticas**: total de requisições, IPs únicos, erros 404/403, top IPs, sugestões de ações.
- **Relatório de Segurança**: integração com o último scan do Pentest Recon Engine (lê `reports/report.json`).
- **Exportação de Logs**: JSON, CSV, SQL, Markdown, TXT.

### Vulnerabilidades Propositais
| # | Vulnerabilidade | Descrição |
|---|----------------|-----------|
| 1 | **Credenciais hardcoded** | `admin:123456`, `secure_user:P@ssw0rd!2024` armazenadas em texto plano. |
| 2 | **Chave secreta exposta** | `app.secret_key = "secret_key_123"` — permite forjar cookies de sessão. |
| 3 | **Cookie inseguro** | Sessão marcada com `httponly=False, secure=False`. |
| 4 | **Debug ativado** | `app.run(debug=True)` — expõe console Werkzeug com PIN (`669-931-934`). |
| 5 | **Autenticação fraca** | Verificação simples de usuário/senha sem proteção contra brute force. |
| 6 | **Rota protegida apenas por sessão** | `/dashboard` acessível se `session["logged_in"] == True`. |

---

## 🛠️ Tecnologias

- **Python 3.11+** / **Flask 3.x**
- **Tailwind CSS** (CDN) — design responsivo e moderno
- **Jinja2** — templates dinâmicos
- **Threading** — controle de concorrência
- **Persistência em memória** — sem banco de dados externo

---

## 🚀 Instalação e Uso

### Pré‑requisitos
- Python 3.11+
- pip
- Navegador moderno

```bash
# Clone o repositório
git clone https://github.com/OtavioTavaresDev/Flask-Security-Testing-Suite.git
cd Flask-Security-Testing-Suite

# Instale o Flask
pip install flask

# Execute a aplicação
python app.py
Acesse:

Aplicação vulnerável: http://127.0.0.1:5000

Painel de controle: http://127.0.0.1:5000/admin

🧪 Testando com Pentest Recon Engine
bash
# Clone a engine
git clone https://github.com/OtavioTavaresDev/Pentest-Recon-Engine.git
cd Pentest-Recon-Engine
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Inicie a GUI
python main_gui.py
Fluxo de teste:

Na aba Scan, insira 127.0.0.1 e clique em Quick Scan.

Na aba Brute Force, clique em Scan Forms e depois em Start Brute Force.

As credenciais admin:123456 serão descobertas.

Acesse o painel admin e veja as requisições sendo registradas em tempo real.

Ative o auto‑ban e use o Request Generator para simular um ataque de força bruta.

📊 Gerador de Requisições (Testes de Stress)
bash
python request_generator.py
Ferramenta GUI (Tkinter) para disparar requisições HTTP configuráveis:

Método: GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS.

RPS ajustável (float).

Total de requisições (0 = infinito).

Botão "Parar".

Ideal para testar os controles de rate limiting e auto‑ban do painel administrativo.

🧠 Exemplos de Exploração
Brute Force (via Pentest Recon Engine)
python
# A engine envia automaticamente combinações de usuário/senha
# Exemplo de requisição enviada:
POST / HTTP/1.1
username=admin&password=123456
# Resposta: 302 Found (login bem-sucedido)
Bypass de Autenticação via Console Werkzeug
Acesse http://127.0.0.1:5000/console

Insira o PIN do debugger (669-931-934)

Execute:

python
from __main__ import app
with app.test_request_context():
    from flask import session
    session["logged_in"] = True
Acesse http://127.0.0.1:5000/dashboard — autenticado sem credenciais.

Forja de Cookie de Sessão
bash
# Com a secret_key conhecida, é possível assinar cookies falsos
pip install flask-unsign
flask-unsign --sign --secret 'secret_key_123' --cookie "{'logged_in': True}"
Copie o cookie gerado e injete no navegador.

📁 Estrutura do Projeto
text
Flask-Security-Testing-Suite/
├── app.py                    # Aplicação principal (Flask)
├── templates/
│   ├── login.html            # Tela de login (Tailwind)
│   ├── dashboard.html        # Dashboard pós-login
│   └── admin.html            # Painel administrativo
├── passwords.txt             # Wordlist de senhas para brute force
└── request_generator.py      # Gerador de requisições HTTP
📄 Licença
MIT License. Consulte o arquivo LICENSE para mais detalhes.

⚠️ Aviso
Este projeto é destinado exclusivamente para fins educacionais e testes em ambientes controlados.
Não utilize contra sistemas sem autorização explícita.
O autor não se responsabiliza pelo uso indevido desta ferramenta.

👤 Autor
Otávio Tavares
Engenharia de Segurança Ofensiva
GitHub
