#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VERCEL SERVERLESS FUNCTION — POST /api/register
Handler compatible avec l'hébergement cloud Vercel.
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# Ajout du dossier core
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core"))

from database import add_user
from notifier import send_welcome_email

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
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
                self.wfile.write(json.dumps({"success": False, "error": "Nom et contact requis."}).encode("utf-8"))
                return

            add_user(name=name, email=email, telegram=telegram, country=country, category=category)

            email_sent = False
            if email and "@" in email:
                success, _ = send_welcome_email(email, name, category, country)
                email_sent = success

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({
                "success": True,
                "message": f"Bienvenue {name} ! Ton profil est activé.",
                "email_sent": email_sent
            }, ensure_ascii=False).encode("utf-8"))

        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
