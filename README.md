# ReOrient CM 🎯

**Assistant conversationnel basé sur l'Intelligence Artificielle pour l'orientation professionnelle des diplômés camerounais**

🔗 Application en ligne : [reorient-cm.onrender.com](https://reorient-cm.onrender.com)

---

## Présentation

ReOrient CM est une application web qui aide les diplômés camerounais en situation d'inadéquation formation-emploi à construire un plan de reconversion professionnelle personnalisé, ancré dans les réalités du marché camerounais.

L'application repose sur le modèle Claude Sonnet (Anthropic), enrichi par une base de connaissances localisée injectée dans le prompt système à chaque session — couvrant les secteurs formels et informels, les filières universitaires, les structures d'appui (FNE, PAJER-U, APME, GIZ, Orange Digital Centers) et les dix régions du Cameroun.

### Fonctionnalités

- 💬 Chat conversationnel avec mémoire de session complète
- 🔐 Authentification sécurisée (JWT + hachage SHA-256)
- ☁️ Sauvegarde et persistance des conversations en base de données
- 🌙 Mode sombre
- 🔍 Recherche avec surbrillance dans les conversations
- 📄 Export du plan de reconversion en PDF
- ✉️ Réinitialisation de mot de passe par email

---

## Architecture

Application **three-tier** :

| Couche | Technologie |
|---|---|
| Présentation | HTML5, CSS3, JavaScript vanilla (SPA, sans framework) |
| Logique métier | Python 3.12, FastAPI, Uvicorn (ASGI) |
| Données | PostgreSQL, SQLAlchemy (ORM) |
| IA | Claude Sonnet — Anthropic API |
| Email | Resend API |

Le choix d'un frontend sans framework vise à garantir des temps de chargement rapides sur des connexions à débit limité, contrainte réelle pour une partie des utilisateurs ciblés.

---

## Installation en local

### Prérequis
- Python 3.12+
- Un compte [PostgreSQL](https://www.postgresql.org/) (local ou cloud, ex. Render)
- Une clé API [Anthropic](https://console.anthropic.com)
- Une clé API [Resend](https://resend.com) (pour l'envoi d'emails)

### Étape 1 — Cloner le dépôt
```bash
git clone https://github.com/ismailbapes/reorient-cm.git
cd reorient-cm/backend
```

### Étape 2 — Configurer l'environnement
```bash
python3.12 -m venv venv
source venv/bin/activate      # Windows : venv\Scripts\activate

pip install -r requirements.txt --break-system-packages
```

### Étape 3 — Variables d'environnement
Créez un fichier `.env` à la racine du dossier `backend` :

```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
ANTHROPIC_API_KEY=sk-ant-votre-cle-ici
RESEND_API_KEY=re_votre-cle-ici
SECRET_KEY=votre-cle-secrete-jwt
APP_URL=http://localhost:8000
FROM_EMAIL=onboarding@resend.dev
```

### Étape 4 — Lancer l'application
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

✅ Application accessible sur : http://localhost:8000
✅ Documentation API interactive (Swagger) : http://localhost:8000/docs

---

## Structure du projet

```
reorient-cm/
├── backend/
│   ├── main.py                     # Point d'entrée FastAPI
│   ├── requirements.txt            # Dépendances Python
│   ├── database.py                 # Configuration SQLAlchemy / PostgreSQL
│   ├── models/                     # Modèles ORM (User, Conversation, Message...)
│   ├── routers/
│   │   ├── auth.py                 # Inscription, connexion, JWT
│   │   ├── chat.py                 # Endpoints de conversation
│   │   └── password_reset.py       # Réinitialisation de mot de passe
│   ├── knowledge/                  # Base de connaissances (5 blocs JSON)
│   │   ├── secteurs_formels.json
│   │   ├── secteurs_informels.json
│   │   ├── filieres_universitaires.json
│   │   ├── structures_appui.json
│   │   └── regions_cameroun.json
│   └── static/
│       └── index.html              # Interface web (SPA)
└── README.md
```

---

## Déploiement

L'application est déployée sur **[Render](https://render.com)** :

- **Web Service** : build à partir du dossier `backend`, démarré via `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **PostgreSQL** : base de données managée Render
- **Variables d'environnement** : `DATABASE_URL`, `ANTHROPIC_API_KEY`, `RESEND_API_KEY`, `SECRET_KEY`, `APP_URL`, `FROM_EMAIL`

⚠️ Le plan gratuit Render met le service en veille après 15 minutes d'inactivité ; le redémarrage prend 30 à 60 secondes.

---

## Technique : RAG statique (context stuffing)

ReOrient CM s'inspire du principe RAG (*Retrieval-Augmented Generation*) sans recherche vectorielle dynamique : les cinq blocs de la base de connaissances sont injectés intégralement dans le prompt système à chaque nouvelle session. Cette approche — plus proche du *context stuffing* — a été retenue car le volume de données reste compatible avec la fenêtre de contexte de Claude Sonnet, évitant une infrastructure de recherche vectorielle disproportionnée par rapport aux besoins actuels du projet.

---

## Projet académique

Développé dans le cadre du rapport d'étude technologique pour l'obtention du diplôme d'Ingénieur en Génie Numérique (filière Création et Design Numérique) à l'ESIGN — École Supérieure Internationale de Génie Numérique, Université Inter-États Congo-Cameroun (UIECC), Sangmélima, Cameroun.

**Thème** : *Conception et développement d'un assistant conversationnel basé sur l'Intelligence Artificielle pour l'orientation professionnelle des diplômés camerounais : cas de ReOrient CM*

**Auteur** : NSANG BAPES Cédric Ismail
**Superviseur** : Dr. ONDOBO Luc
**Encadreurs** : Dr. ELOUNDOU Telesphore, Dr. EBALA EBALA Hervé

---

*ReOrient CM — Parce que ton diplôme mérite une seconde chance.*
