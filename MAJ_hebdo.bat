@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================
echo   Mise a jour Cost Carte - Maisons Bocuse
echo ============================================
echo.
python extract.py
echo.
echo Termine. La page index.html est a jour.
echo (upload GitHub : a configurer plus tard)
echo.
pause
