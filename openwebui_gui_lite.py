#!/usr/bin/env python3
"""
Open WebUI Manager - Versione Lite (Tkinter)
Per Raspberry Pi Zero e dispositivi con risorse limitate
Autore: Carlo
"""

import sys
import os
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import platform
from pathlib import Path

# Directory dello script
SCRIPT_DIR = Path(__file__).parent.resolve()
SCRIPTS_DIR = SCRIPT_DIR / "scripts"

IS_WINDOWS = platform.system() == "Windows"


class OpenWebUIManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Open WebUI Manager Lite")
        self.root.geometry("600x500")
        self.root.minsize(500, 400)

        # Imposta icona
        icon_path = SCRIPT_DIR / "ICONA" / "ICONA_Trasparente.png"
        if icon_path.exists():
            try:
                icon = tk.PhotoImage(file=str(icon_path))
                self.root.iconphoto(True, icon)
                self._icon = icon  # Mantieni riferimento
            except Exception:
                pass  # Ignora errori icona

        # Stile
        style = ttk.Style()
        style.theme_use('clam')

        self.setup_ui()
        self.start_status_checker()

    def setup_ui(self):
        # Frame principale
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Titolo
        title = ttk.Label(main_frame, text="Open WebUI Manager",
                         font=('Helvetica', 16, 'bold'))
        title.pack(pady=(0, 10))

        # Frame stato
        status_frame = ttk.LabelFrame(main_frame, text="Stato Servizi", padding="10")
        status_frame.pack(fill=tk.X, pady=5)

        self.docker_status = ttk.Label(status_frame, text="* Docker: Verifica...")
        self.docker_status.pack(anchor=tk.W)

        self.ollama_status = ttk.Label(status_frame, text="* Ollama: Verifica...")
        self.ollama_status.pack(anchor=tk.W)

        self.webui_status = ttk.Label(status_frame, text="* Open WebUI: Verifica...")
        self.webui_status.pack(anchor=tk.W)

        # Frame pulsanti
        btn_frame = ttk.LabelFrame(main_frame, text="Azioni", padding="10")
        btn_frame.pack(fill=tk.X, pady=5)

        btn_grid = ttk.Frame(btn_frame)
        btn_grid.pack(fill=tk.X)

        ttk.Button(btn_grid, text="▶ Avvia", command=self.start_services).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(btn_grid, text="⏹ Ferma", command=self.stop_services).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(btn_grid, text="🔄 Riavvia", command=self.restart_services).grid(row=0, column=2, padx=5, pady=5, sticky="ew")
        ttk.Button(btn_grid, text="🌐 Browser", command=self.open_browser).grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        btn_grid.columnconfigure(0, weight=1)
        btn_grid.columnconfigure(1, weight=1)
        btn_grid.columnconfigure(2, weight=1)
        btn_grid.columnconfigure(3, weight=1)

        # Frame manutenzione
        maint_frame = ttk.LabelFrame(main_frame, text="Manutenzione", padding="10")
        maint_frame.pack(fill=tk.X, pady=5)

        maint_grid = ttk.Frame(maint_frame)
        maint_grid.pack(fill=tk.X)

        ttk.Button(maint_grid, text="⬆ Aggiorna", command=self.update).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        ttk.Button(maint_grid, text="🔧 Ripara", command=self.fix).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ttk.Button(maint_grid, text="📜 Log", command=self.show_logs).grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        maint_grid.columnconfigure(0, weight=1)
        maint_grid.columnconfigure(1, weight=1)
        maint_grid.columnconfigure(2, weight=1)

        # Area log
        log_frame = ttk.LabelFrame(main_frame, text="Output", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.log_area = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD,
                                                   font=('Courier', 9))
        self.log_area.pack(fill=tk.BOTH, expand=True)

        # Info
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=5)

        ttk.Label(info_frame, text="http://localhost:3000",
                 foreground="blue", cursor="hand2").pack(side=tk.LEFT)

    def log(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)

    def clear_log(self):
        self.log_area.delete(1.0, tk.END)

    def run_command(self, command, message=""):
        if message:
            self.log(message)

        def run():
            try:
                process = subprocess.Popen(
                    command, shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    cwd=SCRIPT_DIR,
                    text=True
                )
                for line in iter(process.stdout.readline, ''):
                    if line:
                        self.root.after(0, lambda l=line: self.log(l.strip()))
                exit_code = process.wait()
                if exit_code == 0:
                    self.root.after(0, lambda: self.log("[OK] Completato"))
                else:
                    self.root.after(0, lambda: self.log(f"[X] Errore (codice {exit_code})"))
            except Exception as e:
                self.root.after(0, lambda: self.log(f"[X] Errore: {e}"))

        threading.Thread(target=run, daemon=True).start()

    def check_docker(self):
        """Verifica se Docker e' disponibile e in esecuzione"""
        try:
            result = subprocess.run(
                "docker info",
                shell=True,
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False

    def docker_cmd(self):
        try:
            subprocess.run("docker compose version", shell=True, capture_output=True)
            return "docker compose"
        except:
            return "docker-compose"

    def start_services(self):
        self.clear_log()
        if not self.check_docker():
            self.log("[X] Docker Desktop non e' in esecuzione!")
            self.log("")
            self.log("Soluzione:")
            self.log("  1. Avvia Docker Desktop")
            self.log("  2. Attendi che sia completamente avviato")
            self.log("  3. Riprova")
            return
        cmd = f"cd {SCRIPT_DIR} && {self.docker_cmd()} up -d"
        self.run_command(cmd, "Avvio servizi...")

    def stop_services(self):
        self.clear_log()
        if not self.check_docker():
            self.log("[!] Docker Desktop non risponde")
            self.log("    I servizi potrebbero essere gia' fermi")
            return
        cmd = f"cd {SCRIPT_DIR} && {self.docker_cmd()} down"
        self.run_command(cmd, "Arresto servizi...")

    def restart_services(self):
        self.clear_log()
        if not self.check_docker():
            self.log("[X] Docker Desktop non e' in esecuzione!")
            self.log("    Avvia Docker Desktop e riprova")
            return
        cmd = f"cd {SCRIPT_DIR} && {self.docker_cmd()} restart"
        self.run_command(cmd, "Riavvio servizi...")

    def update(self):
        self.clear_log()
        if not self.check_docker():
            self.log("[X] Docker Desktop non e' in esecuzione!")
            self.log("    Avvia Docker Desktop e riprova")
            return
        cmd = f"cd {SCRIPT_DIR} && {self.docker_cmd()} pull && {self.docker_cmd()} up -d"
        self.run_command(cmd, "Aggiornamento...")

    def fix(self):
        self.clear_log()
        if not self.check_docker():
            self.log("[X] Docker Desktop non e' in esecuzione!")
            self.log("    Avvia Docker Desktop e riprova")
            return
        cmd = (f"cd {SCRIPT_DIR} && {self.docker_cmd()} down && "
               "docker rmi ghcr.io/open-webui/open-webui:main 2>/dev/null; "
               "docker pull ghcr.io/open-webui/open-webui:main && "
               f"{self.docker_cmd()} up -d")
        self.run_command(cmd, "Riparazione...")

    def show_logs(self):
        self.clear_log()
        if not self.check_docker():
            self.log("[X] Docker Desktop non e' in esecuzione!")
            return
        cmd = f"cd {SCRIPT_DIR} && {self.docker_cmd()} logs --tail=50"
        self.run_command(cmd, "Caricamento log...")

    def open_browser(self):
        url = 'http://localhost:3000'
        try:
            if IS_WINDOWS:
                os.startfile(url)
            elif platform.system() == "Darwin":
                subprocess.Popen(['open', url])
            else:
                subprocess.Popen(['xdg-open', url],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
        except:
            self.log(f"Apri manualmente: {url}")

    def check_status(self):
        # Docker
        docker_ok = self.check_docker()

        # Ollama
        try:
            result = subprocess.run(
                ['curl', '-s', 'http://localhost:11434/api/version'],
                capture_output=True, timeout=2
            )
            ollama_ok = result.returncode == 0
        except:
            ollama_ok = False

        # Open WebUI
        try:
            result = subprocess.run(
                ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}',
                 'http://localhost:3000'],
                capture_output=True, timeout=2, text=True
            )
            webui_ok = result.stdout.strip() in ['200', '302']
        except:
            webui_ok = False

        # Aggiorna UI
        if docker_ok:
            self.docker_status.config(text="* Docker: Attivo", foreground="green")
        else:
            self.docker_status.config(text="* Docker: Non attivo", foreground="red")

        if ollama_ok:
            self.ollama_status.config(text="* Ollama: Attivo", foreground="green")
        else:
            self.ollama_status.config(text="* Ollama: Non attivo", foreground="red")

        if webui_ok:
            self.webui_status.config(text="* Open WebUI: Attivo", foreground="green")
        else:
            self.webui_status.config(text="* Open WebUI: Non attivo", foreground="red")

    def start_status_checker(self):
        def check():
            self.check_status()
            self.root.after(5000, check)
        check()


def main():
    root = tk.Tk()
    app = OpenWebUIManager(root)
    root.mainloop()


if __name__ == "__main__":
    main()
