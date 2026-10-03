#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MOTEUR DE MATCHING IA — OURSON HUNTER GLOBAL
Associe chaque offre d'emploi ou grant aux profils des utilisateurs inscrits
en fonction de leurs compétences, de leur niveau et de leur pays.
"""

import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def score_match(user, opp):
    """
    Calcule un score de pertinence entre un utilisateur et une opportunité (0-100).
    """
    score = 0
    user_cat = user["category"].lower()
    opp_cat = opp["category"].lower()
    opp_title = opp["title"].lower()
    opp_notes = (opp.get("notes") or "").lower()
    user_skills = (user.get("skills") or "").lower()

    # 1. Correspondance de catégorie (40 pts)
    if user_cat in opp_cat or opp_cat in user_cat:
        score += 40
    elif any(kw in opp_title or kw in opp_notes for kw in user_cat.split()):
        score += 30

    # 2. Compétences clés croisées (30 pts)
    matching_keywords = ["community", "telegram", "ambassador", "content", "grant", "developer", "solidity", "design", "trading"]
    for kw in matching_keywords:
        if kw in user_skills and (kw in opp_title or kw in opp_notes):
            score += 10
            break

    # 3. Niveau d'expérience (15 pts)
    user_exp = user.get("experience_years", 1)
    if user_exp >= 3:
        score += 15
    elif user_exp >= 1:
        score += 10

    # 4. Éligibilité géographique (15 pts)
    FRANCOPHONE_AFRICA = [
        "togo", "bénin", "benin", "côte d'ivoire", "cote d'ivoire", "sénégal", "senegal",
        "cameroun", "cameroon", "burkina faso", "burkina", "mali", "guinée", "guinee",
        "niger", "rdc", "congo", "gabon", "tchad", "madagascar", "rwanda", "burundi",
        "centrafrique", "mauritanie", "comores", "djibouti"
    ]
    opp_elig = opp.get("eligibility", "Global").lower()
    user_country = user.get("country", "").lower()
    
    is_franco = any(c in user_country for c in FRANCOPHONE_AFRICA)
    if "global" in opp_elig or "mondial" in opp_elig or user_country in opp_elig:
        score += 15
    elif is_franco and ("afrique" in opp_elig or "africa" in opp_elig or "west africa" in opp_elig):
        score += 15

    return min(score, 100)

def match_opportunities_for_user(user, opportunities, min_score=60):
    """
    Retourne la liste des opportunités recommandées pour un utilisateur donné,
    triées par pertinence.
    """
    matched = []
    for opp in opportunities:
        match_pts = score_match(user, opp)
        if match_pts >= min_score:
            matched.append({
                "opportunity": opp,
                "match_score": match_pts
            })
    matched.sort(key=lambda x: x["match_score"], reverse=True)
    return matched

if __name__ == "__main__":
    from database import get_all_active_users, get_all_active_opportunities
    users = get_all_active_users()
    opps = get_all_active_opportunities()
    
    print(f"Test de Matching sur {len(users)} utilisateur(s) et {len(opps)} offre(s) :")
    for u in users:
        matches = match_opportunities_for_user(u, opps)
        print(f"\n👤 {u['name']} ({u['country']} - {u['category']}) : {len(matches)} offre(s) pertinente(s)")
        for m in matches[:3]:
            o = m["opportunity"]
            print(f"   ★ Match {m['match_score']}% | {o['title']} ({o['company']}) - {o['salary']}")
