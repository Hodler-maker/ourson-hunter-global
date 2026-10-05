#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BASE DE DONNÉES CENTRALE — OURSON HUNTER GLOBAL
Gère les profils des utilisateurs du monde entier et les opportunités scannées.
Utilise SQLite (sans configuration, portable, réplicable sur Supabase).
"""

import sqlite3
import os
import json
import urllib.request
from datetime import datetime

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

def supabase_request(endpoint, method="GET", data=None):
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    url = f"{SUPABASE_URL}/rest/v1/{endpoint.lstrip('/')}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    if method == "POST":
        headers["Prefer"] = "resolution=merge-duplicates,return=representation"
    
    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode("utf-8")
            if content:
                return json.loads(content)
            return True
    except Exception as e:
        print(f"[SUPABASE WARN] {method} {endpoint} : {e}")
        return None

if os.environ.get("VERCEL"):
    DB_PATH = "/tmp/ourson_global.db"
    PUBLIC_JSON_PATH = "/tmp/public_jobs.json"
    PUBLIC_EVENTS_PATH = "/tmp/public_events.json"
else:
    DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "ourson_global.db")
    PUBLIC_JSON_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "public_jobs.json")
    PUBLIC_EVENTS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "public_events.json")

def get_connection():
    try:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
    except OSError:
        # Fallback pour tout environnement à système de fichiers en lecture seule
        fallback_path = "/tmp/ourson_global.db"
        conn = sqlite3.connect(fallback_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Table des utilisateurs enregistrés
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE,
        telegram TEXT,
        country TEXT DEFAULT 'Togo',
        category TEXT NOT NULL,
        experience_years INTEGER DEFAULT 1,
        english_level TEXT DEFAULT 'Bon',
        skills TEXT,
        notify_telegram BOOLEAN DEFAULT 1,
        notify_email BOOLEAN DEFAULT 1,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Table des opportunités scannées
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS opportunities (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        company TEXT NOT NULL,
        category TEXT NOT NULL,
        type TEXT NOT NULL,
        salary TEXT,
        url TEXT NOT NULL,
        eligibility TEXT DEFAULT 'Global',
        score INTEGER DEFAULT 80,
        notes TEXT,
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Table d'historique des notifications
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        opportunity_id TEXT,
        channel TEXT,
        sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (opportunity_id) REFERENCES opportunities (id)
    )
    """)

    # Table des événements Web3 Afrique
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        organizer TEXT NOT NULL,
        date TEXT NOT NULL,
        location TEXT NOT NULL,
        country TEXT DEFAULT 'Togo',
        type TEXT DEFAULT 'Meetup',
        url TEXT NOT NULL,
        description TEXT,
        poster_url TEXT DEFAULT '',
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()
    print("Base de données SQLite initialisée avec succès.")

def add_user(name, email, telegram, country, category, experience_years=2, english_level="Bon", skills=""):
    user_id = None
    # 1. Sauvegarde SQLite locale / fallback
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT OR REPLACE INTO users (name, email, telegram, country, category, experience_years, english_level, skills)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, email, telegram, country, category, experience_years, english_level, skills))
        conn.commit()
        user_id = cursor.lastrowid
    finally:
        conn.close()

    # 2. Synchronisation automatique Supabase (Cloud persistant)
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            payload = {
                "name": name,
                "email": email,
                "telegram": telegram,
                "country": country,
                "category": category,
                "experience_years": experience_years,
                "english_level": english_level,
                "skills": skills,
                "notify_telegram": True,
                "notify_email": True,
                "is_active": True
            }
            res = supabase_request("users", method="POST", data=payload)
            if res:
                print(f"[SUPABASE OK] Utilisateur synchronisé dans le cloud : {email}")
        except Exception as se:
            print(f"[SUPABASE WARN] Impossible de synchroniser l'utilisateur : {se}")

    return user_id

def add_opportunity(opp_id, title, company, category, opp_type, salary, url, eligibility, score, notes=""):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT OR REPLACE INTO opportunities (id, title, company, category, type, salary, url, eligibility, score, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (opp_id, title, company, category, opp_type, salary, url, eligibility, score, notes))
        conn.commit()
    finally:
        conn.close()

def delete_opportunity(opp_id):
    ensure_tables()
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE opportunities SET status = 'deleted' WHERE id = ?", (opp_id,))
        conn.commit()
        return True
    finally:
        conn.close()

def add_event(event_id, title, organizer, event_date, location, country="Togo", event_type="Meetup", url="", description="", poster_url=""):
    ensure_tables()
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT OR REPLACE INTO events (id, title, organizer, date, location, country, type, url, description, poster_url, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
        """, (event_id, title, organizer, event_date, location, country, event_type, url, description, poster_url))
        conn.commit()
    finally:
        conn.close()

def delete_event(event_id):
    ensure_tables()
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE events SET status = 'deleted' WHERE id = ?", (event_id,))
        conn.commit()
        return True
    finally:
        conn.close()

def get_all_active_events():
    ensure_tables()
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events WHERE status = 'active' ORDER BY created_at DESC")
        events = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return events
    except Exception as e:
        print(f"Erreur SQL events: {e}")
        return []

def export_public_events_json():
    events = get_all_active_events()
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_paths = [
        PUBLIC_EVENTS_PATH,
        os.path.join(root_dir, "data", "public_events.json"),
        os.path.join(root_dir, "public", "public_events.json"),
        os.path.join(root_dir, "web", "public_events.json"),
        os.path.join(root_dir, "public_events.json")
    ]
    for p in set(target_paths):
        try:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                json.dump(events, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
    print(f"Export JSON événements synchronisé : {len(events)} événement(s)")

def ensure_tables():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='opportunities'")
        if not cursor.fetchone():
            init_db()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='events'")
        if not cursor.fetchone():
            init_db()
        else:
            # Migration automatique si la colonne poster_url manque
            cursor.execute("PRAGMA table_info(events)")
            cols = [row[1] for row in cursor.fetchall()]
            if "poster_url" not in cols:
                try:
                    cursor.execute("ALTER TABLE events ADD COLUMN poster_url TEXT DEFAULT ''")
                    conn.commit()
                except Exception:
                    pass

        # Vérifier opportunités (totalite existante)
        cursor.execute("SELECT count(*) FROM opportunities")
        opp_count = cursor.fetchone()[0]
        if opp_count == 0:
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            for jpath in [
                os.path.join(root_dir, "data", "public_jobs.json"),
                os.path.join(root_dir, "public", "public_jobs.json")
            ]:
                if os.path.exists(jpath):
                    try:
                        with open(jpath, "r", encoding="utf-8") as f:
                            jobs = json.load(f)
                        c2 = conn.cursor()
                        for j in jobs:
                            c2.execute("""
                            INSERT OR IGNORE INTO opportunities (id, title, company, category, type, salary, url, eligibility, score, notes, status)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
                            """, (j.get("id"), j.get("title"), j.get("company"), j.get("category"), j.get("type"), j.get("salary"), j.get("url"), j.get("eligibility", "Global"), j.get("score", 85), j.get("desc", "")))
                        conn.commit()
                        break
                    except Exception as e:
                        print(f"Erreur import jobs: {e}")

        # Événements : gérés uniquement par l'administrateur
        pass
    except Exception as e:
        print(f"Erreur ensure_tables: {e}")
    finally:
        conn.close()

def get_all_active_users():
    # 1. Priorité Supabase Cloud (Données persistantes mondiales)
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            remote_users = supabase_request("users?is_active=eq.true&select=*")
            if remote_users is not None and isinstance(remote_users, list):
                return remote_users
        except Exception as se:
            print(f"[SUPABASE WARN] Récupération utilisateurs échouée, bascule SQLite : {se}")

    # 2. Fallback SQLite local
    ensure_tables()
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE is_active = 1")
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return users
    except Exception as e:
        print(f"Erreur SQL users: {e}")
        return []

def get_all_active_opportunities():
    ensure_tables()
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM opportunities WHERE status = 'active' ORDER BY score DESC, created_at DESC")
        opps = [dict(row) for row in cursor.fetchall()]
        conn.close()
        if opps:
            return opps
    except Exception as e:
        print(f"Erreur SQL opportunities: {e}")

    # Fallback fichiers JSON
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for p in [PUBLIC_JSON_PATH, os.path.join(root_dir, "data", "public_jobs.json"), os.path.join(root_dir, "public", "public_jobs.json")]:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
    return []

def export_public_json():
    opps = get_all_active_opportunities()
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_paths = [
        PUBLIC_JSON_PATH,
        os.path.join(root_dir, "data", "public_jobs.json"),
        os.path.join(root_dir, "public", "public_jobs.json"),
        os.path.join(root_dir, "web", "public_jobs.json"),
        os.path.join(root_dir, "public_jobs.json")
    ]
    for p in set(target_paths):
        try:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                json.dump(opps, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
    print(f"Export JSON opportunités synchronisé : {len(opps)} opportunité(s)")

def seed_default_events_if_empty(existing_conn=None):
    # Les événements sont gérés exclusivement depuis la console admin
    pass


if __name__ == "__main__":
    init_db()
    # Ajout du profil fondateur de Tine par défaut
    add_user(
        name="Tine Antonio Etche",
        email="tine@example.com",
        telegram="@tine_etche",
        country="Togo",
        category="Community",
        experience_years=5,
        english_level="Courant",
        skills="Blockchain consulting, community building, trading, lives d'analyse, KOL"
    )
    # Insertion des opportunités vérifiées actuelles
    initial_opps = [
        ("KRAKEN-01", "Community Lead — Kraken Pro", "Kraken", "Community", "CDI Remote", "83k - 166k $/an", "https://jobs.ashbyhq.com/kraken.com/f6100b36-d906-4c8d-93b8-a03399452966", "Global / Afrique", 92, "Advocacy et scaling de communauté trading"),
        ("CELO-01", "Regional Community Lead Africa", "Celo Foundation", "Community", "Contrat Remote", "28k - 48k $/an", "https://jobs.lever.co/celo", "Afrique francophone & globale", 90, "Hubs locaux et onboarding francophone"),
        ("CLOWN-01", "Web3 Telegram Community Manager", "CLOWN Token", "Community", "Freelance", "15 - 30 $/heure", "https://cryptojobslist.com/jobs/web3-telegram-community-manager-clown-remote-at-clown-token", "Global", 84, "Modération et lives communautaires"),
        ("ARBITRUM-01", "Discord & Governance Moderator", "Arbitrum Ecosystem", "Community", "Freelance Remote", "1 200 - 2 000 $/mois", "https://arbitrum.foundation", "Global", 86, "Support L2 et surveillance anti-scam"),
        ("CERTIK-01", "BD & Community Ambassador", "CertiK", "Ambassadeur", "Ambassadeur (~5h/sem)", "1 000 $/mois", "https://cryptojobslist.com/jobs/business-development-intern-certik-san-francisco-bay-area-ca-remote-at-certik", "Global / Afrique", 88, "Sécurité Web3 et audits smart contracts"),
        ("TON-01", "Campus & Regional Ambassador Francophone", "TON Foundation", "Ambassadeur", "Ambassadeur", "500 - 1 500 $/mois", "https://ton.org", "Afrique francophone", 89, "Meetups Mini-Apps Telegram"),
        ("BYBIT-01", "Bybit Ranger & Campus KOL Partner", "Bybit", "Ambassadeur", "Partenaire", "Commissions + Prime 800 $/mois", "https://www.bybit.com", "Afrique / Global", 87, "Représentation locale et événements"),
        ("FIBER-01", "Fiber Community Ambassador", "Fiber Network", "Ambassadeur", "Indépendant", "Incentives Tokens", "https://cryptojobslist.com/jobs/fiber-community-ambassador-remote-at-fiber", "Global", 81, "Éducation et micro-transactions"),
        ("SUPERTEAM-01", "Missions Content & Research Web3", "Superteam Earn", "Content", "Bounties", "100 - 1 500 USDC", "https://earn.superteam.fun", "Global", 89, "Bounties Solana en rédaction et recherche"),
        ("BANKLESS-01", "Crypto Newsletter Analyst & Writer", "Bankless DAO", "Content", "Freelance", "50 - 120 $/article", "https://bankless.community", "Global", 85, "Articles de synthèse DeFi"),
        ("ETHEREUM-01", "Technical Writer & Translator Francophone", "Ethereum.org", "Content", "Grants & Bounties", "500 - 2 000 USDC", "https://ethereum.org/contributing/translation-program/", "Global / Afrique", 88, "Traduction documentation Ethereum"),
        ("ARC-01", "Arc Microgrants (Proof-of-Learning)", "Circle / Arc (DoraHacks)", "Dev", "Bourse MVP", "500 USDC garanti", "https://dorahacks.io/hackathon/arc-microgrants/detail", "Global", 87, "Bourse MVP déployé sur Arc mainnet"),
        ("SOLANA-01", "Solana Superteam MVP Grants", "Solana Foundation", "Dev", "Subvention MVP", "1 000 - 10 000 USDC", "https://earn.superteam.fun/grants/", "Global / Afrique", 91, "Financement sans dilution pour prototypes"),
        ("CODE4RENA-01", "Smart Contract Auditor Apprentice", "Code4rena / Sherlock", "Dev", "Bug Bounty", "500 - 5 000 USDC", "https://code4rena.com", "Global", 86, "Recherche de vulnérabilités Solidity"),
        ("COINMARKETCAP-01", "Analyste Fondamental & Contenu Crypto", "CoinMarketCap Community", "Trading", "Freelance", "300 - 900 $/mois", "https://coinmarketcap.com/community", "Global", 84, "Analyses graphiques et fondamentales"),
        ("BITGET-01", "Bitget Global KOL Partner", "Bitget", "Trading", "Partenariat KOL", "Jusqu'à 60% RevShare + 1 200 $ bonus", "https://www.bitget.com", "Afrique / Global", 88, "Lives de trading et partage de stratégies")
    ]
    for opp in initial_opps:
        add_opportunity(*opp)
    export_public_json()
