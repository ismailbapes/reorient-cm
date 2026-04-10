#!/bin/bash
# Script de démarrage ReOrient CM
# Usage : bash start.sh

echo "============================================"
echo "   ReOrient CM — Démarrage du serveur"
echo "============================================"
echo ""

# Vérifier Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Python non trouvé. Installez Python 3.10+ sur python.org"
    exit 1
fi

PYTHON="python3"
command -v python3 &> /dev/null || PYTHON="python"

echo "✅ Python détecté: $($PYTHON --version)"

# Aller dans le backend
cd "$(dirname "$0")/backend"

# Créer venv si nécessaire
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    $PYTHON -m venv venv
fi

# Activer venv
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

# Installer dépendances
echo "📦 Installation des dépendances..."
pip install -r requirements.txt -q

# Vérifier .env
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT : Ouvrez le fichier backend/.env"
    echo "   et remplacez 'sk-ant-votre-cle-ici' par votre vraie clé API Anthropic."
    echo "   Obtenez-la gratuitement sur : console.anthropic.com"
    echo ""
    read -p "Appuyez sur Entrée une fois le fichier .env configuré..."
fi

# Vérifier la clé API
if grep -q "sk-ant-votre-cle-ici" .env; then
    echo "❌ Clé API non configurée dans backend/.env"
    echo "   Remplacez 'sk-ant-votre-cle-ici' par votre vraie clé Anthropic."
    exit 1
fi

echo ""
echo "🚀 Démarrage de ReOrient CM..."
echo "   Backend : http://localhost:8000"
echo "   API docs : http://localhost:8000/docs"
echo "   Frontend : ouvrez frontend/index.html dans votre navigateur"
echo ""
echo "   Appuyez sur Ctrl+C pour arrêter le serveur"
echo "============================================"
echo ""

$PYTHON main.py
