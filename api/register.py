#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERCEL SERVERLESS FUNCTION — POST /api/register
Compatible avec Vercel Python Runtime (WSGI / ASGI / Handler)
"""

import json
import os
import sys

# Ajout du dossier core
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core"))

from database import add_user
from notifier import send_welcome_email

def app(environ, start_response):
    """
    Standard WSGI callable reconnu par Vercel.
    """
    method = environ.get("REQUEST_METHOD", "GET")
    
    # Gestion des requêtes OPTIONS (CORS pre-flight)
    if method == "OPTIONS":
        headers = [
            ("Content-Type", "application/json"),
            ("Access-Control-Allow-Origin", "*"),
            ("Access-Control-Allow-Methods", "POST, OPTIONS"),
            ("Access-Control-Allow-Headers", "Content-Type")
        ]
        start_response("200 OK", headers)
        return [b""]

    if method != "POST":
        headers = [("Content-Type", "application/json")]
        start_response("405 Method Not Allowed", headers)
        return [json.dumps({"error": "Méthode non autorisée"}).encode("utf-8")]

    try:
        content_length = int(environ.get("CONTENT_LENGTH", 0))
    except (ValueError, TypeError):
        content_length = 0

    request_body = environ["wsgi.input"].read(content_length) if content_length > 0 else b"{}"

    try:
        data = json.loads(request_body.decode("utf-8"))
        name = data.get("name", "").strip()
        email = data.get("email", "").strip()
        telegram = data.get("telegram", "").strip()
        category = data.get("category", "Community")
        country = data.get("country", "Togo")

        if not name or (not email and not telegram):
            headers = [("Content-Type", "application/json"), ("Access-Control-Allow-Origin", "*")]
            start_response("400 Bad Request", headers)
            return [json.dumps({"success": False, "error": "Nom et contact requis."}).encode("utf-8")]

        # Enregistrement
        add_user(name=name, email=email, telegram=telegram, country=country, category=category)

        # Envoi de l'e-mail de bienvenue
        email_sent = False
        if email and "@" in email:
            success, _ = send_welcome_email(email, name, category, country)
            email_sent = success

        response_data = {
            "success": True,
            "message": f"Bienvenue {name} ! Ton profil est activé.",
            "email_sent": email_sent
        }
        headers = [("Content-Type", "application/json"), ("Access-Control-Allow-Origin", "*")]
        start_response("200 OK", headers)
        return [json.dumps(response_data, ensure_ascii=False).encode("utf-8")]

    except Exception as e:
        headers = [("Content-Type", "application/json"), ("Access-Control-Allow-Origin", "*")]
        start_response("500 Internal Server Error", headers)
        return [json.dumps({"success": False, "error": str(e)}).encode("utf-8")]

# Alias pour couvrir tous les cas de détection Vercel
application = app
handler = app
