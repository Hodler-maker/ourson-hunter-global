#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERCEL SERVERLESS ENTRYPOINT — OURSON HUNTER GLOBAL
Sert l'application Web (GET) et traite les inscriptions (POST /api/register)
Compatible avec Vercel Python Runtime (WSGI)
"""

import json
import os
import sys

# Ajout du dossier core
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core"))

from database import add_user
from notifier import send_welcome_email, send_welcome_telegram

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
                    ("Cache-Control", "public, max-age=0, must-revalidate"),
                    ("Access-Control-Allow-Origin", "*"),
                ]
                start_response("200 OK", headers)
                return [content]
            except Exception:
                pass

    msg = f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>Ourson Hunter</title></head><body style='font-family:sans-serif;background:#0b1120;color:#fff;text-align:center;padding:50px;'><h1>Ourson Hunter Global</h1><p>Page {filename} en ligne.</p></body></html>".encode("utf-8")
    headers = [("Content-Type", "text/html; charset=utf-8"), ("Content-Length", str(len(msg)))]
    start_response("200 OK", headers)
    return [msg]

def app(environ, start_response):
    """
    Standard WSGI callable reconnu par Vercel.
    """
    method = environ.get("REQUEST_METHOD", "GET")
    raw_path = environ.get("PATH_INFO", "/").lower().strip("/")
    
    # Gestion des requêtes OPTIONS (CORS pre-flight)
    if method == "OPTIONS":
        headers = [
            ("Content-Type", "application/json"),
            ("Access-Control-Allow-Origin", "*"),
            ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
            ("Access-Control-Allow-Headers", "Content-Type")
        ]
        start_response("200 OK", headers)
        return [b""]

    # Requête GET -> Servir les pages HTML
    if method == "GET":
        if "evenement" in raw_path or "event" in raw_path:
            return serve_file("evenements.html", start_response)
        elif "admin" in raw_path:
            return serve_file("admin.html", start_response)
        elif "contact" in raw_path:
            return serve_file("contact.html", start_response)
        return serve_file("index.html", start_response)

    # Requête POST
    if method == "POST":
        try:
            content_length = int(environ.get("CONTENT_LENGTH", 0))
        except (ValueError, TypeError):
            content_length = 0

        request_body = environ["wsgi.input"].read(content_length) if content_length > 0 else b"{}"

        try:
            data = json.loads(request_body.decode("utf-8"))
        except Exception:
            data = {}

        # 1. Routage vers l'API Admin si action ou admin_key présent
        if "action" in data or "admin_key" in data or "admin" in raw_path:
            import io
            environ["wsgi.input"] = io.BytesIO(request_body)
            environ["CONTENT_LENGTH"] = str(len(request_body))
            try:
                sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
                import admin
                return admin.app(environ, start_response)
            except Exception as admin_err:
                headers = [("Content-Type", "application/json"), ("Access-Control-Allow-Origin", "*")]
                start_response("500 Internal Server Error", headers)
                return [json.dumps({"success": False, "error": f"Erreur admin API: {admin_err}"}).encode("utf-8")]

        # 2. Inscription utilisateur
        try:
            name = data.get("name", "").strip()
            email = data.get("email", "").strip()
            telegram = data.get("telegram", "").strip()
            category = data.get("category", "Community")
            country = data.get("country", "Togo")

            if not name or (not email and not telegram):
                headers = [("Content-Type", "application/json"), ("Access-Control-Allow-Origin", "*")]
                start_response("400 Bad Request", headers)
                return [json.dumps({"success": False, "error": "Nom et contact requis."}).encode("utf-8")]

            # Enregistrement en base de données
            try:
                add_user(name=name, email=email, telegram=telegram, country=country, category=category)
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
                "message": f"Bienvenue {name} ! Ton profil est activé.",
                "email_sent": email_sent,
                "telegram_sent": telegram_sent
            }
            headers = [("Content-Type", "application/json"), ("Access-Control-Allow-Origin", "*")]
            start_response("200 OK", headers)
            return [json.dumps(response_data, ensure_ascii=False).encode("utf-8")]

        except Exception as e:
            headers = [("Content-Type", "application/json"), ("Access-Control-Allow-Origin", "*")]
            start_response("500 Internal Server Error", headers)
            return [json.dumps({"success": False, "error": str(e)}).encode("utf-8")]

    # Autres méthodes non supportées
    headers = [("Content-Type", "application/json")]
    start_response("405 Method Not Allowed", headers)
    return [json.dumps({"error": "Méthode non autorisée"}).encode("utf-8")]

# Alias pour couvrir tous les cas de détection Vercel
application = app
handler = app
