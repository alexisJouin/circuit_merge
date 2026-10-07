@echo off
cd /d "%~dp0"
echo Installation de Circuit Merge dans un environnement local...
py -3 -m venv .venv
if errorlevel 1 goto failure
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failure
echo Installation terminee. Lancez Lancer_Windows.bat.
pause
exit /b 0
:failure
echo Installation impossible. Consultez README.md pour les commandes manuelles.
pause
exit /b 1
