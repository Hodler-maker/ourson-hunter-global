# JOURNAL XP — OPPORTUNITY HUNTER
Niveau : Recrue | XP confirmé : 10 | XP en attente : 20

## Opportunités suivies
| Titre | Lien | Date limite annoncée | Statut | Montant | Score /100 | Date de consultation | Leçon |
|---|---|---|---|---|---|---|---|
| Arc Microgrants (Circle / Arc) | https://dorahacks.io/hackathon/arc-microgrants/detail | 14 oct. 2026 | validée | 500 USDC (fait) | 87/100 | 03 oct. 2026 | Exige un déploiement live sur Arc mainnet et du gas en USDC Arc. Décision rolling rapide d'ici le 21 oct. Validée et confirmée (+5 XP confirmé). |
| Colosseum Crypto World's Fair | https://colosseum.org/worldsfair | 12 oct. 2026 | validée | 840 000 $ pool global (détail par projet : non vérifié) | 79/100 | 03 oct. 2026 | Multichain (inclut Bitcoin, Solana et Open Track). Échéance très courte (9 jours). 100% en ligne. Répartition individuelle non vérifiée. Validée et confirmée (+5 XP confirmé). |
| HRF Bitcoin Development Fund | https://hrf.org/program/financial-freedom/bitcoin-development-fund/ | continu (revue trimestrielle) | validée | montant non publié | 91/100 | 03 oct. 2026 | Finance l'éducation et les communautés Bitcoin en Afrique. Candidature directe via formulaire officiel. Montants individuels non publiés (+5 XP en attente). |
| Superteam Earn | https://earn.superteam.fun | continu | validée | 100 $ à 1 500 $ / tâche (fait selon listing) | 89/100 | 03 oct. 2026 | Bounties de contenu, community management et recherche payés en USDC Solana sans restriction géographique (+5 XP en attente). |
| Algorand Foundation Community | https://cryptojobslist.com | continu | validée | Rémunération Web3 compétitive | 86/100 | 08 oct. 2026 | Opportunité vérifiée via flux officiel CryptoJobsList. Rôle communautaire mondial adapté au profil de Tine (+5 XP en attente). |
| DoraHacks Web3 for Social Good 2026 | https://dorahacks.io/hackathon/web3-social-good-2026/detail | 24 oct. 2026 | à confirmer | non vérifié (Pending) | 71/100 | 03 oct. 2026 | Organisé par SMU, GSR Foundation et UMA. L'Idea Track ne requiert aucun code au départ. Présentation finale possible en ligne. Montant des prix non publié. |
| Regional Community Lead Africa (Celo) | https://jobs.lever.co/celo | expirée | expirée | 28k - 48k $/an | 0/100 | 03 oct. 2026 | Offre fermée par le recruteur (404 Lever). Détectée et purgée automatiquement de la base et du site. |
| Campus Ambassador Francophone (TON) | https://ton.org | inéligible | purgée | 500 - 1500 $/mois | 0/100 | 03 oct. 2026 | Aucun formulaire ni offre de poste ouverte sur le site officiel (redirection vers page d'accueil ton.org). Purgée de la base et du site. |
| Selar (Monétisation de produits) | https://selar.co | permanent | à confirmer | non vérifié (estimation) | 64/100 | 03 oct. 2026 | Plateforme de vente de produits numériques multi-devises. Retrait direct Mobile Money créateur au Togo à vérifier directement sur dashboard officiel. |

## Sources fiables
- **DoraHacks** (`https://dorahacks.io`) : plateforme officielle de hackathons et microgrants Web3 (Arc Microgrants, SMU Social Good). Consulté le 03/10/2026.
- **Colosseum** (`https://colosseum.org`) : organisation officielle de hackathons multichain et Solana avec règles claires. Consulté le 03/10/2026.
- **Human Rights Foundation** (`https://hrf.org`) : source officielle pour les subventions Bitcoin mondiales axées sur l'éducation et la liberté financière. Consulté le 03/10/2026.
- **Superteam Earn** (`https://earn.superteam.fun`) : hub officiel de bounties Web3 rémunérés en USDC. Consulté le 03/10/2026.
- **CryptoJobsList** (`https://cryptojobslist.com/rss.xml`) : flux RSS officiel certifié de +100 offres Web3 récentes (Kraken, Binance, Stellar, BitGo, eToro, etc.) avec vérification d'éligibilité remote.
- **Jobicy API** (`https://jobicy.com/api/v2/remote-jobs`) : intégration multi-tags (crypto, defi, solidity, community, marketing, ambassador, trading).

## Sources à éviter
(vide)

## Leçons apprises
1. **Paiements et retraits en Afrique :** Les paiements en crypto (USDC / BTC) restent les plus fluides et immédiatement vérifiables pour Tine depuis Lomé sans dépendre d'intermédiaires bancaires.
2. **Vérification stricte des montants :** Si un montant individuel ou une répartition de dotation n'est pas explicitement publiée par la source primaire (comme pour HRF ou Colosseum), il doit être étiqueté "montant non publié" ou "non vérifié" sans extrapolation.
3. **Idea Track vs Tech Track :** Le hackathon SMU Web3 for Social Good propose une piste "Idée" pure sans code préalable avec mentorat "Vibe Coding" pour les finalistes, ce qui permet de valoriser immédiatement un concept sans passer des semaines à coder.
4. **Purge automatique & Rejet strict des pages d'accueil génériques :** Règle #1 d'AGENTS.md appliquée dans le cleaner. Une opportunité qui redirige vers une racine de domaine (`ton.org`, `arbitrum.foundation`) sans formulaire de candidature ni lien direct vers l'offre est désormais systématiquement rejetée et purgée de la base de données.
5. **Anti-répétition et rotation des e-mails d'alerte :** Pour éviter que les abonnés ne reçoivent indéfiniment les mêmes offres à chaque scan de 8h, l'historique d'envoi est persisté (`notifications`). Le moteur de matching isole les opportunités jamais reçues (`matched_new`) et ne bascule sur les anciennes qu'en cas d'absence totale de nouveautés.
6. **Flux direct CryptoJobsList RSS :** L'intégration du flux XML officiel de CryptoJobsList permet d'ajouter en continu des dizaines d'offres réelles de leaders de l'écosystème crypto (Circle, Binance, BitGo, Kraken, Stellar) tout en éliminant les restrictions géographiques locales (US/UK only).
7. **Persistance des abonnés & Envoi d'alertes par scan :** L'intégration de Supabase PostgreSQL a permis de résoudre le problème des environnements sans état (GitHub Actions et Vercel). Les abonnés sont désormais conservés dans le cloud et interrogés lors de chaque scan automatique de 8h, permettant la distribution effective des e-mails d'opportunités ciblées.

## Hypothèses à tester
- **Hypothèse 1 :** Déployer un contrat minimal d'attestation ou de score pour le jeu éducatif Bitcoin sur Arc mainnet permet de sécuriser un grant de 500 USDC en moins de 10 jours.
- **Hypothèse 2 (spéculation) :** Une proposition conjointe Togo Bitcoin Community + Jeu éducatif auprès du HRF Bitcoin Development Fund pourrait permettre d'obtenir un financement en BTC pour des activités éducatives locales (montants individuels non publiés).
- **Hypothèse 3 :** Tester directement sur le dashboard Selar les options effectives de retrait disponibles pour un compte créateur togolais afin de valider ou invalider formellement la faisabilité de l'encaissement local.
- **Hypothèse 4 :** Candidater de façon ciblée aux rôles d'ambassadeurs et de Community Leads régionaux (Afrique / Francophonie) sur CryptoJobsList permet de décrocher un contrat mensuel récurrent en stablecoins sous 30 jours.
