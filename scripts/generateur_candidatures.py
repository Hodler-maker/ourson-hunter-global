#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GÉNÉRATEUR AUTOMATIQUE DE DOSSIERS DE CANDIDATURE
Pour Tine Antonio Etche (Opportunity Hunter v2)
Génère pour chaque opportunité validée :
1. Un Cold DM (LinkedIn / Twitter / Telegram) < 120 mots
2. Une Cover Letter professionnelle personnalisée en anglais/français
3. Une fiche d'arguments clés pour l'entretien
"""

import os
import sys

PROFILE_TINE = {
    "name": "Tine Antonio Etche",
    "location": "Lomé, Togo",
    "roles": [
        "Vice-Président de la Togo Bitcoin Community",
        "Blockchain Consultant chez Block-Bridge Technology",
        "KOL Bitget & Bybit Ranger"
    ],
    "experience": "5+ ans d'expérience, 10+ projets conseillés, speaker lors de 10 conférences dans 4 pays d'Afrique francophone",
    "skills": "Community building, growth strategy, consulting blockchain, analyse fondamentale, gestion de crise, développement de prototypes assistés par IA",
    "assets": [
        "Jeu éducatif Bitcoin",
        "Générateur de carrousels LinkedIn",
        "Programme de formation blockchain",
        "Lives hebdomadaires d'analyse fondamentale"
    ]
}

def generer_brouillon_markdown(job_title, company, job_url, salary, notes=""):
    slug_company = "".join(c for c in company if c.isalnum() or c in (' ', '_', '-')).strip().lower().replace(' ', '_')
    slug_role = "".join(c for c in job_title if c.isalnum() or c in (' ', '_', '-')).strip().lower().replace(' ', '_')[:30]
    filename = f"candidature_{slug_company}_{slug_role}.md"
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(os.path.dirname(script_dir), "RAPPORTS", "brouillons")
    os.makedirs(output_dir, exist_ok=True)
    target_path = os.path.join(output_dir, filename)

    content = f"""# DOSSIER DE CANDIDATURE — {company.upper()}
**Poste :** {job_title}  
**Entreprise :** {company}  
**Lien officiel :** {job_url}  
**Rémunération :** {salary}  
**Profil candidat :** {PROFILE_TINE['name']} — Lomé, Togo  

---

## 1. COLD DM D'ACCROCHE (LinkedIn / X / Telegram — Moins de 120 mots)
> *À personnaliser et envoyer directement au recruteur ou au Lead de l'écosystème.*

Hi [Recruiter / Lead Name],

I came across the {job_title} opportunity at {company}. As a Blockchain Consultant at Block-Bridge Technology and Vice President of the Togo Bitcoin Community with 5+ years of experience leading Web3 adoption in emerging markets, I have built and scaled engaged trader and builder communities across West Africa.

Having advised 10+ projects and hosted regular fundamental analysis live sessions, I understand how to turn casual community members into educated, long-term ecosystem contributors.

I’d love to connect and explore how my community leadership and regional footprint can accelerate {company}’s growth.

Best regards,  
**{PROFILE_TINE['name']}**  
Blockchain Consultant | VP Togo Bitcoin Community  
Telegram: @[Ton Telegram] | LinkedIn: [Ton Profil]

---

## 2. COVER LETTER COMPLÈTE (Format professionnel anglais)

**{PROFILE_TINE['name']}**  
Lomé, Togo | Email: [Ton Email] | Phone/WhatsApp: [Ton Numéro]  
LinkedIn: [Ton Profil] | X/Twitter: [Ton Handle]  

**To:** The Hiring Team at {company}  
**Subject:** Application for {job_title}  

Dear Hiring Team,

I am writing to express my enthusiastic interest in the {job_title} role at {company}. With over five years of dedicated experience building crypto communities, advising blockchain startups, and driving adoption across French-speaking Africa, I bring a proven track record of strategic growth, education, and community resilience.

As Vice President of the Togo Bitcoin Community and Blockchain Consultant at Block-Bridge Technology, my work has focused on creating high-trust environments where Web3 users learn, trade, and build with confidence:

1. **Grassroots Community & Ecosystem Growth:** Over the past 5 years, I have advised 10+ projects and delivered keynotes at 10 major conferences across four African nations. I specialize in onboarding non-technical audiences as well as power users into active platform champions.
2. **Education & Retention Frameworks:** I host weekly fundamental analysis sessions and develop localized educational tools. I understand how to demystify complex blockchain mechanisms to foster genuine user loyalty and brand advocacy.
3. **Execution & Integrity:** Operating in high-growth emerging markets has instilled in me a deep discipline regarding risk management, user security, and proactive community moderation.

{company} has built an exceptional reputation in the Web3 space. I am eager to contribute my energy, deep regional insights, and community expertise to expand your footprint and strengthen user trust.

Thank you for your consideration. I look forward to discussing how my profile aligns with your strategic objectives.

Sincerely,

**{PROFILE_TINE['name']}**  
Vice President, Togo Bitcoin Community  
Blockchain Consultant, Block-Bridge Technology  

---

## 3. ARGUMENTS CLÉS POUR L'ENTRETIEN

- **Preuve d'impact :** 5+ ans de terrain, VP d'une des communautés Bitcoin les plus actives d'Afrique de l'Ouest.
- **Polyvalence :** Capable de gérer à la fois l'animation quotidienne de milliers de membres, la création de contenu éducatif et les relations partenariats.
- **Fiabilité :** Basé à Lomé avec disponibilité 100% remote et une excellente maîtrise des deux langues de travail (français natif, anglais professionnel).
"""

    with open(target_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"Dossier généré avec succès : {target_path}")
    return target_path

if __name__ == "__main__":
    if len(sys.argv) >= 5:
        generer_brouillon_markdown(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print("Usage: python generateur_candidatures.py <Titre> <Entreprise> <URL> <Salaire>")
