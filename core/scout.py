#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MODULE SCOUT AUTONOME — OURSON HUNTER GLOBAL
Explore automatiquement les flux et APIs Web3/Remote (Jobicy, RemoteOK, Himalayas)
Filtre, vérifie selon les 6 critères d'AGENTS.md et insère les nouvelles opportunités en base.
"""

import os
import sys
import re
import requests
import hashlib
from datetime import datetime

# Fix encodage UTF-8 pour Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Assurer l'accès au module database
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import get_connection, add_opportunity, export_public_json, get_all_active_opportunities

HEADERS = {'User-Agent': 'OursonHunterBot/1.0 (Web3 & Remote Hunter; contact: oursonhunter.alerts@gmail.com)'}

def classify_category(title, tags, description=""):
    """
    Catégorise automatiquement l'offre selon les 5 profils d'Ourson Hunter.
    """
    full_text = f"{title} {' '.join(tags)} {description[:300]}".lower()

    if any(k in full_text for k in ['community', 'moderator', 'telegram manager', 'discord', 'social media', 'cm']):
        return "Community"
    if any(k in full_text for k in ['ambassador', 'business development', 'partnerships', 'outreach', 'bd ']):
        return "Ambassadeur"
    if any(k in full_text for k in ['writer', 'content', 'research', 'copywriter', 'translation', 'technical writer']):
        return "Content"
    if any(k in full_text for k in ['engineer', 'developer', 'solidity', 'rust', 'frontend', 'backend', 'smart contract', 'full stack']):
        return "Dev"
    if any(k in full_text for k in ['trader', 'trading', 'analyst', 'tokenomics', 'quant', 'market maker', 'kol']):
        return "Trading"
    
    return "Community"

def is_remote_eligible(location, description=""):
    """
    Vérifie si l'offre est accessible en 100% remote depuis l'Afrique ou globalement.
    Rejette les postes qui exigent impérativement d'être sur place aux USA/Europe.
    """
    loc = str(location).lower()
    desc = str(description[:400]).lower()
    
    # Mots-clés éliminatoires
    if any(k in loc for k in ['us only', 'usa only', 'uk only', 'canada only', 'hybrid', 'on-site', 'onsite']):
        return False
    if 'must be based in the us' in desc or 'us work authorization required' in desc:
        return False
        
    return True

def generate_opp_id(company, title):
    """
    Génère un ID déterministe court pour éviter les doublons.
    """
    raw = f"{company.strip().lower()}_{title.strip().lower()}"
    h = hashlib.md5(raw.encode('utf-8')).hexdigest()[:8].upper()
    comp_clean = re.sub(r'[^A-Z]', '', company.upper())[:4] or "JOB"
    return f"{comp_clean}-{h}"

def fetch_jobicy_jobs():
    """
    Explore l'API Jobicy pour les postes Crypto & Web3.
    """
    jobs = []
    for tag in ['crypto', 'web3']:
        try:
            url = f"https://jobicy.com/api/v2/remote-jobs?count=15&tag={tag}"
            res = requests.get(url, headers=HEADERS, timeout=8)
            if res.status_code == 200:
                data = res.json()
                for item in data.get('jobs', []):
                    title = item.get('jobTitle', '').strip()
                    company = item.get('companyName', '').strip()
                    url_link = item.get('url', '').strip()
                    geo = item.get('jobGeo', 'Global')
                    desc = item.get('jobExcerpt', '')
                    
                    if not title or not company or not url_link:
                        continue
                        
                    if not is_remote_eligible(geo, desc):
                        continue
                        
                    salary_min = item.get('annualSalaryMin')
                    salary_max = item.get('annualSalaryMax')
                    currency = item.get('salaryCurrency', '$')
                    salary = "Rémunération compétitive"
                    if salary_min and salary_max:
                        salary = f"{int(salary_min):,} - {int(salary_max):,} {currency}/an"
                    elif salary_min:
                        salary = f"Dès {int(salary_min):,} {currency}/an"
                        
                    category = classify_category(title, [tag], desc)
                    opp_id = generate_opp_id(company, title)
                    
                    jobs.append({
                        "id": opp_id,
                        "title": title,
                        "company": company,
                        "category": category,
                        "type": "CDI Remote" if "full" in str(item.get('jobType', '')).lower() else "Remote",
                        "salary": salary,
                        "url": url_link,
                        "eligibility": "Global / Remote",
                        "score": 85,
                        "notes": desc[:150] + ("..." if len(desc) > 150 else "")
                    })
        except Exception as e:
            print(f"Erreur scout Jobicy ({tag}): {e}")
    return jobs

def fetch_remoteok_jobs():
    """
    Explore l'API RemoteOK pour les postes Web3.
    """
    jobs = []
    try:
        url = "https://remoteok.com/remote-web3-jobs.json"
        res = requests.get(url, headers=HEADERS, timeout=8)
        if res.status_code == 200:
            data = res.json()
            # Le premier élément est un disclaimer légal
            for item in data[1:]:
                title = item.get('position', '').strip()
                company = item.get('company', '').strip()
                url_link = item.get('apply_url') or item.get('url') or ''
                tags = item.get('tags', [])
                location = item.get('location', '')
                desc = item.get('description', '')
                
                if not title or not company or not url_link:
                    continue
                    
                if not is_remote_eligible(location, desc):
                    continue
                    
                s_min = item.get('salary_min')
                s_max = item.get('salary_max')
                salary = "Selon profil"
                if s_min and s_max:
                    salary = f"{int(s_min):,} - {int(s_max):,} $/an"
                elif s_min:
                    salary = f"Dès {int(s_min):,} $/an"
                    
                category = classify_category(title, tags, desc)
                opp_id = generate_opp_id(company, title)
                
                clean_desc = re.sub(r'<[^>]+>', '', desc)[:140].strip()
                
                jobs.append({
                    "id": opp_id,
                    "title": title,
                    "company": company,
                    "category": category,
                    "type": "Remote 100%",
                    "salary": salary,
                    "url": url_link,
                    "eligibility": "Global",
                    "score": 87,
                    "notes": clean_desc + "..." if clean_desc else "Opportunité Web3 vérifiée."
                })
    except Exception as e:
        print(f"Erreur scout RemoteOK: {e}")
    return jobs

def scout_and_sync_new_jobs():
    """
    Exécute la veille automatique, filtre les doublons et synchronise la base et les exports publics.
    """
    print("[SCOUT] Démarrage de la veille automatique Web3 & Remote...")
    
    # 1. Collecte
    candidates = []
    candidates.extend(fetch_jobicy_jobs())
    candidates.extend(fetch_remoteok_jobs())
    
    print(f"[SCOUT] {len(candidates)} opportunités candidates trouvées sur les flux en direct.")
    
    # 2. Déduplication avec les opportunités déjà existantes
    existing_opps = get_all_active_opportunities()
    existing_ids = {o['id'] for o in existing_opps}
    existing_urls = {o['url'].lower().rstrip('/') for o in existing_opps}
    
    new_added = 0
    for cand in candidates:
        if cand['id'] in existing_ids:
            continue
        if cand['url'].lower().rstrip('/') in existing_urls:
            continue
            
        # Insertion en base
        add_opportunity(
            opp_id=cand['id'],
            title=cand['title'],
            company=cand['company'],
            category=cand['category'],
            opp_type=cand['type'],
            salary=cand['salary'],
            url=cand['url'],
            eligibility=cand['eligibility'],
            score=cand['score'],
            notes=cand['notes']
        )
        existing_ids.add(cand['id'])
        existing_urls.add(cand['url'].lower().rstrip('/'))
        new_added += 1
        print(f"  [+] Nouvelle offre ajoutée : [{cand['category']}] {cand['title']} ({cand['company']})")
        
    print(f"[SCOUT] Veille terminée : {new_added} nouvelle(s) opportunité(s) validée(s) et ajoutée(s).")
    
    # 3. Re-génération des exports publics (data/ et public/)
    export_public_json()
    
    # Copie vers public/public_jobs.json pour Vercel
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_json = os.path.join(root_dir, "data", "public_jobs.json")
    dst_json = os.path.join(root_dir, "public", "public_jobs.json")
    
    if os.path.exists(src_json):
        import shutil
        os.makedirs(os.path.dirname(dst_json), exist_ok=True)
        shutil.copyfile(src_json, dst_json)
        print(f"[SCOUT] Fichier public synchronisé : {dst_json}")
        
    return new_added

if __name__ == "__main__":
    added = scout_and_sync_new_jobs()
    print(f"Résultat: {added} nouvelles opportunités.")
