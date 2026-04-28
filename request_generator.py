#!/usr/bin/env python3
"""GUI para gerar requisições HTTP de teste (GET/POST/PUT/DELETE) com controle de RPS."""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import requests

class RequestGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("HTTP Request Generator")
        self.root.geometry("700x600")
        self.stop_event = threading.Event()
        self.build_ui()

    def build_ui(self):
        # URL
        ttk.Label(self.root, text="URL:").pack(pady=2)
        self.url_var = tk.StringVar(value="http://127.0.0.1:5000")
        ttk.Entry(self.root, textvariable=self.url_var, width=80).pack(pady=2)

        # Método
        ttk.Label(self.root, text="Método:").pack(pady=2)
        method_frame = ttk.Frame(self.root)
        method_frame.pack()
        self.method_var = tk.StringVar(value="GET")
        for m in ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]:
            ttk.Radiobutton(method_frame, text=m, variable=self.method_var, value=m).pack(side=tk.LEFT, padx=5)

        # Dados POST (opcional)
        ttk.Label(self.root, text="Dados (para POST/PUT, ex: key=value&key2=value2):").pack(pady=2)
        self.data_var = tk.StringVar()
        ttk.Entry(self.root, textvariable=self.data_var, width=80).pack(pady=2)

        # Parâmetros de controle
        control_frame = ttk.Frame(self.root)
        control_frame.pack(pady=10, fill=tk.X, padx=10)

        ttk.Label(control_frame, text="RPS:").grid(row=0, column=0, sticky="w")
        self.rps_var = tk.DoubleVar(value=5.0)
        ttk.Entry(control_frame, textvariable=self.rps_var, width=8).grid(row=0, column=1, sticky="w", padx=5)

        ttk.Label(control_frame, text="Total de requisições (0 = infinito):").grid(row=1, column=0, sticky="w")
        self.total_var = tk.IntVar(value=20)
        ttk.Entry(control_frame, textvariable=self.total_var, width=8).grid(row=1, column=1, sticky="w", padx=5)

        # Botões
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)
        self.start_btn = ttk.Button(btn_frame, text="Iniciar", command=self.start)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        self.stop_btn = ttk.Button(btn_frame, text="Parar", command=self.stop, state="disabled")
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        # Log
        self.log = scrolledtext.ScrolledText(self.root, height=15, state='disabled')
        self.log.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def log_msg(self, msg):
        self.log.configure(state='normal')
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)
        self.log.configure(state='disabled')

    def start(self):
        url = self.url_var.get().strip()
        method = self.method_var.get()
        data_str = self.data_var.get().strip()
        rps = self.rps_var.get()
        total = self.total_var.get()

        if not url:
            messagebox.showwarning("Erro", "Informe uma URL.")
            return

        self.stop_event.clear()
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        threading.Thread(target=self._run, args=(url, method, data_str, rps, total), daemon=True).start()

    def stop(self):
        self.stop_event.set()
        self.log_msg("[INFO] Parando... (aguardando requisições atuais terminarem)")
        self.stop_btn.configure(state="disabled")

    def _run(self, url, method, data_str, rps, total):
        count = 0
        interval = 1.0 / rps if rps > 0 else 0
        while not self.stop_event.is_set():
            if total > 0 and count >= total:
                break

            try:
                if method == "GET":
                    resp = requests.get(url, timeout=5)
                elif method == "POST":
                    resp = requests.post(url, data=data_str, timeout=5)
                elif method == "PUT":
                    resp = requests.put(url, data=data_str, timeout=5)
                elif method == "DELETE":
                    resp = requests.delete(url, timeout=5)
                elif method == "PATCH":
                    resp = requests.patch(url, data=data_str, timeout=5)
                elif method == "HEAD":
                    resp = requests.head(url, timeout=5)
                elif method == "OPTIONS":
                    resp = requests.options(url, timeout=5)
                else:
                    self.log_msg(f"[ERROR] Método {method} não suportado.")
                    break

                status = resp.status_code
                length = len(resp.content)
                count += 1
                self.log_msg(f"[{count}] {method} {url} -> {status} | size: {length}")
            except Exception as e:
                count += 1
                self.log_msg(f"[{count}] ERRO: {e}")

            if interval > 0:
                time.sleep(interval)

        self.log_msg(f"[DONE] {count} requisições enviadas.")
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = RequestGenerator(root)
    root.mainloop()
