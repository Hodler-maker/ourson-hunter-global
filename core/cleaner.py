#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NETTOYEUR D'OFFRES EXPIRÉES & LIENS MORTS — OURSON HUNTER
Vérifie la disponibilité HTTP de chaque offre :
- Supprime immédiatement les 404, 410 et pages d'offres closes (Lever, Ashby, etc.)
- Met à jour la base de données et les exports publics.
"""

import os
import sys
import requests
import shutil

# Fix encodage UTF-8 pour Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import get_connection, export_public_json, get_all_active_opportunities

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

EXPIRED_PHRASES = [
    "couldn't find anything here",
    "job posting you're looking for might have closed",
    "job has been removed",
    "this position has been closed",
    "no longer accepting applications",
    "job is no longer available",
    "this job post has expired",
    "this listing is expired",
    "page not found"
]

from urllib.parse import urlparse

def is_opportunity_alive(url):
    """
    Vérifie si le lien profond de l'opportunité est toujours valide et actif.
    Retourne (True, statut) ou (False, raison).
    """
    if not url or not url.startswith("http"):
        return False, "URL invalide"

    # 1. Rejet strict des pages d'accueil génériques (Lien profond obligatoire selon AGENTS.md)
    parsed = urlparse(url)
    path = parsed.path.strip('/')
    if not path:
        return False, "Page d'accueil générique (Lien profond vers l'annonce obligatoire)"

    try:
        # Requete GET avec timeout de 8 secondes
        res = requests.get(url, headers=HEADERS, timeout=8, allow_redirects=True)
        
        # 2. Statut HTTP mort
        if res.status_code in [404, 410]:
            return False, f"Code HTTP {res.status_code}"

        # 3. Détection de redirection cachée vers une page d'accueil racine
        final_parsed = urlparse(res.url)
        final_path = final_parsed.path.strip('/')
        if not final_path and not any(sub in final_parsed.netloc for sub in ['affiliates.', 'earn.', 'jobs.', 'careers.']):
            return False, f"Redirige vers la racine générique ({res.url})"

        # 4. Détection de page d'expiration dans le contenu HTML
        content_lower = res.text.lower()
        for phrase in EXPIRED_PHRASES:
            if phrase in content_lower:
                return False, f"Offre expirée ({phrase})"

        return True, "En ligne"
    except requests.exceptions.Timeout:
        # Ne supprime pas en cas de simple timeout réseau ponctuel
        return True, "Timeout temporaire"
    except Exception as e:
        return True, f"Erreur réseau temporaire ({e})"

def purge_dead_opportunities():
    """
    Scanne toutes les offres actives et supprime définitivement celles dont le lien est mort ou expiré.
    """
    print("[CLEANER] Début de l'audit de validité des opportunités...")
    opps = get_all_active_opportunities()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    purged_count = 0
    purged_ids = []

    for opp in opps:
        opp_id = opp['id']
        url = opp['url']
        title = opp['title']
        company = opp['company']

        alive, reason = is_opportunity_alive(url)
        if not alive:
            print(f"  [X] EXPIRÉE / MORTE : {opp_id} - {title} ({company}) -> {reason}")
            cursor.execute("DELETE FROM opportunities WHERE id = ?", (opp_id,))
            purged_count += 1
            purged_ids.append(opp_id)

    if purged_count > 0:
        conn.commit()
        print(f"[CLEANER] {purged_count} offre(s) expirée(s) supprimée(s) de la base de données.")
        export_public_json()

        # Synchroniser public/public_jobs.json
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        src = os.path.join(root_dir, "data", "public_jobs.json")
        dst = os.path.join(root_dir, "public", "public_jobs.json")
        if os.path.exists(src):
            shutil.copyfile(src, dst)
            print(f"[CLEANER] Export public synchronisé : {dst}")
    else:
        print("[CLEANER] Toutes les opportunités actuelles sont valides et actives !")

    conn.close()
    return purged_ids

if __name__ == "__main__":
    purge_dead_opportunities()
