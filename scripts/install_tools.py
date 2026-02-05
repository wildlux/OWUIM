#!/usr/bin/env python3
"""
Script per installare automaticamente tutti i tools in Open WebUI
Autore: Carlo
"""

import requests
import os
import sys
import getpass

BASE_URL = "http://localhost:3000"

# Lista dei file tools da installare
TOOLS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Tools OWUI")

TOOLS_FILES = [
    "text_assistant.py",
    "math_assistant.py",
    "code_assistant.py",
    "book_assistant.py",
    "study_assistant.py",
    "creative_writing.py",
    "research_assistant.py",
    "book_publishing.py",
    "productivity_assistant.py",
    "finance_italian.py",
    "scientific_council.py",
]


def login(email: str, password: str) -> str:
    """Effettua il login e restituisce il token JWT"""
    response = requests.post(
        f"{BASE_URL}/api/v1/auths/signin",
        json={"email": email, "password": password}
    )

    if response.status_code == 200:
        data = response.json()
        return data.get("token")
    else:
        print(f"❌ Errore login: {response.json().get('detail', 'Errore sconosciuto')}")
        return None


def add_tool(token: str, tool_content: str) -> bool:
    """Aggiunge un tool a Open WebUI"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Estrai metadata dal contenuto
    lines = tool_content.split('\n')
    name = "Tool"
    description = ""

    for line in lines[:20]:
        if 'title:' in line:
            name = line.split('title:')[1].strip().strip('"')
        if 'description:' in line:
            description = line.split('description:')[1].strip().strip('"')

    # Genera ID dal nome
    tool_id = name.lower().replace(' ', '_').replace('-', '_')

    payload = {
        "id": tool_id,
        "name": name,
        "content": tool_content,
        "meta": {
            "description": description
        }
    }

    # Prima prova a creare
    response = requests.post(
        f"{BASE_URL}/api/v1/tools/create",
        headers=headers,
        json=payload
    )

    if response.status_code == 200:
        return True, "creato"
    elif response.status_code == 400 and "already exists" in response.text.lower():
        # Se esiste, prova ad aggiornare
        response = requests.post(
            f"{BASE_URL}/api/v1/tools/id/{tool_id}/update",
            headers=headers,
            json=payload
        )
        if response.status_code == 200:
            return True, "aggiornato"

    return False, response.text


def main():
    print("=" * 50)
    print("  🔧 Installazione Tools Open WebUI")
    print("=" * 50)
    print()

    # Verifica che la cartella tools esista
    if not os.path.exists(TOOLS_DIR):
        print(f"❌ Cartella tools non trovata: {TOOLS_DIR}")
        sys.exit(1)

    # Chiedi credenziali
    print("Inserisci le credenziali di Open WebUI")
    print("(devi avere un account admin)")
    print()

    email = input("📧 Email: ").strip()
    password = getpass.getpass("🔑 Password: ")

    print()
    print("🔄 Login in corso...")

    token = login(email, password)
    if not token:
        print("❌ Login fallito. Verifica le credenziali.")
        sys.exit(1)

    print("✅ Login effettuato!")
    print()
    print("📦 Installazione tools...")
    print("-" * 50)

    successi = 0
    errori = 0

    for tool_file in TOOLS_FILES:
        tool_path = os.path.join(TOOLS_DIR, tool_file)

        if not os.path.exists(tool_path):
            print(f"⚠️  {tool_file} - File non trovato")
            errori += 1
            continue

        with open(tool_path, 'r', encoding='utf-8') as f:
            content = f.read()

        success, status = add_tool(token, content)

        if success:
            print(f"✅ {tool_file} - {status}")
            successi += 1
        else:
            print(f"❌ {tool_file} - Errore: {status[:50]}...")
            errori += 1

    print("-" * 50)
    print()
    print(f"📊 Risultato: {successi} installati, {errori} errori")
    print()

    if successi > 0:
        print("🎉 Installazione completata!")
        print()
        print("Per abilitare i tools:")
        print("1. Vai su http://localhost:3000")
        print("2. Apri Admin Panel → Functions → Tools")
        print("3. Attiva i tools che vuoi usare")
        print("4. Nelle chat, clicca + per selezionare i tools")

    return 0 if errori == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
