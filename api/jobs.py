#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API JOBS — OURSON HUNTER GLOBAL / ANFAANI
Renvoie la liste des opportunites et offres actives avec restriction CORS stricte.
Aucun emoji dans ce fichier.
"""

import json
import os
import sys

# Ajout du dossier core
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core"))

from database import get_all_active_opportunities
from security import get_cors_origin

def app(environ, start_response):
    method = environ.get("REQUEST_METHOD", "GET")
    raw_origin = environ.get("HTTP_ORIGIN", "").strip()
    cors_origin = get_cors_origin(environ)

    if method == "OPTIONS":
        if raw_origin and not cors_origin:
            start_response("403 Forbidden", [("Content-Type", "application/json")])
            return [json.dumps({"error": "Origine non autorisee"}).encode("utf-8")]

        headers = [
            ("Content-Type", "application/json"),
            ("Access-Control-Allow-Methods", "GET, OPTIONS"),
            ("Access-Control-Allow-Headers", "Content-Type")
        ]
        if cors_origin:
            headers.append(("Access-Control-Allow-Origin", cors_origin))
            headers.append(("Vary", "Origin"))
        start_response("200 OK", headers)
        return [b""]

    try:
        jobs = get_all_active_opportunities()
    except Exception:
        jobs = []

    payload = json.dumps(jobs, ensure_ascii=False).encode("utf-8")
    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Content-Length", str(len(payload)))
    ]
    if cors_origin:
        headers.append(("Access-Control-Allow-Origin", cors_origin))
        headers.append(("Vary", "Origin"))
        headers.append(("Access-Control-Allow-Methods", "GET, OPTIONS"))
        headers.append(("Access-Control-Allow-Headers", "Content-Type"))

    start_response("200 OK", headers)
    return [payload]

application = app
handler = app
