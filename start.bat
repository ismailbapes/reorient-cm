@echo off
echo ============================================
echo    ReOrient CM - Demarrage du serveur
echo ============================================
echo.

cd /d "%~dp0backend"

if not exist "venv" (
    echo Creation de l'environnement virtuel...
    python -m venv venv
)

call venv\Scripts\activate

echo Installation des dependances...
pip install -r requirements.txt -q

if not exist ".env" (
    copy .env.example .env
    echo.
    echo IMPORTANT : Ouvrez le fichier backend\.env
    echo et remplacez sk-ant-votre-cle-ici par votre vraie cle API Anthropic.
    echo Obtenez-la gratuitement sur : console.anthropic.com
    echo.
    pause
)

echo.
echo Demarrage de ReOrient CM...
echo Backend : http://localhost:8000
echo Frontend : ouvrez frontend\index.html dans votre navigateur
echo.
echo Appuyez sur Ctrl+C pour arreter le serveur
echo ============================================
echo.

python main.py
pause
