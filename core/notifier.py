#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DISPATCHER DE NOTIFICATIONS — OURSON HUNTER GLOBAL
Envoie les alertes d'offres personnalisées aux utilisateurs :
- Via Email (SMTP Gmail ou Resend API) avec template HTML soigné
- Via Bot Telegram (100% gratuit et instantané)
- Avec fallback console / journal
"""

import os
import sys
import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import requests

# Chargement du fichier .env
try:
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    load_dotenv(env_path)
except Exception:
    pass

# Variables de configuration E-mail
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "ÀNFÀÀNÍ")
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

def format_telegram_digest(user_name, matches):
    """
    Formate un message Telegram clair et direct avec les meilleures opportunités.
    """
    msg = f"*ÀNFÀÀNÍ — Nouvelles Offres pour toi*\n"
    msg += f"Bonjour *{user_name}*, voici les meilleures opportunités détectées ce matin correspondant à ton profil :\n\n"

    for idx, item in enumerate(matches[:3], 1):
        opp = item["opportunity"]
        score = item["match_score"]
        msg += f"*{idx}. {opp['title']}* ({opp['company']})\n"
        msg += f"Pertinence : `{score}%` | {opp['salary']}\n"
        msg += f"Eligibilité : {opp['eligibility']} | Type : {opp['type']}\n"
        msg += f" [Voir l'offre officielle]({opp['url']})\n\n"

    msg += "_ÀNFÀÀNÍ · Open the door to opportunity._"
    return msg

def format_email_html(user_name, matches):
    """
    Génère un template HTML d'e-mail moderne, sombre et responsive.
    """
    items_html = ""
    for idx, item in enumerate(matches[:4], 1):
        opp = item["opportunity"]
        score = item["match_score"]
        items_html += f"""
        <div style="background-color: #1e293b; border: 1px solid #334155; border-radius: 16px; padding: 18px; margin-bottom: 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span style="color: #fbbf24; font-weight: bold; font-size: 13px;">{opp['company']}</span>
                <span style="background-color: rgba(16, 185, 129, 0.2); color: #34d399; padding: 2px 8px; border-radius: 9999px; font-size: 11px; font-weight: bold;">Score {score}/100</span>
            </div>
            <h3 style="color: #ffffff; margin: 0 0 6px 0; font-size: 16px;">{opp['title']}</h3>
            <p style="color: #94a3b8; font-size: 13px; margin: 0 0 12px 0; line-height: 1.4;">{opp.get('notes') or 'Opportunité sélectionnée pour ton profil.'}</p>
            <div style="border-top: 1px solid #334155; padding-top: 10px; display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="color: #fde68a; font-weight: bold; font-size: 13px;">{opp['salary']}</div>
                    <div style="color: #64748b; font-size: 11px;">{opp['type']} · {opp['eligibility']}</div>
                </div>
                <a href="{opp['url']}" target="_blank" style="background: linear-gradient(90deg, #d97706, #f59e0b); color: #ffffff; text-decoration: none; padding: 8px 14px; border-radius: 10px; font-size: 12px; font-weight: bold; display: inline-block;">Postuler -></a>
            </div>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ÀNFÀÀNÍ — Open the door to opportunity</title>
</head>
<body style="margin: 0; padding: 0; background-color: #0b0f19; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #f8fafc;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #0b0f19; padding: 20px 10px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" style="max-width: 600px; background-color: #0f172a; border: 1px solid rgba(245, 158, 11, 0.25); border-radius: 24px; overflow: hidden; padding: 24px;">
          <!-- Header -->
          <tr>
            <td align="center" style="padding-bottom: 20px; border-bottom: 1px solid #1e293b;">
              <h1 style="color: #fbbf24; margin: 0; font-size: 24px; font-weight: 900; letter-spacing: 1px;">ÀNFÀÀNÍ</h1>
              <p style="color: #f59e0b; margin: 2px 0 0 0; font-size: 13px; font-weight: 600;">Open the door to opportunity.</p>
              <p style="color: #94a3b8; margin: 4px 0 0 0; font-size: 12px;">Tech, Web3 & Remote Jobs · Afrique Francophone & Monde</p>
            </td>
          </tr>
          <!-- Salutation -->
          <tr>
            <td style="padding: 20px 0 12px 0;">
              <h2 style="color: #ffffff; font-size: 17px; margin: 0 0 6px 0;">Bonjour {user_name} </h2>
              <p style="color: #cbd5e1; font-size: 13px; margin: 0; line-height: 1.5;">Voici ta sélection quotidienne d'opportunités vérifiées correspondant exactement à ton profil :</p>
            </td>
          </tr>
          <!-- Opportunités -->
          <tr>
            <td>
              {items_html}
            </td>
          </tr>
          <!-- Action Banner -->
          <tr>
            <td style="background-color: rgba(217, 119, 6, 0.1); border: 1px dashed rgba(245, 158, 11, 0.35); border-radius: 14px; padding: 14px; text-align: center; margin-top: 10px;">
              <p style="color: #fde68a; font-size: 12px; margin: 0; font-weight: 600;"> Besoin d'un message d'accroche ou d'une Cover Letter ?</p>
              <p style="color: #94a3b8; font-size: 11px; margin: 4px 0 0 0;">Utilise le générateur IA sur la plateforme ÀNFÀÀNÍ pour postuler en 2 minutes.</p>
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td align="center" style="padding-top: 24px; border-top: 1px solid #1e293b; margin-top: 20px;">
              <p style="color: #64748b; font-size: 11px; margin: 0;">ÀNFÀÀNÍ · Open the door to opportunity · Initié par Tine Antonio Etche (Lomé, Togo)</p>
              <p style="color: #475569; font-size: 10px; margin: 4px 0 0 0;">Tu reçois cet e-mail car tu t'es inscrit sur ÀNFÀÀNÍ.</p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""
    return html

def format_email_text(user_name, matches):
    """
    Version texte brut de l'e-mail pour les clients qui ne supportent pas le HTML.
    """
    text = f"OURSON HUNTER GLOBAL — Nouvelles Opportunités\n"
    text += f"Bonjour {user_name},\n\n"
    text += f"Voici tes opportunités du jour :\n\n"
    for idx, item in enumerate(matches[:4], 1):
        opp = item["opportunity"]
        text += f"{idx}. {opp['title']} — {opp['company']}\n"
        text += f"   Rémunération : {opp['salary']}\n"
        text += f"   Type : {opp['type']} ({opp['eligibility']})\n"
        text += f"   Lien : {opp['url']}\n\n"
    text += "Pour générer ta lettre de motivation personnalisée, connecte-toi sur ÀNFÀÀNÍ.\n"
    return text

def send_email_smtp(recipient_email, subject, html_content, text_content):
    """
    Envoie un e-mail via SMTP (ex: Gmail, Brevo, ou serveur personnalisé).
    """
    if not SMTP_USER or not SMTP_PASSWORD:
        return False, "Configuration SMTP manquante (SMTP_USER ou SMTP_PASSWORD non définis)."

    msg = MIMEMultipart("alternative")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = f"{SMTP_FROM_NAME} <{SMTP_USER}>"
    msg["To"] = recipient_email

    part1 = MIMEText(text_content, "plain", "utf-8")
    part2 = MIMEText(html_content, "html", "utf-8")
    msg.attach(part1)
    msg.attach(part2)

    try:
        if SMTP_PORT == 465:
            server = smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=15)
        else:
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15)
            server.starttls()
        
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, [recipient_email], msg.as_string())
        server.quit()
        return True, "E-mail envoyé avec succès via SMTP."
    except Exception as e:
        return False, f"Erreur SMTP : {str(e)}"

def send_email_resend(recipient_email, subject, html_content):
    """
    Envoie un e-mail via l'API Resend (https://resend.com).
    """
    if not RESEND_API_KEY:
        return False, "Clé RESEND_API_KEY manquante."

    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "from": f"{SMTP_FROM_NAME} <onboarding@resend.dev>",
        "to": [recipient_email],
        "subject": subject,
        "html": html_content
    }
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=15)
        if res.status_code in (200, 201):
            return True, "E-mail envoyé avec succès via Resend."
        else:
            return False, f"Erreur API Resend ({res.status_code}) : {res.text}"
    except Exception as e:
        return False, f"Erreur de connexion Resend : {str(e)}"

def send_email(recipient_email, subject, html_content, text_content):
    """
    Dispatcher e-mail : tente d'abord Resend si disponible, sinon bascule sur SMTP.
    """
    if RESEND_API_KEY:
        success, msg = send_email_resend(recipient_email, subject, html_content)
        if success:
            return True, msg

    if SMTP_USER and SMTP_PASSWORD:
        return send_email_smtp(recipient_email, subject, html_content, text_content)

    return False, "Aucun canal e-mail configuré (SMTP ou Resend)."

def send_telegram_alert(chat_id_or_handle, message):
    """
    Envoie un message via l'API Telegram Bot.
    """
    if not TELEGRAM_BOT_TOKEN:
        return False, "TELEGRAM_BOT_TOKEN non configuré."

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id_or_handle,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        res = requests.post(url, json=payload, timeout=10)
        return res.status_code == 200, "Message Telegram envoyé."
    except Exception as e:
        return False, f"Erreur Telegram : {e}"

def resolve_telegram_chat_id(telegram_input):
    """
    Tente de convertir un @pseudo en chat_id numérique en inspectant les mises à jour du bot.
    Si c'est déjà un ID numérique, le retourne directement.
    """
    if not telegram_input:
        return None
    
    clean = str(telegram_input).strip()
    if clean.isdigit():
        return clean
    
    clean_handle = clean.lstrip("@").lower()
    
    if not TELEGRAM_BOT_TOKEN:
        return None
        
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            for update in reversed(data.get("result", [])):
                msg = update.get("message", {}) or update.get("my_chat_member", {})
                user = msg.get("from", {})
                chat = msg.get("chat", {})
                u_handle = (user.get("username") or "").lower()
                c_id = str(chat.get("id") or user.get("id") or "")
                if u_handle and c_id:
                    # Correspondance exacte ou tolérance pour les inversions courantes
                    if u_handle == clean_handle or u_handle in clean_handle or clean_handle in u_handle:
                        return c_id
    except Exception as e:
        print(f"Erreur résolution chat_id: {e}")
        
    return clean

def send_welcome_telegram(telegram_input, user_name, category="Community", country="Togo"):
    """
    Envoie un message d'accueil et d'activation immédiat sur Telegram.
    """
    chat_id = resolve_telegram_chat_id(telegram_input)
    if not chat_id:
        return False, "Chat ID Telegram introuvable."
        
    msg = (
        f" *BIENVENUE SUR ÀNFÀÀNÍ !*\n"
        f"_Open the door to opportunity._\n\n"
        f"Félicitations *{user_name}* ! \n\n"
        f"Ton profil d'alerte est activé avec succès :\n"
        f"*Pays :* {country}\n"
        f"*Spécialité :* {category}\n"
        f"*Fréquence :* Scan et alertes automatiques chaque matin\n\n"
        f"*TOP Opportunités prêtes pour toi :*\n\n"
        f"1. *Community Lead — Kraken Pro* (Kraken)\n"
        f"83k - 166k $/an | CDI Remote | Score: 92%\n\n"
        f"2. *BD & Community Ambassador* (CertiK)\n"
        f"1 000 $/mois (~5h/sem) | Ambassadeur | Score: 88%\n\n"
        f"3. *Arc Microgrants Proof-of-Learning* (Circle / Arc)\n"
        f"500 USDC | Bourse MVP | Score: 87%\n\n"
        f"_Découvre toutes les opportunités sur la plateforme :_\n"
        f"https://anfaani.vercel.app/"
    )
    return send_telegram_alert(chat_id, msg)

def notify_user_matches(user, matches):
    """
    Déclenche l'envoi de la notification selon les préférences et les canaux de l'utilisateur.
    """
    if not matches:
        return False

    notifications_sent = 0
    user_email = user.get("email")
    user_telegram = user.get("telegram")
    user_name = user.get("name", "Abonné")

    # 1. Envoi par E-mail si configuré
    if user_email and "@" in user_email and not user_email.endswith("example.com"):
        subject = f"{len(matches)} opportunités Web3 & Remote sélectionnées pour toi !"
        html_body = format_email_html(user_name, matches)
        text_body = format_email_text(user_name, matches)
        success, info = send_email(user_email, subject, html_body, text_body)
        if success:
            notifications_sent += 1
            print(f"[E-MAIL OK] Envoyé à {user_email}")
        else:
            print(f"[E-MAIL ÉCHEC] {user_email} -> {info}")
    elif user_email and user_email.endswith("example.com"):
        print(f"[E-MAIL SIMULÉ] ({user_email} est une adresse d'exemple)")

    # 2. Envoi par Telegram si configuré
    if user_telegram and TELEGRAM_BOT_TOKEN:
        tg_msg = format_telegram_digest(user_name, matches)
        success, info = send_telegram_alert(user_telegram, tg_msg)
        if success:
            notifications_sent += 1
            print(f"[TELEGRAM OK] Envoyé à {user_telegram}")

    return notifications_sent > 0

def format_welcome_email(user_name, category, country):
    """
    Template HTML pour l'e-mail de bienvenue lors de l'inscription.
    """
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Bienvenue sur ÀNFÀÀNÍ</title>
</head>
<body style="margin: 0; padding: 0; background-color: #0b0f19; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #f8fafc;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #0b0f19; padding: 20px 10px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" style="max-width: 600px; background-color: #0f172a; border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 24px; overflow: hidden; padding: 26px;">
          <!-- Header -->
          <tr>
            <td align="center" style="padding-bottom: 20px; border-bottom: 1px solid #1e293b;">
              <h1 style="color: #fbbf24; margin: 0; font-size: 26px; font-weight: 900; letter-spacing: 1px;">ÀNFÀÀNÍ</h1>
              <p style="color: #f59e0b; margin: 2px 0 0 0; font-size: 13px; font-weight: 600;">Open the door to opportunity.</p>
              <p style="color: #94a3b8; margin: 4px 0 0 0; font-size: 13px;">Le Radar IA des talents Tech, Web3 & Remote</p>
            </td>
          </tr>
          <!-- Corps -->
          <tr>
            <td style="padding: 24px 0 16px 0;">
              <h2 style="color: #ffffff; font-size: 18px; margin: 0 0 10px 0;">Félicitations {user_name} ! </h2>
              <p style="color: #cbd5e1; font-size: 14px; margin: 0 0 14px 0; line-height: 1.6;">
                Ton profil est désormais enregistré avec succès sur <strong>ÀNFÀÀNÍ</strong>. Notre agent IA analyse le web chaque jour pour dénicher les opportunités les plus rémunératrices et accessibles depuis <strong>{country}</strong>.
              </p>
              
              <!-- Profil récapitulatif -->
              <div style="background-color: #1e293b; border-left: 4px solid #f59e0b; border-radius: 12px; padding: 14px 18px; margin: 18px 0;">
                <div style="color: #94a3b8; font-size: 12px; font-weight: bold; text-transform: uppercase;">Récapitulatif de ton profil d'alerte :</div>
                <div style="color: #ffffff; font-size: 14px; margin-top: 6px; line-height: 1.6;">
                  <strong>Pays :</strong> {country}<br>
                  <strong>Métier cible :</strong> {category}<br>
                  <strong>Fréquence :</strong> Chaque matin à 08h00 UTC
                </div>
              </div>

              <h3 style="color: #fbbf24; font-size: 15px; margin: 20px 0 8px 0;">Ce qui va se passer ensuite :</h3>
              <p style="color: #cbd5e1; font-size: 13px; margin: 0 0 6px 0; line-height: 1.6;">
                1. <strong>Veille active 24/7 :</strong> Notre agent scrute les bourses (grants), bounties en USDC et contrats 100% remote.<br>
                2. <strong>Matching IA sur mesure :</strong> Dès qu'une opportunité correspond à tes compétences, tu reçois une alerte directe avec le lien pour postuler.<br>
                3. <strong>Générateur de Pitch :</strong> Utilise notre plateforme pour générer une lettre de motivation et un message d'accroche personnalisé en 2 clics.
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td align="center" style="padding-top: 24px; border-top: 1px solid #1e293b; margin-top: 20px;">
              <p style="color: #64748b; font-size: 11px; margin: 0;">ÀNFÀÀNÍ · Open the door to opportunity · Fondé par Tine Antonio Etche (Lomé, Togo)</p>
              <p style="color: #475569; font-size: 10px; margin: 4px 0 0 0;">Des questions ? Réponds directement à cet e-mail officiel.</p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""
    return html

def send_welcome_email(recipient_email, user_name, category="Community", country="Togo"):
    """
    Envoie un e-mail de bienvenue officiel dès qu'un utilisateur s'enregistre.
    """
    subject = f" Bienvenue sur ÀNFÀÀNÍ, {user_name} ! Ton profil est activé"
    html_content = format_welcome_email(user_name, category, country)
    text_content = f"Bienvenue sur ÀNFÀÀNÍ, {user_name} !\nTon profil ({category} - {country}) est activé. Tu recevras tes premières alertes d'offres chaque matin à 08h00."
    return send_email(recipient_email, subject, html_content, text_content)

if __name__ == "__main__":
    print("Module Notifier prêt.")
    print(f"SMTP configuré : {'OUI' if SMTP_USER and SMTP_PASSWORD else 'NON'}")
    print(f"Resend configuré : {'OUI' if RESEND_API_KEY else 'NON'}")
    print(f"Telegram configuré : {'OUI' if TELEGRAM_BOT_TOKEN else 'NON'}")
