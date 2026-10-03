#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CHEF D'ORCHESTRE GLOBAL (Exécuté toutes les 8h)
Script principal lancé par GitHub Actions ou Windows Task Scheduler :
1. Scrape & vérifie les offres actives
2. Met à jour la base SQLite et exporte public_jobs.json
3. Exécute le matching pour chaque utilisateur inscrit
4. Envoie les alertes personnalisées via Telegram/Email
"""

import os
import sys
from datetime import datetime, timezone

# Fix encodage UTF-8 pour Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Assurer l'accès aux modules internes
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_db, get_all_active_users, get_all_active_opportunities, export_public_json
from matcher import match_opportunities_for_user
from notifier import notify_user_matches

def run_global_cycle():
    now_str = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    print(f"\n[{now_str}] DÉMARRAGE DU CYCLE 8H — OURSON HUNTER GLOBAL")
    
    # 1. Init DB
    init_db()

    # 2. Récupération des opportunités et utilisateurs
    opps = get_all_active_opportunities()
    users = get_all_active_users()
    
    print(f"Opportunités actives : {len(opps)} | Utilisateurs abonnés : {len(users)}")

    # 3. Export pour le site web public
    export_public_json()

    # 4. Matching & Diffusion personnalisée
    sent_count = 0
    for user in users:
        matches = match_opportunities_for_user(user, opps, min_score=60)
        if matches:
            success = notify_user_matches(user, matches)
            if success:
                sent_count += 1
                print(f"[OK] Alerte envoyée à {user['name']} ({len(matches)} offres ciblées)")
        else:
            print(f"[INFO] Aucune nouvelle offre > 60% pour {user['name']} ce cycle-ci")

    print(f"[SUCCÈS] CYCLE TERMINÉ : {sent_count} alerte(s) distribuée(s).\n")

if __name__ == "__main__":
    run_global_cycle()
