@echo off
REM ==============================
REM Create Project Structure
REM ==============================

cd /d "%~dp0"

echo Creating project folder structure...

mkdir notebooks
mkdir src
mkdir src\mypkg
mkdir tests
mkdir data

REM สร้างไฟล์ __init__.py ให้ Python รู้ว่าเป็นแพ็กเกจ
echo. > src\mypkg\__init__.py

REM gitignore เบื้องต้น
echo # Byte-compiled / cache >> .gitignore
echo __pycache__/ >> .gitignore
echo *.pyc >> .gitignore
echo >> .gitignore
echo # Jupyter checkpoints >> .gitignore
echo .ipynb_checkpoints/ >> .gitignore
echo >> .gitignore
echo # Data >> .gitignore
echo data/ >> .gitignore
echo >> .gitignore
echo # Virtual environment >> .gitignore
echo .venv/ >> .gitignore

REM ไฟล์ requirements.txt ว่าง
echo # Add pip packages here >> requirements.txt

echo Project structure created successfully!
pause
