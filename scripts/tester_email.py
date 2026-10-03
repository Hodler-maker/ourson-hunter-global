#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRIPT DE TEST D'ENVOI D'E-MAIL
Permet de valider immédiatement ta configuration e-mail (Gmail ou Resend).
"""

import os
import sys

# Fix encodage UTF-8 pour Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Assure l'accès au dossier core
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core"))

from notifier import send_email, format_email_html, format_email_text
from database import get_all_active_opportunities

def tester_envoi(destinataire):
    print(f"\n[TEST EMAIL] Préparation de l'envoi de test vers : {destinataire}...")
    
    # Récupérer quelques opportunités réelles de test
    opps = get_all_active_opportunities()
    mock_matches = [{"opportunity": o, "match_score": 90 - idx*5} for idx, o in enumerate(opps[:3])]
    
    subject = "🐻 [TEST] Ton premier e-mail de veille Ourson Hunter !"
    html_content = format_email_html("Tine Antonio", mock_matches)
    text_content = format_email_text("Tine Antonio", mock_matches)
    
    success, info = send_email(destinataire, subject, html_content, text_content)
    
    if success:
        print(f"\n✅ SUCCÈS : {info}")
        print("Vérifie ta boîte de réception (et ton dossier Spams au cas où) !")
    else:
        print(f"\n❌ ÉCHEC : {info}")
        print("Vérifie tes identifiants dans le fichier .env (SMTP_USER et SMTP_PASSWORD).")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = input("Entrez l'adresse e-mail de destination du test : ").strip()
    
    if target:
        tester_envoi(target)
    else:
        print("Aucune adresse e-mail fournie.")
