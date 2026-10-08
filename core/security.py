#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MODULE DE SECURITE — OURSON HUNTER GLOBAL / ANFAANI
Gestion du Rate-Limiting, de la validation CORS stricte, et de la comparaison securisee.
Aucun emoji dans ce fichier.
"""

import json
import os
import re
import time
import hmac

ALLOWED_ORIGIN_PATTERNS = [
    r"^https://anfaani\.vercel\.app$",
    r"^https://ourson-hunter-global\.vercel\.app$",
    r"^https://anfaani-[a-zA-Z0-9-]+\.vercel\.app$",
    r"^https://ourson-hunter-global-[a-zA-Z0-9-]+\.vercel\.app$",
    r"^http://localhost(:\d+)?$",
    r"^http://127\.0\.0\.1(:\d+)?$",
]

def get_cors_origin(environ):
    """
    Verifie si l'en-tete Origin fait partie des domaines autorises.
    Renvoie la valeur de l'origin valide ou None.
    """
    origin = environ.get("HTTP_ORIGIN", "").strip()
    if not origin:
        return None

    for pattern in ALLOWED_ORIGIN_PATTERNS:
        if re.match(pattern, origin, re.IGNORECASE):
            return origin

    return None

def is_origin_allowed(environ):
    """
    Verifie si la requete est autorisee.
    Si Origin n'est pas fourni (requete interne / meme origine), retourne True.
    Si Origin est fourni mais non autorise, retourne False.
    """
    origin = environ.get("HTTP_ORIGIN", "").strip()
    if not origin:
        return True
    return get_cors_origin(environ) is not None

def get_client_ip(environ):
    """
    Extrait l'adresse IP reelle du client derriere le reverse proxy Vercel.
    """
    xff = environ.get("HTTP_X_FORWARDED_FOR", "")
    if xff:
        # Premier element de la liste X-Forwarded-For (l'IP originale du visiteur)
        return xff.split(",")[0].strip()
    real_ip = environ.get("HTTP_X_REAL_IP", "")
    if real_ip:
        return real_ip.strip()
    return environ.get("REMOTE_ADDR", "127.0.0.1").strip()

# --- RATE LIMITER POUR L'ADMINISTRATION ---
RATE_LIMIT_WINDOW = 900  # 15 minutes en secondes
MAX_FAILED_ATTEMPTS = 5

if os.environ.get("VERCEL"):
    RATE_LIMIT_FILE = "/tmp/admin_rate_limits.json"
else:
    RATE_LIMIT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "admin_rate_limits.json")

_memory_attempts = {}

def _read_rate_limits():
    data = dict(_memory_attempts)
    try:
        if os.path.exists(RATE_LIMIT_FILE):
            with open(RATE_LIMIT_FILE, "r", encoding="utf-8") as f:
                disk = json.load(f)
                if isinstance(disk, dict):
                    for k, v in disk.items():
                        if k not in data or len(v) > len(data.get(k, [])):
                            data[k] = v
    except Exception:
        pass
    return data

def _write_rate_limits(data):
    global _memory_attempts
    _memory_attempts = data
    try:
        os.makedirs(os.path.dirname(RATE_LIMIT_FILE), exist_ok=True)
        with open(RATE_LIMIT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        pass

def check_admin_rate_limit(ip):
    """
    Verifie si l'adresse IP a depasse le quota de tentatives.
    Retourne (is_allowed, retry_after_seconds, count).
    """
    now = time.time()
    data = _read_rate_limits()
    attempts = [t for t in data.get(ip, []) if (now - t) < RATE_LIMIT_WINDOW]

    if len(attempts) >= MAX_FAILED_ATTEMPTS:
        oldest = attempts[0]
        retry_after = int(RATE_LIMIT_WINDOW - (now - oldest))
        if retry_after <= 0:
            retry_after = 60
        return False, retry_after, len(attempts)

    return True, 0, len(attempts)

def record_admin_failed_attempt(ip):
    """
    Enregistre un echec d'authentification pour l'IP et retourne le nombre total d'echecs recents.
    """
    now = time.time()
    data = _read_rate_limits()
    attempts = [t for t in data.get(ip, []) if (now - t) < RATE_LIMIT_WINDOW]
    attempts.append(now)
    data[ip] = attempts
    _write_rate_limits(data)
    return len(attempts)

def reset_admin_rate_limit(ip):
    """
    Reinitialise les tentatives echouees lors d'une authentification reussie.
    """
    data = _read_rate_limits()
    if ip in data:
        del data[ip]
        _write_rate_limits(data)

def verify_admin_password(candidate_key, expected_password=None):
    """
    Comparaison a temps constant (HMAC) pour empecher les attaques temporelles.
    """
    if expected_password is None:
        expected_password = os.environ.get("ADMIN_PASSWORD", "ourson2026")
    candidate = str(candidate_key or "").strip()
    target = str(expected_password).strip()
    return hmac.compare_digest(candidate, target)
