#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API JOBS — OURSON HUNTER GLOBAL / ÀNFÀÀNÍ
Renvoie la liste des opportunités et offres actives publiques.
Endpoint Vercel Serverless : GET /api/jobs
"""

import json
import os
import sys

# Ajout du dossier core
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core"))

from database import get_all_active_opportunities

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
        jobs = get_all_active_opportunities()
    except Exception as e:
        jobs = []

    payload = json.dumps(jobs, ensure_ascii=False).encode("utf-8")
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
