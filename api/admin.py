#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API ADMIN — OURSON HUNTER GLOBAL
Permet à l'administrateur (Tine) de gérer les opportunités et les événements Web3.
Endpoints WSGI Vercel : POST /api/admin
"""

import json
import os
import sys

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

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "ourson2026")

def json_response(start_response, status_str, data):
    payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Access-Control-Allow-Origin", "*"),
        ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
        ("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Admin-Key"),
        ("Content-Length", str(len(payload)))
    ]
    start_response(status_str, headers)
    return [payload]

def app(environ, start_response):
    method = environ.get("REQUEST_METHOD", "GET")

    # Options CORS
    if method == "OPTIONS":
        headers = [
            ("Content-Type", "application/json"),
            ("Access-Control-Allow-Origin", "*"),
            ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
            ("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Admin-Key")
        ]
        start_response("200 OK", headers)
        return [b""]

    # Traitement POST
    if method == "POST":
        try:
            content_length = int(environ.get("CONTENT_LENGTH", 0))
        except (ValueError, TypeError):
            content_length = 0

        request_body = environ["wsgi.input"].read(content_length) if content_length > 0 else b"{}"

        try:
            data = json.loads(request_body.decode("utf-8"))
        except Exception:
            return json_response(start_response, "400 Bad Request", {"success": False, "error": "JSON invalide"})

        # Vérification du mot de passe admin
        key = data.get("admin_key", "")
        if key != ADMIN_PASSWORD:
            return json_response(start_response, "401 Unauthorized", {"success": False, "error": "Mot de passe administrateur incorrect"})

        action = data.get("action", "")

        # 1. Vérification auth / Connexion
        if action == "login":
            return json_response(start_response, "200 OK", {
                "success": True,
                "message": "Authentification réussie"
            })

        # 2. Obtenir les statistiques & listes
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
                })
            except Exception as dbe:
                print(f"Erreur get_dashboard: {dbe}")
                return json_response(start_response, "200 OK", {
                    "success": True,
                    "stats": {"opportunities_count": 0, "events_count": 0, "users_count": 0},
                    "opportunities": [],
                    "events": [],
                    "warning": str(dbe)
                })

        # 3. Ajouter une opportunité
        if action == "add_opportunity":
            opp = data.get("opportunity", {})
            opp_id = opp.get("id") or f"MANUAL-{int(os.times().system * 1000)}"
            title = opp.get("title", "").strip()
            company = opp.get("company", "").strip()
            category = opp.get("category", "Community")
            opp_type = opp.get("type", "Contrat Remote")
            salary = opp.get("salary", "À négocier")
            url = opp.get("url", "").strip()
            eligibility = opp.get("eligibility", "Global / Afrique")
            score = int(opp.get("score", 85))
            notes = opp.get("notes", "").strip()

            if not title or not url or not company:
                return json_response(start_response, "400 Bad Request", {"success": False, "error": "Titre, entreprise et URL requis"})

            add_opportunity(opp_id, title, company, category, opp_type, salary, url, eligibility, score, notes)
            export_public_json()

            return json_response(start_response, "200 OK", {
                "success": True,
                "message": f"Offre '{title}' ajoutée avec succès",
                "id": opp_id
            })

        # 4. Supprimer une opportunité
        if action == "delete_opportunity":
            opp_id = data.get("id")
            if not opp_id:
                return json_response(start_response, "400 Bad Request", {"success": False, "error": "ID manquant"})
            
            deleted = delete_opportunity(opp_id)
            export_public_json()

            return json_response(start_response, "200 OK", {
                "success": True,
                "message": f"Offre {opp_id} supprimée",
                "deleted": deleted
            })

        # 5. Ajouter un événement
        if action == "add_event":
            evt = data.get("event", {})
            evt_id = evt.get("id") or f"EVT-CUSTOM-{int(os.times().system * 1000)}"
            title = evt.get("title", "").strip()
            organizer = evt.get("organizer", "").strip()
            date_str = evt.get("date", "").strip()
            location = evt.get("location", "").strip()
            country = evt.get("country", "Togo").strip()
            evt_type = evt.get("type", "Meetup").strip()
            url = evt.get("url", "").strip()
            desc = evt.get("description", "").strip()

            if not title or not organizer or not date_str:
                return json_response(start_response, "400 Bad Request", {"success": False, "error": "Titre, organisateur et date requis"})

            add_event(evt_id, title, organizer, date_str, location, country, evt_type, url, desc)
            export_public_events_json()

            return json_response(start_response, "200 OK", {
                "success": True,
                "message": f"Événement '{title}' ajouté avec succès",
                "id": evt_id
            })

        # 6. Supprimer un événement
        if action == "delete_event":
            evt_id = data.get("id")
            if not evt_id:
                return json_response(start_response, "400 Bad Request", {"success": False, "error": "ID manquant"})

            deleted = delete_event(evt_id)
            export_public_events_json()

            return json_response(start_response, "200 OK", {
                "success": True,
                "message": f"Événement {evt_id} supprimé",
                "deleted": deleted
            })

        # 7. Déclencher le nettoyeur d'offres mortes / 404
        if action == "run_cleaner":
            try:
                from cleaner import purge_dead_opportunities
                purged_ids = purge_dead_opportunities()
                return json_response(start_response, "200 OK", {
                    "success": True,
                    "message": f"Nettoyage effectué ({len(purged_ids)} offre(s) purgée(s))",
                    "purged_ids": purged_ids
                })
            except Exception as ce:
                return json_response(start_response, "500 Internal Server Error", {"success": False, "error": str(ce)})

        return json_response(start_response, "400 Bad Request", {"success": False, "error": f"Action inconnue: {action}"})

    # GET par défaut -> stats publiques légères
    if method == "GET":
        return json_response(start_response, "200 OK", {
            "status": "online",
            "service": "Ourson Hunter Admin API",
            "version": "2.0"
        })

    return json_response(start_response, "405 Method Not Allowed", {"error": "Méthode non autorisée"})

application = app
handler = app
