#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API EVENTS — OURSON HUNTER GLOBAL / ÀNFÀÀNÍ
Renvoie la liste des événements actifs publics.
Endpoint Vercel Serverless : GET /api/events
"""

import json
import os
import sys

# Ajout du dossier core
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core"))

from database import get_all_active_events

def app(environ, start_response):
    method = environ.get("REQUEST_METHOD", "GET")

    if method == "OPTIONS":
        headers = [
            ("Content-Type", "application/json"),
            ("Access-Control-Allow-Origin", "*"),
            ("Access-Control-Allow-Methods", "GET, OPTIONS"),
            ("Access-Control-Allow-Headers", "Content-Type")
        ]
        start_response("200 OK", headers)
        return [b""]

    try:
        events = get_all_active_events()
    except Exception as e:
        events = []

    payload = json.dumps(events, ensure_ascii=False).encode("utf-8")
    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Access-Control-Allow-Origin", "*"),
        ("Access-Control-Allow-Methods", "GET, OPTIONS"),
        ("Access-Control-Allow-Headers", "Content-Type"),
        ("Content-Length", str(len(payload)))
    ]
    start_response("200 OK", headers)
    return [payload]

application = app
handler = app
