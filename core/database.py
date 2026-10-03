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

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "ourson_global.db")
PUBLIC_JSON_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "public_jobs.json")

def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
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
        ("KRAKEN-01", "Community Lead - Kraken Pro", "Kraken", "Community", "CDI Remote", "83 000 $ - 166 000 $ / an", "https://jobs.ashbyhq.com/kraken.com/f6100b36-d906-4c8d-93b8-a03399452966", "Global", 92, "Trading & crypto community leader"),
        ("CERTIK-01", "Business Development & Community Ambassador", "CertiK", "Ambassadeur", "Ambassadeur (~5h/sem)", "1 000 $ / mois", "https://cryptojobslist.com/jobs/business-development-intern-certik-san-francisco-bay-area-ca-remote-at-certik", "Global / Afrique", 88, "Sécurité Web3 et audit de smart contracts"),
        ("ARC-01", "Arc Microgrants (Proof-of-Learning Bitcoin)", "Circle / Arc", "Grants", "Bourse MVP", "500 USDC", "https://dorahacks.io/hackathon/arc-microgrants/detail", "Global", 87, "J-11 clôture 14 oct 2026"),
        ("SUPERTEAM-01", "Missions Freelance Content & Research Web3", "Superteam Earn", "Content", "Bounties", "100 $ - 1 500 USDC", "https://earn.superteam.fun", "Global", 89, "Bounties continus sur Solana"),
        ("CLOWN-01", "Web3 Telegram Community Manager", "CLOWN Token", "Community", "Freelance", "15 $ - 30 $ / heure", "https://cryptojobslist.com/jobs/web3-telegram-community-manager-clown-remote-at-clown-token", "Global", 84, "Modération et lives communautaires"),
        ("FIBER-01", "Fiber Community Ambassador", "Fiber Network", "Ambassadeur", "Indépendant", "Incentives / Bounties", "https://cryptojobslist.com/jobs/fiber-community-ambassador-remote-at-fiber", "Global", 81, "Éducation et adoption")
    ]
    for opp in initial_opps:
        add_opportunity(*opp)
    export_public_json()
