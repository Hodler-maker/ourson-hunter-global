#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API ADMIN — OURSON HUNTER GLOBAL / ANFAANI
Gestion securisee des opportunites et des evenements Web3.
Protection anti brute-force avec rate limiting, comparaison a temps constant et CORS restreint.
Aucun emoji dans ce fichier.
"""

import json
import os
import sys
import time

# Ajout du dossier core
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core"))

from database import (
    get_connection,
    add_opportunity,
    delete_opportunity,
    get_all_active_opportunities,
    export_public_json,
    add_event,
    delete_event,
    get_all_active_events,
    export_public_events_json,
    get_all_active_users
)

from security import (
    get_cors_origin,
    is_origin_allowed,
    get_client_ip,
    check_admin_rate_limit,
    record_admin_failed_attempt,
    reset_admin_rate_limit,
    verify_admin_password,
    MAX_FAILED_ATTEMPTS
)

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "ourson2026")

def json_response(start_response, status_str, data, origin=None, extra_headers=None):
    payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Content-Length", str(len(payload)))
    ]
    if origin:
        headers.append(("Access-Control-Allow-Origin", origin))
        headers.append(("Vary", "Origin"))
        headers.append(("Access-Control-Allow-Methods", "GET, POST, OPTIONS"))
        headers.append(("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Admin-Key"))
    if extra_headers:
        headers.extend(extra_headers)
    start_response(status_str, headers)
    return [payload]

def app(environ, start_response):
    method = environ.get("REQUEST_METHOD", "GET")
    raw_origin = environ.get("HTTP_ORIGIN", "").strip()
    cors_origin = get_cors_origin(environ)
    client_ip = get_client_ip(environ)

    # 1. Gestion des requetes OPTIONS (CORS preflight)
    if method == "OPTIONS":
        if raw_origin and not cors_origin:
            headers = [("Content-Type", "application/json")]
            start_response("403 Forbidden", headers)
            return [json.dumps({"success": False, "error": "Origine non autorisee (CORS)"}).encode("utf-8")]

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

    # 2. Verification de l'origine sur requete directe
    if raw_origin and not cors_origin:
        return json_response(start_response, "403 Forbidden", {
            "success": False,
            "error": "Acces cross-origin refuse. Origine non autorisee."
        }, origin=None)

    # 3. Traitement POST
    if method == "POST":
        try:
            content_length = int(environ.get("CONTENT_LENGTH", 0))
        except (ValueError, TypeError):
            content_length = 0

        request_body = environ["wsgi.input"].read(content_length) if content_length > 0 else b"{}"

        try:
            data = json.loads(request_body.decode("utf-8"))
        except Exception:
            return json_response(start_response, "400 Bad Request", {
                "success": False,
                "error": "JSON invalide"
            }, origin=cors_origin)

        action = data.get("action", "")

        # Actions publiques autorisees sans cle admin
        if action == "get_events":
            return json_response(start_response, "200 OK", get_all_active_events(), origin=cors_origin)
        if action == "get_jobs":
            return json_response(start_response, "200 OK", get_all_active_opportunities(), origin=cors_origin)

        # Verification stricte du Rate Limiting pour toutes les actions admin
        is_allowed, retry_after, recent_failures = check_admin_rate_limit(client_ip)
        if not is_allowed:
            extra_headers = [("Retry-After", str(retry_after))]
            return json_response(start_response, "429 Too Many Requests", {
                "success": False,
                "error": f"Trop de tentatives de connexion. IP temporairement bloquee. Reessayez dans {retry_after} secondes.",
                "retry_after": retry_after
            }, origin=cors_origin, extra_headers=extra_headers)

        # Verification securisee du mot de passe admin (HMAC constant-time)
        key = data.get("admin_key", "")
        if not verify_admin_password(key, ADMIN_PASSWORD):
            failures = record_admin_failed_attempt(client_ip)
            # Ralentissement artificiel pour neutraliser les attaques en rafale
            time.sleep(1.2)
            if failures >= MAX_FAILED_ATTEMPTS:
                extra_headers = [("Retry-After", "900")]
                return json_response(start_response, "429 Too Many Requests", {
                    "success": False,
                    "error": "Trop de tentatives echouees. IP temporairement bloquee pendant 15 minutes.",
                    "retry_after": 900
                }, origin=cors_origin, extra_headers=extra_headers)

            remaining = MAX_FAILED_ATTEMPTS - failures
            return json_response(start_response, "401 Unauthorized", {
                "success": False,
                "error": f"Mot de passe administrateur incorrect. ({remaining} tentative(s) restante(s))"
            }, origin=cors_origin)

        # Authentification reussie -> reinitialisation des echecs pour cette IP
        reset_admin_rate_limit(client_ip)

        # Action: login
        if action == "login":
            return json_response(start_response, "200 OK", {
                "success": True,
                "message": "Authentification reussie"
            }, origin=cors_origin)

        # Action: get_dashboard
        if action == "get_dashboard":
            try:
                opps = get_all_active_opportunities()
                events = get_all_active_events()
                users = get_all_active_users()
                return json_response(start_response, "200 OK", {
                    "success": True,
                    "stats": {
                        "opportunities_count": len(opps),
                        "events_count": len(events),
                        "users_count": len(users)
                    },
                    "opportunities": opps,
                    "events": events
                }, origin=cors_origin)
            except Exception as dbe:
                return json_response(start_response, "200 OK", {
                    "success": True,
                    "stats": {"opportunities_count": 0, "events_count": 0, "users_count": 0},
                    "opportunities": [],
                    "events": [],
                    "warning": str(dbe)
                }, origin=cors_origin)

        # Action: add_opportunity
        if action == "add_opportunity":
            opp = data.get("opportunity", {})
            opp_id = opp.get("id") or f"MANUAL-{int(time.time() * 1000)}"
            title = opp.get("title", "").strip()
            company = opp.get("company", "").strip()
            category = opp.get("category", "Community")
            opp_type = opp.get("type", "Contrat Remote")
            salary = opp.get("salary", "A negocier")
            url = opp.get("url", "").strip()
            eligibility = opp.get("eligibility", "Global / Afrique")
            score = int(opp.get("score", 85))
            notes = opp.get("notes", "").strip()

            if not title or not url or not company:
                return json_response(start_response, "400 Bad Request", {
                    "success": False,
                    "error": "Titre, entreprise et URL requis"
                }, origin=cors_origin)

            add_opportunity(opp_id, title, company, category, opp_type, salary, url, eligibility, score, notes)
            export_public_json()

            return json_response(start_response, "200 OK", {
                "success": True,
                "message": f"Offre '{title}' ajoutee avec succes",
                "id": opp_id
            }, origin=cors_origin)

        # Action: delete_opportunity
        if action == "delete_opportunity":
            opp_id = data.get("id")
            if not opp_id:
                return json_response(start_response, "400 Bad Request", {
                    "success": False,
                    "error": "ID manquant"
                }, origin=cors_origin)

            deleted = delete_opportunity(opp_id)
            export_public_json()

            return json_response(start_response, "200 OK", {
                "success": True,
                "message": f"Offre {opp_id} supprimee",
                "deleted": deleted
            }, origin=cors_origin)

        # Action: add_event
        if action == "add_event":
            evt = data.get("event", {})
            evt_id = evt.get("id") or f"EVT-CUSTOM-{int(time.time() * 1000)}"
            title = evt.get("title", "").strip()
            organizer = evt.get("organizer", "").strip()
            date_str = evt.get("date", "").strip()
            location = evt.get("location", "").strip()
            country = evt.get("country", "Togo").strip()
            evt_type = evt.get("type", "Meetup").strip()
            url = evt.get("url", "").strip()
            desc = evt.get("description", "").strip()
            poster_url = evt.get("poster_url", "").strip()

            if not title or not organizer or not date_str:
                return json_response(start_response, "400 Bad Request", {
                    "success": False,
                    "error": "Titre, organisateur et date requis"
                }, origin=cors_origin)

            add_event(evt_id, title, organizer, date_str, location, country, evt_type, url, desc, poster_url)
            export_public_events_json()

            return json_response(start_response, "200 OK", {
                "success": True,
                "message": f"Evenement '{title}' ajoute avec succes",
                "id": evt_id
            }, origin=cors_origin)

        # Action: delete_event
        if action == "delete_event":
            evt_id = data.get("id")
            if not evt_id:
                return json_response(start_response, "400 Bad Request", {
                    "success": False,
                    "error": "ID manquant"
                }, origin=cors_origin)

            deleted = delete_event(evt_id)
            export_public_events_json()

            return json_response(start_response, "200 OK", {
                "success": True,
                "message": f"Evenement {evt_id} supprime",
                "deleted": deleted
            }, origin=cors_origin)

        # Action: run_cleaner
        if action == "run_cleaner":
            try:
                from cleaner import purge_dead_opportunities
                purged_ids = purge_dead_opportunities()
                return json_response(start_response, "200 OK", {
                    "success": True,
                    "message": f"Nettoyage effectue ({len(purged_ids)} offre(s) purgee(s))",
                    "purged_ids": purged_ids
                }, origin=cors_origin)
            except Exception as ce:
                return json_response(start_response, "500 Internal Server Error", {
                    "success": False,
                    "error": str(ce)
                }, origin=cors_origin)

        return json_response(start_response, "400 Bad Request", {
            "success": False,
            "error": f"Action inconnue: {action}"
        }, origin=cors_origin)

    # 4. Traitement GET
    if method == "GET":
        query_string = (environ.get("QUERY_STRING") or "").lower()
        path_info = (environ.get("PATH_INFO") or "").lower()
        if "action=get_events" in query_string or "type=events" in query_string or "events" in path_info:
            return json_response(start_response, "200 OK", get_all_active_events(), origin=cors_origin)
        if "action=get_jobs" in query_string or "type=jobs" in query_string or "jobs" in path_info:
            return json_response(start_response, "200 OK", get_all_active_opportunities(), origin=cors_origin)

        return json_response(start_response, "200 OK", {
            "status": "online",
            "service": "ANFAANI Admin API",
            "version": "2.1"
        }, origin=cors_origin)

    return json_response(start_response, "405 Method Not Allowed", {
        "error": "Methode non autorisee"
    }, origin=cors_origin)

application = app
handler = app
