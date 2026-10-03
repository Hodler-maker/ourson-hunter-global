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
from datetime import datetime

if os.environ.get("VERCEL"):
    DB_PATH = "/tmp/ourson_global.db"
    PUBLIC_JSON_PATH = "/tmp/public_jobs.json"
else:
    DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "ourson_global.db")
    PUBLIC_JSON_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "public_jobs.json")

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

    conn.commit()
    conn.close()
    print("Base de données SQLite initialisée avec succès.")

def add_user(name, email, telegram, country, category, experience_years=2, english_level="Bon", skills=""):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT OR REPLACE INTO users (name, email, telegram, country, category, experience_years, english_level, skills)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, email, telegram, country, category, experience_years, english_level, skills))
        conn.commit()
        user_id = cursor.lastrowid
        return user_id
    finally:
        conn.close()

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

def get_all_active_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE is_active = 1")
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users

def get_all_active_opportunities():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM opportunities WHERE status = 'active' ORDER BY score DESC, created_at DESC")
    opps = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return opps

def export_public_json():
    opps = get_all_active_opportunities()
    with open(PUBLIC_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(opps, f, indent=2, ensure_ascii=False)
    print(f"Export JSON public généré : {PUBLIC_JSON_PATH} ({len(opps)} opportunités)")

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
