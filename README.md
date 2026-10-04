# ANFAANI

> **Plateforme autonome de veille IA, Job Board Web3 & Remote et matching de CV pour les talents d'Afrique et du monde.**  
> Slogan officiel : **Open the door to opportunity.**  
> Fondateur : Tine Antonio Etche (Lomé, Togo).  
> Site officiel : [https://anfaani.vercel.app/](https://anfaani.vercel.app/)

---

## Vue d'ensemble

ÀNFÀÀNÍ est une architecture SaaS globale de veille et d'aide à la candidature :
1. **Frontend Public (`index.html`, `evenements.html`, `admin.html`, `contact.html`)** :
   - Interface moderne, sombre, responsive et sans émojis.
   - Module interactif d'analyse de CV (PDF, Texte, Markdown) avec extraction sémantique des compétences et recalcul des scores de compatibilité en temps réel.
   - Générateur de Pitch IA (DM direct, Lettre de motivation, Pitch oral) personnalisé selon le profil et les compétences extraites du candidat.
   - Agenda des événements Web3 majeurs en Afrique francophone (Togo, Côte d'Ivoire, Sénégal, Bénin, Cameroun et en ligne) avec visualisation des affiches en haute définition.
   - Console d'administration sécurisée pour ajouter et modérer les opportunités et événements.

2. **Moteur Backend (`core/`)** :
   - `database.py` : Base SQLite gérant les utilisateurs, les compétences, les opportunités et les événements avec synchronisation JSON multi-dossiers.
   - `matcher.py` : Algorithme IA reliant chaque utilisateur aux meilleures opportunités selon ses compétences, son expérience et son pays.
   - `cleaner.py` : Détection automatique des liens 404/410 et purge des offres fermées.
   - `scout.py` : Veille automatisée sur les flux Web3 & Remote.
   - `notifier.py` : Envoi des alertes personnalisées via Telegram Bot et e-mail (SMTP/Resend).
   - `scheduler_runner.py` : Chef d'orchestre exécutant le cycle complet de veille, d'audit anti-scam et de notification.

3. **Automatisation Cloud 24h/24 (`.github/workflows/hunt_and_notify.yml`)** :
   - Exécution planifiée toutes les 8 heures via GitHub Actions pour rafraîchir les opportunités et distribuer les alertes sans intervention humaine.

---

## Déploiement en Ligne (Vercel)

Le projet est configuré pour un déploiement continu sur Vercel avec support Serverless Python :
- `vercel.json` gère le routage des endpoints `/api/admin` et `/api/register`.
- Les fichiers statiques et assets sont servis automatiquement.

---

## Commandes Locales Utiles

- **Lancer le serveur web local :**
  ```bash
  python scripts/serveur_local.py 8080
  ```

- **Tester le cycle autonome complet (Scout + Cleaner + Matching + Notification) :**
  ```bash
  python core/scheduler_runner.py
  ```

- **Tester le matching IA :**
  ```bash
  python core/matcher.py
  ```

- **Tester l'envoi d'un e-mail d'alerte :**
  ```bash
  python scripts/tester_email.py ton@email.com
  ```

- **Mettre à jour le CRM de conversion :**
  ```bash
  python scripts/pipeline_crm.py
  ```

---

## Éthique & Sécurité

- Aucun frais d'inscription exigé auprès des candidats.
- Ne demande jamais de clé privée, mot de passe ou signature de portefeuille.
- Audit anti-scam rigoureux basé sur les 6 critères d'élimination de la charte de veille.
