@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================
echo   Mise a jour Cost Carte - Maisons Bocuse
echo ============================================
echo.
echo [1/2] Lecture des cartes et generation de la page...
python extract.py
if errorlevel 1 (
  echo.
  echo *** ERREUR pendant la generation. Rien n'a ete publie. ***
  pause
  exit /b 1
)
echo.
echo [2/2] Publication sur GitHub...
git add -A
git commit -m "MAJ hebdo cost carte %date%"
if errorlevel 1 (
  echo   (Aucun changement a publier cette fois.)
) else (
  git push origin main
)
echo.
echo ============================================
echo   Termine !
echo   Page en ligne : https://abrugnoli9.github.io/MAJMenuBocuse/
echo ============================================
echo.
pause
