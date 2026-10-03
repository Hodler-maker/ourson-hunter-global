@echo off
REM === Lancement hebdomadaire de OPPORTUNITY HUNTER en MODE AUTONOME ===
REM 1) Remplace le chemin ci-dessous par celui de ton dossier AGENT
cd /d "C:\CHEMIN\VERS\AGENT"

REM 2) Crée le dossier des rapports s'il n'existe pas
if not exist "RAPPORTS" mkdir "RAPPORTS"
if not exist "RAPPORTS\brouillons" mkdir "RAPPORTS\brouillons"

REM 3) Lance l'agent une seule fois, puis quitte (mode headless)
agy -p "MODE AUTONOME. Date du jour : %date%. Execute la session hebdomadaire complete decrite dans la section MODE AUTONOME de AGENTS.md." --print-timeout 20m --output-format json > "RAPPORTS\derniere-execution.json" 2>> "RAPPORTS\erreurs.log"
