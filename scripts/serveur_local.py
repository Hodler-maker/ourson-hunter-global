#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SERVEUR WEB LOCAL & API D'INSCRIPTION / ADMIN — OURSON HUNTER GLOBAL
Sert le site web frontend (dossier web/) et gère les APIs :
- POST /api/register : Enregistre le profil dans la base de données et déclenche l'e-mail de bienvenue
- POST /api/admin : Actions d'administration (ajout/suppression opportunités et événements)
- GET /api/jobs & GET /public_jobs.json : Retourne les opportunités actives en temps réel
- GET /api/events & GET /public_events.json : Retourne les événements actifs en temps réel
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

from database import (
    add_user,
    get_all_active_opportunities,
    add_opportunity,
    delete_opportunity,
    export_public_json,
    get_all_active_events,
    add_event,
    delete_event,
    export_public_events_json
)
from notifier import send_welcome_email

WEB_DIR = os.path.join(ROOT_DIR, "web")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "ourson2026")

class OursonHunterHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

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
                skills = data.get("skills", "")
                try:
                    experience_years = int(data.get("experience_years", 2))
                except (ValueError, TypeError):
                    experience_years = 2

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
                    category=category,
                    experience_years=experience_years,
                    skills=skills
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

        elif self.path == "/api/admin":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else b"{}"

            try:
                data = json.loads(post_data.decode("utf-8"))
            except Exception:
                self.send_response(400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": "JSON invalide"}).encode("utf-8"))
                return

            key = data.get("admin_key", "")
            if key != ADMIN_PASSWORD:
                self.send_response(401)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": "Mot de passe admin incorrect"}).encode("utf-8"))
                return

            action = data.get("action", "")
            res = {"success": True}

            try:
                if action == "login":
                    res = {"success": True, "message": "Authentifié avec succès"}

                elif action == "get_dashboard":
                    opps = get_all_active_opportunities()
                    evts = get_all_active_events()
                    res = {
                        "success": True,
                        "stats": {
                            "opportunities_count": len(opps),
                            "events_count": len(evts)
                        },
                        "opportunities": opps,
                        "events": evts
                    }

                elif action == "delete_event":
                    evt_id = data.get("id")
                    if not evt_id:
                        res = {"success": False, "error": "ID manquant"}
                    else:
                        deleted = delete_event(evt_id)
                        export_public_events_json()
                        print(f"[ADMIN] Événement {evt_id} supprimé.")
                        res = {"success": True, "message": f"Événement {evt_id} supprimé avec succès", "deleted": deleted}

                elif action == "add_event":
                    evt = data.get("event", {})
                    evt_id = evt.get("id") or f"EVT-MANUAL-{int(os.times().system * 1000)}"
                    add_event(
                        evt_id,
                        evt.get("title", "").strip(),
                        evt.get("organizer", "").strip(),
                        evt.get("date", "").strip(),
                        evt.get("location", "").strip(),
                        evt.get("country", "Togo").strip(),
                        evt.get("type", "Meetup").strip(),
                        evt.get("url", "").strip(),
                        evt.get("description", "").strip()
                    )
                    export_public_events_json()
                    print(f"[ADMIN] Événement {evt_id} ajouté.")
                    res = {"success": True, "message": "Événement publié", "id": evt_id}

                elif action == "delete_opportunity":
                    opp_id = data.get("id")
                    if not opp_id:
                        res = {"success": False, "error": "ID manquant"}
                    else:
                        deleted = delete_opportunity(opp_id)
                        export_public_json()
                        print(f"[ADMIN] Offre {opp_id} supprimée.")
                        res = {"success": True, "message": f"Offre {opp_id} supprimée", "deleted": deleted}

                elif action == "add_opportunity":
                    opp = data.get("opportunity", {})
                    opp_id = opp.get("id") or f"MANUAL-{int(os.times().system * 1000)}"
                    add_opportunity(
                        opp_id,
                        opp.get("title", "").strip(),
                        opp.get("company", "").strip(),
                        opp.get("category", "Community").strip(),
                        opp.get("type", "Remote").strip(),
                        opp.get("salary", "Selon profil").strip(),
                        opp.get("url", "").strip(),
                        opp.get("eligibility", "Global").strip(),
                        int(opp.get("score", 85)),
                        opp.get("notes", "").strip()
                    )
                    export_public_json()
                    print(f"[ADMIN] Offre {opp_id} ajoutée.")
                    res = {"success": True, "message": "Offre publiée", "id": opp_id}

                elif action == "run_cleaner":
                    try:
                        from cleaner import purge_dead_opportunities
                        purged = purge_dead_opportunities()
                        export_public_json()
                        res = {"success": True, "message": f"Nettoyage effectué : {len(purged)} offre(s) purgée(s)", "purged_ids": purged}
                    except Exception as ce:
                        res = {"success": True, "message": "Nettoyage terminé"}

                else:
                    res = {"success": False, "error": f"Action inconnue: {action}"}

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(res, ensure_ascii=False).encode("utf-8"))

            except Exception as e:
                print(f"[ERREUR ADMIN] : {e}")
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))

        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        clean_path = self.path.split("?")[0]

        if clean_path in ("/public_events.json", "/api/events"):
            evts = get_all_active_events()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(evts, ensure_ascii=False).encode("utf-8"))

        elif clean_path in ("/public_jobs.json", "/api/jobs"):
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
    print(f"[SERVEUR] ANFAANI EN LIGNE SUR http://localhost:{port}")
    print(f"[ACCES] Ouvrez http://localhost:{port} dans votre navigateur")
    print(f"=======================================================\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêt du serveur.")
        httpd.server_close()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port)
