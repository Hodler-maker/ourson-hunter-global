#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API EVENTS — OURSON HUNTER GLOBAL / ANFAANI
Renvoie la liste des evenements actifs publics avec restriction CORS stricte.
Aucun emoji dans ce fichier.
"""

import json
import os
import sys

# Ajout du dossier core
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core"))

from urllib.parse import parse_qs
from database import get_all_active_events, get_event_by_id
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

    # Traitement des parametres de requete (?id=...)
    query_string = environ.get("QUERY_STRING", "")
    params = parse_qs(query_string)
    event_id = params.get("id", [None])[0]

    if event_id:
        evt = get_event_by_id(event_id)
        if evt:
            payload = json.dumps({"success": True, "event": evt}, ensure_ascii=False).encode("utf-8")
            status = "200 OK"
        else:
            payload = json.dumps({"success": False, "error": "Evenement introuvable"}, ensure_ascii=False).encode("utf-8")
            status = "404 Not Found"
    else:
        try:
            events = get_all_active_events()
        except Exception:
            events = []
        payload = json.dumps(events, ensure_ascii=False).encode("utf-8")
        status = "200 OK"

    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Content-Length", str(len(payload)))
    ]
    if cors_origin:
        headers.append(("Access-Control-Allow-Origin", cors_origin))
        headers.append(("Vary", "Origin"))
        headers.append(("Access-Control-Allow-Methods", "GET, OPTIONS"))
        headers.append(("Access-Control-Allow-Headers", "Content-Type"))

    start_response(status, headers)
    return [payload]

application = app
handler = app
