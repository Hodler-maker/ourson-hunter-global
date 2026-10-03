import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

EXCEL_PATH = r"c:\Users\bitco\OneDrive\Desktop\AGENT\RAPPORTS\OFFRES_EMPLOI.xlsx"

HEADERS = [
    "Date d'ajout",
    "Intitulé du poste",
    "Entreprise / Projet",
    "Type de contrat",
    "Rémunération",
    "Mode de travail",
    "Éligibilité Togo / Afrique",
    "Lien de l'offre",
    "Statut de suivi",
    "Adéquation profil & Compétences"
]

INITIAL_JOBS = [
    {
        "date": "2026-10-03",
        "title": "Community Lead - Kraken Pro",
        "company": "Kraken",
        "type": "Plein temps / CDI",
        "salary": "Non précisé (Compétitif marché)",
        "mode": "100% Remote (Mondial)",
        "togo": "Oui (Remote mondial)",
        "url": "https://cryptojobslist.com",
        "status": "Nouvelle",
        "notes": "Community management trading, animation et support d'utilisateurs avancés. Fort alignement avec expertise crypto et KOL."
    },
    {
        "date": "2026-10-03",
        "title": "Web3 Telegram Community Manager",
        "company": "CLOWN Token / Ecosystem",
        "type": "Freelance / Part-time",
        "salary": "Non précisé (Paiement crypto)",
        "mode": "100% Remote",
        "togo": "Oui (Paiement crypto)",
        "url": "https://cryptojobslist.com",
        "status": "Nouvelle",
        "notes": "Gestion de communauté Telegram, modération, growth et animation d'événements live. Cœur de métier de Tine."
    },
    {
        "date": "2026-10-03",
        "title": "Fiber Community Ambassador",
        "company": "Fiber Network",
        "type": "Contrat indépendant / Ambassadeur",
        "salary": "Incentives / Bounties en tokens",
        "mode": "100% Remote",
        "togo": "Oui (Mondial)",
        "url": "https://cryptojobslist.com",
        "status": "Nouvelle",
        "notes": "Sensibilisation, éducation des utilisateurs locaux, croissance de communauté. Idéal en synergie avec la Togo Bitcoin Community."
    },
    {
        "date": "2026-10-03",
        "title": "Business Development & Community Ambassador",
        "company": "CertiK",
        "type": "Programme Ambassadeur / Remote",
        "salary": "Incentives + Récompenses BD",
        "mode": "100% Remote",
        "togo": "Oui",
        "url": "https://cryptojobslist.com",
        "status": "Nouvelle",
        "notes": "Développement des relations communautaires et sécurité Web3 pour un acteur leader de l'audit blockchain."
    },
    {
        "date": "2026-10-03",
        "title": "Missions Freelance Content & Research Web3",
        "company": "Superteam Earn Sponsors",
        "type": "Freelance / Bounties au livrable",
        "salary": "100 $ à 1 500 $ / mission (USDC)",
        "mode": "100% Remote",
        "togo": "Oui (Wallet Solana)",
        "url": "https://earn.superteam.fun",
        "status": "Nouvelle",
        "notes": "Rédaction d'analyses fondamentales, threads X, croissance d'écosystèmes. Rémunération immédiate en stablecoins."
    },
    {
        "date": "2026-10-03",
        "title": "Regional Ambassador & Community Lead (Africa)",
        "company": "Celo Foundation",
        "type": "Ambassadeur régional",
        "salary": "Grants & Rémunération selon impact",
        "mode": "100% Remote / Local",
        "togo": "Oui (Focus Afrique de l'Ouest)",
        "url": "https://celo.org",
        "status": "Nouvelle",
        "notes": "Promotion de la finance programmable et mobile en Afrique francophone. Valorise l'ancrage local à Lomé."
    }
]

def init_or_update_excel(jobs=INITIAL_JOBS):
    os.makedirs(os.path.dirname(EXCEL_PATH), exist_ok=True)
    
    if os.path.exists(EXCEL_PATH):
        wb = openpyxl.load_workbook(EXCEL_PATH)
        ws = wb.active
    else:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Offres Emploi Web3"
        ws.append(HEADERS)
        
        # Style headers
        header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        thin_border = Border(
            left=Side(style='thin', color='CCCCCC'),
            right=Side(style='thin', color='CCCCCC'),
            top=Side(style='thin', color='CCCCCC'),
            bottom=Side(style='thin', color='CCCCCC')
        )
        
        for col_num in range(1, len(HEADERS) + 1):
            cell = ws.cell(row=1, column=col_num)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_alignment
            cell.border = thin_border
        ws.row_dimensions[1].height = 28

    # Existing URLs
    existing_urls = set()
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row and len(row) >= 8 and row[7]:
            existing_urls.add(row[7])

    # Append jobs without duplicates
    data_font = Font(name="Calibri", size=10)
    data_alignment = Alignment(vertical="center", wrap_text=True)
    thin_border = Border(
        left=Side(style='thin', color='E5E7EB'),
        right=Side(style='thin', color='E5E7EB'),
        top=Side(style='thin', color='E5E7EB'),
        bottom=Side(style='thin', color='E5E7EB')
    )

    added_count = 0
    for job in jobs:
        unique_key = job["title"] + "___" + job["company"]
        # check url or title+company
        if job["url"] not in existing_urls or job["url"] == "https://cryptojobslist.com":
            row_data = [
                job["date"],
                job["title"],
                job["company"],
                job["type"],
                job["salary"],
                job["mode"],
                job["togo"],
                job["url"],
                job["status"],
                job["notes"]
            ]
            ws.append(row_data)
            added_count += 1
            row_idx = ws.max_row
            
            # Format row
            for col_num in range(1, len(row_data) + 1):
                cell = ws.cell(row=row_idx, column=col_num)
                cell.font = data_font
                cell.alignment = data_alignment
                cell.border = thin_border
            ws.row_dimensions[row_idx].height = 22

    # Auto-adjust column widths
    for col in ws.columns:
        col_letter = get_column_letter(col[0].column)
        max_len = max(len(str(cell.value or '')) for cell in col)
        ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 40)

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    wb.save(EXCEL_PATH)
    print(f"Fichier Excel mis à jour avec succès : {EXCEL_PATH} ({added_count} offres ajoutées)")

if __name__ == "__main__":
    init_or_update_excel()
