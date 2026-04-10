# ReOrient CM 🎯

**Assistant IA de reconversion professionnelle pour diplômés camerounais**

---

## Présentation

ReOrient CM est une application web bilingue (FR/EN) qui aide les jeunes diplômés camerounais en situation de chômage à construire un plan de reconversion professionnelle personnalisé, ancré dans les réalités du marché camerounais 2026.

### Fonctionnalités
- Chat IA conversationnel (10 questions d'onboarding)
- Plan de reconversion en 3 phases (court / moyen / long terme)
- Base de connaissances : 10 régions, 9 filières, 8 secteurs, 7 structures d'appui
- Export du plan en JSON et PDF
- Interface bilingue FR/EN
- Responsive (desktop + mobile)

---

## Installation rapide

### Prérequis
- Python 3.10+
- VS Code (recommandé)
- Un navigateur web moderne

### Étape 1 — Cloner / Télécharger le projet
Placez le dossier `reorient-cm` dans votre espace de travail.

### Étape 2 — Obtenir une clé API Claude (GRATUIT)
1. Allez sur [console.anthropic.com](https://console.anthropic.com)
2. Créez un compte gratuit
3. Allez dans "API Keys" → "Create Key"
4. Copiez la clé (commence par `sk-ant-...`)

### Étape 3 — Configurer le backend
```bash
# Entrez dans le dossier backend
cd reorient-cm/backend

# Créez l'environnement virtuel
python -m venv venv

# Activez-le
# Sur Windows :
venv\Scripts\activate
# Sur Mac/Linux :
source venv/bin/activate

# Installez les dépendances
pip install -r requirements.txt

# Créez le fichier .env
cp .env.example .env
# Ouvrez .env et remplacez "sk-ant-votre-cle-ici" par votre vraie clé API
```

### Étape 4 — Lancer le backend
```bash
# Depuis le dossier backend, avec le venv activé :
python main.py
```
✅ Le backend est accessible sur : http://localhost:8000
✅ Documentation API interactive : http://localhost:8000/docs

### Étape 5 — Ouvrir le frontend
Ouvrez le fichier `frontend/index.html` directement dans votre navigateur.

> **Important** : Le backend doit être lancé AVANT d'ouvrir le frontend.

---

## Structure du projet

```
reorient-cm/
├── backend/
│   ├── main.py                    # Point d'entrée FastAPI
│   ├── requirements.txt           # Dépendances Python
│   ├── .env.example               # Template variables d'environnement
│   └── app/
│       ├── routers/
│       │   ├── chat.py            # Endpoints conversation
│       │   └── plan.py            # Endpoints plan + export
│       ├── models/
│       │   └── schemas.py         # Modèles de données Pydantic
│       ├── services/
│       │   ├── claude_service.py  # Intégration API Claude
│       │   └── session_manager.py # Gestion des sessions
│       └── knowledge/
│           ├── system_prompt.txt           # Prompt système ReOrient CM
│           ├── bloc1a_secteurs_formels.json
│           ├── bloc1b_secteurs_informels.json
│           ├── bloc2a_filieres.json
│           ├── bloc3_formations_structures.json
│           └── bloc4_regions_contraintes.json
└── frontend/
    └── index.html                 # Interface web complète (single file)
```

---

## Déploiement en ligne

### Backend → Railway (gratuit)
1. Créez un compte sur [railway.app](https://railway.app)
2. "New Project" → "Deploy from GitHub" (uploadez le dossier backend)
3. Ajoutez la variable d'environnement `ANTHROPIC_API_KEY`
4. Railway génère une URL publique automatiquement

### Frontend → Vercel (gratuit)
1. Créez un compte sur [vercel.com](https://vercel.com)
2. Uploadez le dossier `frontend`
3. Dans `index.html`, remplacez `http://localhost:8000` par l'URL Railway
4. Vercel génère une URL publique

---

## Endpoints API

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/api/session/new` | Créer une nouvelle session |
| POST | `/api/chat` | Envoyer un message |
| GET | `/api/session/{id}` | Récupérer les données de session |
| GET | `/api/plan/{id}` | Récupérer le plan généré |
| GET | `/api/plan/{id}/export?format=pdf` | Exporter en PDF |
| GET | `/api/plan/{id}/export?format=json` | Exporter en JSON |
| GET | `/health` | Vérifier l'état du serveur |

---

## Technologies utilisées

- **Backend** : Python 3.10+, FastAPI, Anthropic Claude API
- **Frontend** : HTML5, CSS3, JavaScript vanilla (pas de framework nécessaire)
- **IA** : Claude Sonnet (Anthropic) avec prompt engineering avancé
- **Base de données** : Sessions en mémoire (SQLite possible en extension)
- **Export** : ReportLab (PDF), JSON natif

---

## Projet académique

Développé dans le cadre du projet de fin d'études d'ingénieur en génie numérique à l'ESIGN (École Supérieure Internationale de Génie Numérique), Université Inter-Etats Congo-Cameroun (UIECC), Sangmélima, Cameroun — 2026.

---

*ReOrient CM — Parce que ton diplôme mérite une seconde chance.*
"# reorient-cm" 
