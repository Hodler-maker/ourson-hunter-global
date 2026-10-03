#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PIPELINE CRM & TRACKING DE CONVERSION POUR OPPORTUNITY HUNTER v2
Gère le cycle de vie complet des candidatures de Tine Antonio Etche :
Détection -> À postuler -> Postulé -> Relance J+5 -> Entretien -> Encaissé / Expiré
"""

import os
import sys
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

EXCEL_PATH = r"c:\Users\bitco\OneDrive\Desktop\AGENT\RAPPORTS\OFFRES_EMPLOI.xlsx"

HEADERS_CRM = [
    "ID",
    "Date Détection",
    "Intitulé du Poste",
    "Entreprise / Projet",
    "Type Contrat",
    "Rémunération Prévue",
    "Lien Direct",
    "Statut CRM",
    "Date Candidature",
    "Canal Utilisé",
    "Date Relance (J+5)",
    "Message Relance Prêt",
    "Revenu Réel ($)",
    "XP Associé",
    "Notes & Prochaines Actions"
]

STATUS_COLORS = {
    "🎯 À postuler": "EDE9FE",       # Violet clair
    "⏳ Postulé": "FEF3C7",         # Jaune ambre
    "💬 Entretien": "DBEAFE",       # Bleu ciel
    "💰 Gagné / Encaissé": "D1FAE5", # Vert menthe
    "❌ Rejeté / Expiré": "F3F4F6"   # Gris clair
}

INITIAL_CRM_DATA = [
    {
        "id": "JOB-01",
        "date_detec": "2026-10-03",
        "title": "Community Lead - Kraken Pro",
        "company": "Kraken",
        "type": "Plein temps / CDI (Remote)",
        "salary": "83 000 $ - 166 000 $ / an",
        "url": "https://jobs.ashbyhq.com/kraken.com/f6100b36-d906-4c8d-93b8-a03399452966",
        "status": "🎯 À postuler",
        "date_applied": "",
        "channel": "Formulaire Ashby + Cold DM LinkedIn",
        "date_followup": "J+5 après envoi",
        "followup_msg": "Hi [Name], following up on my application for Community Lead - Kraken Pro. Still deeply excited about scaling the trader base in emerging markets!",
        "revenue": 0,
        "xp": "+25 XP dès envoi",
        "notes": "Dossier prêt dans RAPPORTS/brouillons/candidature_kraken_community_lead.md. Envoyer le formulaire puis doubler par un DM."
    },
    {
        "id": "JOB-02",
        "date_detec": "2026-10-03",
        "title": "Business Development & Community Ambassador",
        "company": "CertiK",
        "type": "Ambassadeur (~5h/semaine)",
        "salary": "1 000 $ / mois",
        "url": "https://cryptojobslist.com/jobs/business-development-intern-certik-san-francisco-bay-area-ca-remote-at-certik",
        "status": "🎯 À postuler",
        "date_applied": "",
        "channel": "CryptoJobsList + DM Telegram",
        "date_followup": "J+5 après envoi",
        "followup_msg": "Hi [Name], following up on my CertiK Ambassador application. Ready to connect regional Web3 builders with CertiK's security suite!",
        "revenue": 0,
        "xp": "+25 XP dès envoi",
        "notes": "Dossier prêt dans RAPPORTS/brouillons/candidature_certik_ambassador.md. 1 000 $/mois récurrents."
    },
    {
        "id": "JOB-03",
        "date_detec": "2026-10-03",
        "title": "Arc Microgrants (Proof-of-Learning Bitcoin)",
        "company": "Circle / Arc (DoraHacks)",
        "type": "Microgrant (Bourse MVP)",
        "salary": "500 USDC (Garanti aux 20 premiers)",
        "url": "https://dorahacks.io/hackathon/arc-microgrants/detail",
        "status": "🎯 À postuler",
        "date_applied": "",
        "channel": "Formulaire officiel DoraHacks",
        "date_followup": "15 oct. 2026 (Annonces)",
        "followup_msg": "N/A (Revue rolling par le jury DoraHacks)",
        "revenue": 0,
        "xp": "+25 XP dès soumission (+50 XP si gagné)",
        "notes": "URGENT : Clôture le 14 oct. 2026 (J-11). Brouillon 12 questions déjà rédigé dans RAPPORTS/brouillons/arc_microgrants_draft.md."
    },
    {
        "id": "JOB-04",
        "date_detec": "2026-10-03",
        "title": "Web3 Telegram Community Manager",
        "company": "CLOWN Token",
        "type": "Freelance",
        "salary": "15 $ - 30 $ / heure",
        "url": "https://cryptojobslist.com/jobs/web3-telegram-community-manager-clown-remote-at-clown-token",
        "status": "🎯 À postuler",
        "date_applied": "",
        "channel": "CryptoJobsList",
        "date_followup": "J+5 après envoi",
        "followup_msg": "Hello team, following up on my application for the Telegram CM role. Available immediately to structure and grow your community!",
        "revenue": 0,
        "xp": "+25 XP dès envoi",
        "notes": "Modération et animations lives. Parfait pour compléter l'agenda."
    },
    {
        "id": "JOB-05",
        "date_detec": "2026-10-03",
        "title": "Fiber Community Ambassador",
        "company": "Fiber Network",
        "type": "Indépendant / Bounties",
        "salary": "Incentives / Bounties",
        "url": "https://cryptojobslist.com/jobs/fiber-community-ambassador-remote-at-fiber",
        "status": "🎯 À postuler",
        "date_applied": "",
        "channel": "CryptoJobsList / Discord",
        "date_followup": "J+5 après envoi",
        "followup_msg": "Hi Fiber team, excited to represent Fiber in West Africa through localized workshops and education.",
        "revenue": 0,
        "xp": "+25 XP dès envoi",
        "notes": "Sensibilisation et éducation décentralisée."
    },
    {
        "id": "JOB-06",
        "date_detec": "2026-10-03",
        "title": "Bounties Content & Research Web3",
        "company": "Superteam Earn",
        "type": "Freelance à la mission",
        "salary": "100 $ - 1 500 USDC / bounty",
        "url": "https://earn.superteam.fun",
        "status": "🎯 À postuler",
        "date_applied": "",
        "channel": "Plateforme Superteam Earn",
        "date_followup": "À la date de fin de chaque bounty",
        "followup_msg": "N/A (Soumission directe de livrable)",
        "revenue": 0,
        "xp": "+25 XP par soumission",
        "notes": "Paiement direct en USDC Solana sur wallet non-custodial."
    },
    {
        "id": "JOB-07",
        "date_detec": "2026-10-03",
        "title": "Regional Ambassador Africa",
        "company": "Celo Foundation",
        "type": "Ambassadeur",
        "salary": "Non applicable",
        "url": "https://celo.org",
        "status": "❌ Rejeté / Expiré",
        "date_applied": "",
        "channel": "-",
        "date_followup": "-",
        "followup_msg": "-",
        "revenue": 0,
        "xp": "0 XP",
        "notes": "Cohorte d'ambassadeurs clôturée. Noté pour éviter les doublons."
    }
]

def build_crm_excel():
    os.makedirs(os.path.dirname(EXCEL_PATH), exist_ok=True)
    wb = openpyxl.Workbook()
    
    # -------------------------------------------------------------
    # FEUILLE 1 : PIPELINE CRM
    # -------------------------------------------------------------
    ws1 = wb.active
    ws1.title = "Pipeline CRM & Suivi"
    
    # Header styling
    header_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid") # Dark slate
    header_font = Font(name="Segoe UI", size=11, bold=True, color="F8FAFC")
    header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    
    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )

    ws1.append(HEADERS_CRM)
    ws1.row_dimensions[1].height = 30
    for col_idx in range(1, len(HEADERS_CRM) + 1):
        cell = ws1.cell(row=1, column=col_idx)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_align
        cell.border = thin_border

    # Insert rows
    data_font = Font(name="Segoe UI", size=10)
    data_align_left = Alignment(vertical="center", wrap_text=True)
    data_align_center = Alignment(horizontal="center", vertical="center")

    for item in INITIAL_CRM_DATA:
        row_vals = [
            item["id"],
            item["date_detec"],
            item["title"],
            item["company"],
            item["type"],
            item["salary"],
            item["url"],
            item["status"],
            item["date_applied"],
            item["channel"],
            item["date_followup"],
            item["followup_msg"],
            item["revenue"],
            item["xp"],
            item["notes"]
        ]
        ws1.append(row_vals)
        r_idx = ws1.max_row
        ws1.row_dimensions[r_idx].height = 24

        status_color = STATUS_COLORS.get(item["status"], "FFFFFF")
        status_fill = PatternFill(start_color=status_color, end_color=status_color, fill_type="solid")

        for c_idx in range(1, len(row_vals) + 1):
            c = ws1.cell(row=r_idx, column=c_idx)
            c.font = data_font
            c.border = thin_border
            if c_idx in (1, 2, 8, 9, 11, 13, 14):
                c.alignment = data_align_center
            else:
                c.alignment = data_align_left

            # Highlight status cell
            if c_idx == 8:
                c.fill = status_fill
                c.font = Font(name="Segoe UI", size=10, bold=True)

    # -------------------------------------------------------------
    # FEUILLE 2 : TABLEAU DE BORD & KPIS
    # -------------------------------------------------------------
    ws2 = wb.create_sheet(title="📊 Dashboard & KPIs")
    ws2.column_dimensions["A"].width = 5
    ws2.column_dimensions["B"].width = 32
    ws2.column_dimensions["C"].width = 20
    ws2.column_dimensions["D"].width = 40

    # Title block
    ws2.merge_cells("B2:D2")
    title_cell = ws2["B2"]
    title_cell.value = "TABLEAU DE BORD CRM — OPPORTUNITY HUNTER"
    title_cell.font = Font(name="Segoe UI", size=16, bold=True, color="D97706") # Gold
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws2.row_dimensions[2].height = 35

    kpis = [
        ("Opportunités actives sourcées", "=COUNTIF('Pipeline CRM & Suivi'!H2:H50, \"*À postuler*\")", "Offres prêtes à être postulées"),
        ("Candidatures envoyées (En cours)", "=COUNTIF('Pipeline CRM & Suivi'!H2:H50, \"*Postulé*\")", "En attente de retour ou relance J+5"),
        ("Entretiens décrochés", "=COUNTIF('Pipeline CRM & Suivi'!H2:H50, \"*Entretien*\")", "Phase de négociation / entretien"),
        ("Opportunités gagnées / validées", "=COUNTIF('Pipeline CRM & Suivi'!H2:H50, \"*Gagné*\")", "Offres converties en revenu ou bourses"),
        ("Total Revenus Réels Encaissés", "=SUM('Pipeline CRM & Suivi'!M2:M50)", "Somme totale en USD / Stablecoins"),
        ("Taux de passage à l'action", "=IF(COUNTA('Pipeline CRM & Suivi'!C2:C50)>0, COUNTIF('Pipeline CRM & Suivi'!H2:H50, \"*Postulé*\")/COUNTA('Pipeline CRM & Suivi'!C2:C50), 0)", "Ratio candidatures / opportunités")
    ]

    header_kpi_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    ws2["B4"].value = "Indicateur Clé (KPI)"
    ws2["C4"].value = "Valeur"
    ws2["D4"].value = "Description / Objectif"
    for col in ("B4", "C4", "D4"):
        ws2[col].fill = header_kpi_fill
        ws2[col].font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
        ws2[col].alignment = Alignment(horizontal="center", vertical="center")
        ws2[col].border = thin_border
    ws2.row_dimensions[4].height = 25

    row_k = 5
    for label, formula, desc in kpis:
        c_label = ws2.cell(row=row_k, column=2, value=label)
        c_val = ws2.cell(row=row_k, column=3, value=formula)
        c_desc = ws2.cell(row=row_k, column=4, value=desc)

        c_label.font = Font(name="Segoe UI", size=10, bold=True)
        c_val.font = Font(name="Segoe UI", size=11, bold=True, color="2563EB")
        c_desc.font = Font(name="Segoe UI", size=9, italic=True, color="64748B")

        c_label.border = thin_border
        c_val.border = thin_border
        c_desc.border = thin_border

        c_val.alignment = Alignment(horizontal="center", vertical="center")
        ws2.row_dimensions[row_k].height = 24
        row_k += 1

    # Auto-adjust column widths for Sheet 1
    for col in ws1.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = max(len(str(cell.value or '')) for cell in col)
        ws1.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 45)

    ws1.freeze_panes = "C2"
    ws1.auto_filter.ref = ws1.dimensions

    wb.save(EXCEL_PATH)
    print(f"CRM Excel généré avec succès : {EXCEL_PATH}")

def update_status(job_id_or_company, new_status, applied_date=None, channel=None, revenue=None):
    if not os.path.exists(EXCEL_PATH):
        print("Erreur: Excel inexistant, build d'abord.")
        return False
    
    wb = openpyxl.load_workbook(EXCEL_PATH)
    ws = wb["Pipeline CRM & Suivi"]
    found = False

    for r in range(2, ws.max_row + 1):
        jid = str(ws.cell(r, 1).value or '')
        comp = str(ws.cell(r, 4).value or '')
        title = str(ws.cell(r, 3).value or '')

        if job_id_or_company.lower() in jid.lower() or job_id_or_company.lower() in comp.lower() or job_id_or_company.lower() in title.lower():
            found = True
            # Update status
            ws.cell(r, 8).value = new_status
            if applied_date:
                ws.cell(r, 9).value = applied_date
            if channel:
                ws.cell(r, 10).value = channel
            if revenue is not None:
                ws.cell(r, 13).value = float(revenue)

            # Apply style
            status_color = STATUS_COLORS.get(new_status, "FFFFFF")
            ws.cell(r, 8).fill = PatternFill(start_color=status_color, end_color=status_color, fill_type="solid")
            print(f"Ligne mise à jour : {comp} - {title} -> {new_status}")
            break

    if found:
        wb.save(EXCEL_PATH)
        return True
    else:
        print(f"Aucune opportunité trouvée pour '{job_id_or_company}'")
        return False

if __name__ == "__main__":
    if len(sys.argv) == 1:
        build_crm_excel()
    elif sys.argv[1] == "update" and len(sys.argv) >= 4:
        update_status(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
    elif sys.argv[1] == "rebuild":
        build_crm_excel()
    else:
        print("Usage:")
        print("  python pipeline_crm.py              (Génère ou met à jour le CRM)")
        print("  python pipeline_crm.py update <ID/Entreprise> <Statut> [Date] [Canal]")
