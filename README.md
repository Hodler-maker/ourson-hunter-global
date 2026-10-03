# 🐻 OURSON HUNTER GLOBAL

> **Plateforme autonome de veille IA & Job Board Web3/Remote pour les talents d'Afrique et du monde entier.**  
> Initié par Tine Antonio Etche (Lomé, Togo).

---

## 🌟 Vue d'ensemble

Ourson Hunter est passé d'un outil local à une **architecture SaaS globale multi-utilisateurs** :
1. **Frontend Public (`web/`)** : Site web responsive, prêt à être hébergé gratuitement sur Vercel, Netlify ou Cloudflare Pages.
2. **Moteur Backend (`core/`)** :
   - `database.py` : Base SQLite/Supabase gérant les abonnés et les opportunités.
   - `matcher.py` : Algorithme IA reliant chaque utilisateur aux meilleures offres selon ses compétences et son pays.
   - `notifier.py` : Distribution automatique des alertes par Telegram ou Email.
   - `scheduler_runner.py` : Exécute le cycle complet de veille et d'envoi.
3. **Automatisation Cloud 24h/24 (`.github/workflows/`)** : Tourne **toutes les 8 heures** dans le cloud via GitHub Actions sans ordinateur allumé.

---

## 🚀 Comment déployer la plateforme en ligne (100% Gratuit)

### Étape 1 : Publier le code sur GitHub
1. Crée un dépôt sur ton compte GitHub (ex: `ourson-hunter-global`).
2. Pousse ce dossier sur GitHub :
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Ourson Hunter Global"
   git remote add origin https://github.com/ton-profil/ourson-hunter-global.git
   git branch -M main
   git push -u origin main
   ```
3. Dès que c'est en ligne, **le workflow GitHub Actions tourne automatiquement toutes les 8h** !

### Étape 2 : Mettre en ligne le Site Web (Vercel ou Cloudflare Pages)
1. Va sur [Vercel.com](https://vercel.com) (gratuit).
2. Clique sur **"Add New Project"** et sélectionne ton dépôt GitHub.
3. Dans **Root Directory**, choisis le dossier `web/`.
4. Clique sur **Deploy**.
👉 Ton site est en ligne en 30 secondes avec une URL sécurisée (ex: `https://ourson-hunter.vercel.app`) !

---

## 🛠️ Commandes Locales Utiles

- **Tester le cycle d'alerte complet :**
  ```bash
  python core/scheduler_runner.py
  ```
- **Tester le matching IA :**
  ```bash
  python core/matcher.py
  ```
- **Mettre à jour le fichier Excel CRM personnel :**
  ```bash
  python scripts/pipeline_crm.py
  ```

---

## 💰 Monétisation & Évolution

- **Option Free** : 3 offres par semaine sur Telegram.
- **Option VIP (3 000 FCFA / 5 USDT par mois)** : Offres en direct + Pitch/Cover Letter généré automatiquement par l'IA.
- **Offres Sponsorisées** : Les protocoles Web3 paient pour mettre leur rôle en vedette.
