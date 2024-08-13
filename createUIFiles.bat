@echo off

rem Convertir archivos .ui a .py
pyuic5 mainUI.ui -o mainUi.py
pyuic5 loginUI.ui -o loginUi.py
echo Conversiones completadas.
pause
