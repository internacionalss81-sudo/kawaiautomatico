@echo off
chcp 65001 >nul
cd /d "%~dp0"

set /p MSG="Mensagem do commit (Enter = 'Atualizacao do app'): "
if "%MSG%"=="" set MSG=Atualizacao do app

echo.
echo Enviando alteracoes para o GitHub...
git add .
git commit -m "%MSG%"
git push

echo.
echo Pronto! O GitHub Actions vai iniciar o build do APK automaticamente.
echo Acompanhe em: https://github.com/SEU_USUARIO/SEU_REPOSITORIO/actions
echo.
pause
