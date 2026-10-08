#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERCEL SERVERLESS ENTRYPOINT — OURSON HUNTER GLOBAL / ANFAANI
Sert l'application Web (GET) et traite les inscriptions (POST /api/register).
Securise avec validation CORS stricte (aucun wildcard *).
Aucun emoji dans ce fichier.
"""

import json
import os
import sys

# Ajout du dossier core
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core"))

from database import add_user
from notifier import send_welcome_email, send_welcome_telegram
from security import get_cors_origin, is_origin_allowed

def serve_file(filename, start_response):
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates = [
        os.path.join(root_dir, filename),
        os.path.join(root_dir, "public", filename),
        os.path.join(root_dir, "web", filename),
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    content = f.read()
                headers = [
                    ("Content-Type", "text/html; charset=utf-8"),
                    ("Content-Length", str(len(content))),
                    ("Cache-Control", "public, max-age=0, must-revalidate")
                ]
                start_response("200 OK", headers)
                return [content]
            except Exception:
                pass

    msg = f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>ANFAANI</title></head><body style='font-family:sans-serif;background:#0b1120;color:#fff;text-align:center;padding:50px;'><h1>ANFAANI — Open the door to opportunity</h1><p>Page {filename} en ligne.</p></body></html>".encode("utf-8")
    headers = [("Content-Type", "text/html; charset=utf-8"), ("Content-Length", str(len(msg)))]
    start_response("200 OK", headers)
    return [msg]

def build_headers(status, payload_len, cors_origin=None):
    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Content-Length", str(payload_len))
    ]
    if cors_origin:
        headers.append(("Access-Control-Allow-Origin", cors_origin))
        headers.append(("Vary", "Origin"))
        headers.append(("Access-Control-Allow-Methods", "GET, POST, OPTIONS"))
        headers.append(("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Admin-Key"))
    return headers

def app(environ, start_response):
    method = environ.get("REQUEST_METHOD", "GET")
    raw_path = environ.get("PATH_INFO", "/").lower().strip("/")
    raw_origin = environ.get("HTTP_ORIGIN", "").strip()
    cors_origin = get_cors_origin(environ)

    # Gestion des requetes OPTIONS (CORS preflight)
    if method == "OPTIONS":
        if raw_origin and not cors_origin:
            start_response("403 Forbidden", [("Content-Type", "application/json")])
            return [json.dumps({"error": "Origine non autorisee"}).encode("utf-8")]

        headers = [
            ("Content-Type", "application/json"),
            ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
            ("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Admin-Key")
        ]
        if cors_origin:
            headers.append(("Access-Control-Allow-Origin", cors_origin))
            headers.append(("Vary", "Origin"))
        start_response("200 OK", headers)
        return [b""]

    # Requete GET -> Servir les pages HTML
    if method == "GET":
        if "evenement" in raw_path or "event" in raw_path:
            return serve_file("evenements.html", start_response)
        elif "admin" in raw_path:
            return serve_file("admin.html", start_response)
        elif "contact" in raw_path:
            return serve_file("contact.html", start_response)
        return serve_file("index.html", start_response)

    # Requete POST
    if method == "POST":
        # Verification d'origine non autorisee
        if raw_origin and not cors_origin:
            payload = json.dumps({"success": False, "error": "Origine non autorisee (CORS)"}).encode("utf-8")
            start_response("403 Forbidden", build_headers("403 Forbidden", len(payload), None))
            return [payload]

        try:
            content_length = int(environ.get("CONTENT_LENGTH", 0))
        except (ValueError, TypeError):
            content_length = 0

        request_body = environ["wsgi.input"].read(content_length) if content_length > 0 else b"{}"

        try:
            data = json.loads(request_body.decode("utf-8"))
        except Exception:
            data = {}

        # 1. Routage vers l'API Admin si action ou admin_key present
        if "action" in data or "admin_key" in data or "admin" in raw_path:
            import io
            environ["wsgi.input"] = io.BytesIO(request_body)
            environ["CONTENT_LENGTH"] = str(len(request_body))
            try:
                sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
                import admin
                return admin.app(environ, start_response)
            except Exception as admin_err:
                payload = json.dumps({"success": False, "error": f"Erreur admin API: {admin_err}"}).encode("utf-8")
                start_response("500 Internal Server Error", build_headers("500 Internal Server Error", len(payload), cors_origin))
                return [payload]

        # 2. Inscription utilisateur
        try:
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
                payload = json.dumps({"success": False, "error": "Nom et contact requis."}).encode("utf-8")
                start_response("400 Bad Request", build_headers("400 Bad Request", len(payload), cors_origin))
                return [payload]

            # Enregistrement en base de donnees
            try:
                add_user(name=name, email=email, telegram=telegram, country=country, category=category, experience_years=experience_years, skills=skills)
            except Exception as dbe:
                print(f"Erreur DB: {dbe}")

            # Envoi de l'e-mail de bienvenue
            email_sent = False
            if email and "@" in email:
                try:
                    success, _ = send_welcome_email(email, name, category, country)
                    email_sent = success
                except Exception as mail_err:
                    print(f"Erreur email: {mail_err}")

            # Envoi de la notification de bienvenue Telegram
            telegram_sent = False
            if telegram:
                try:
                    success, _ = send_welcome_telegram(telegram, name, category, country)
                    telegram_sent = success
                except Exception as tg_err:
                    print(f"Erreur telegram: {tg_err}")

            response_data = {
                "success": True,
                "message": f"Bienvenue {name} ! Ton profil est active.",
                "email_sent": email_sent,
                "telegram_sent": telegram_sent
            }
            payload = json.dumps(response_data, ensure_ascii=False).encode("utf-8")
            start_response("200 OK", build_headers("200 OK", len(payload), cors_origin))
            return [payload]

        except Exception as e:
            payload = json.dumps({"success": False, "error": str(e)}).encode("utf-8")
            start_response("500 Internal Server Error", build_headers("500 Internal Server Error", len(payload), cors_origin))
            return [payload]

    # Autres methodes non supportees
    payload = json.dumps({"error": "Methode non autorisee"}).encode("utf-8")
    start_response("405 Method Not Allowed", build_headers("405 Method Not Allowed", len(payload), cors_origin))
    return [payload]

application = app
handler = app
