@echo off
title Psy Quiz - Serveur
echo ======================================
echo   PSY QUIZ - Lancement du serveur
echo ======================================
echo.
echo Activation de l'environnement virtuel...
call .\venv\Scripts\activate.bat

echo.
echo Lancement de l'application...
uvicorn main:app --reload

pause