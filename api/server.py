#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SERVEUR WEB LOCAL & API D'INSCRIPTION — OURSON HUNTER GLOBAL
Sert le site web frontend (dossier web/) et gère l'API d'inscription :
- POST /api/register : Enregistre le profil dans la base de données et déclenche l'e-mail de bienvenue
- GET /api/jobs : Retourne les opportunités actives en JSON
"""

import os
import sys
import json
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Fix encodage UTF-8 pour Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Ajout du dossier core au path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT_DIR, "core"))

from database import add_user, get_all_active_opportunities
from notifier import send_welcome_email

WEB_DIR = os.path.join(ROOT_DIR, "web")

class OursonHunterHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def do_POST(self):
        if self.path == "/api/register":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode("utf-8"))
                name = data.get("name", "").strip()
                email = data.get("email", "").strip()
                telegram = data.get("telegram", "").strip()
                category = data.get("category", "Community")
                country = data.get("country", "Togo")

                if not name or (not email and not telegram):
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": False, "error": "Nom et e-mail requis."}).encode("utf-8"))
                    return

                # 1. Enregistrement en base de données
                user_id = add_user(
                    name=name,
                    email=email if email else None,
                    telegram=telegram if telegram else None,
                    country=country,
                    category=category
                )
                print(f"[NOUVEAU MEMBRE] {name} ({country} - {category}) enregistré avec succès (ID: {user_id})")

                # 2. Envoi de l'e-mail de bienvenue
                email_sent = False
                if email and "@" in email:
                    success, info = send_welcome_email(
                        recipient_email=email,
                        user_name=name,
                        category=category,
                        country=country
                    )
                    email_sent = success
                    print(f"[WELCOME EMAIL] Résultat vers {email} : {success} ({info})")

                # 3. Réponse JSON
                response = {
                    "success": True,
                    "message": f"Félicitations {name} ! Ton profil est activé.",
                    "email_sent": email_sent
                }
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(response, ensure_ascii=False).encode("utf-8"))

            except Exception as e:
                print(f"[ERREUR INSCRIPTION] : {e}")
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path == "/api/jobs":
            opps = get_all_active_opportunities()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(opps, ensure_ascii=False).encode("utf-8"))
        else:
            # Sert les fichiers statiques du dossier web/ (index.html, etc.)
            super().do_GET()

def run_server(port=8080):
    server_address = ("", port)
    httpd = HTTPServer(server_address, OursonHunterHandler)
    print(f"\n=======================================================")
    print(f"🐻 SERVEUR OURSON HUNTER EN LIGNE SUR http://localhost:{port}")
    print(f"👉 Ouvre http://localhost:{port} dans ton navigateur")
    print(f"=======================================================\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêt du serveur.")
        httpd.server_close()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port)
