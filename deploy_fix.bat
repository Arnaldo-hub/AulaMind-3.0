@echo off
chcp 65001 >nul
cd /d "C:\Users\Biotecno Chile\Desktop\AulaMind-3.0"

echo ==========================================
echo  AULAMIND - DEPLOY CORRECCION ASIGNATURAS
echo ==========================================
echo.

echo [1/5] Verificando rama actual...
git branch --show-current

echo.
echo [2/5] Cambiando a main...
git checkout main

echo.
echo [3/5] Mergeando consolidation a main...
git merge consolidation --no-edit

echo.
echo [4/5] Subiendo a GitHub...
git push origin main

echo.
echo [5/5] Verificando ultimo commit...
git log --oneline -3

echo.
echo ==========================================
echo  LISTO. Espera 2-3 minutos y recarga
echo  www.aulamind.cl con Ctrl+F5
echo ==========================================
pause