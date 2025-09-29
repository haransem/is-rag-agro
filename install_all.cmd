@echo off
REM ==============================
REM Setup Python Environment
REM ==============================

cd /d "%~dp0"

echo Removing old venv if exists...
rmdir /s /q .venv 2>nul

echo Creating new virtual environment...
python -m venv .venv

echo Activating venv...
call .venv\Scripts\activate.bat

echo Upgrading pip/setuptools/wheel...
python -m ensurepip --upgrade
python -m pip install --upgrade pip setuptools wheel

REM ==============================
REM Install PyTorch (choose one)
REM ==============================

echo Installing PyTorch (CPU only by default)...
python -m pip install --index-url https://download.pytorch.org/whl/cpu torch torchvision torchaudio

REM If you have NVIDIA GPU with CUDA 11.8, comment the above and uncomment this:
REM python -m pip install --index-url https://download.pytorch.org/whl/cu118 torch torchvision torchaudio

REM ==============================
REM Install Main Dependencies
REM ==============================

echo Installing Python packages...
python -m pip install ^
  transformers datasets sentence-transformers faiss-cpu ^
  tqdm scikit-learn flask jupyter jupyterlab ^
  langchain langchain-core langchain-community langchain-groq langchain-ollama ^
  pythainlp ollama chromadb==0.4.24 ^
  pypdf pdfplumber "camelot-py[cv]" openpyxl ^
  unstructured "unstructured[all-docs]" pdfminer.six python-magic-bin ^
  python-docx python-pptx pandas requests beautifulsoup4 ^
  Pillow pytesseract

REM ==============================
REM Tools for Notebook Collaboration
REM ==============================

python -m pip install nbdime pre-commit nbstripout nbqa ruff black pytest nbmake

echo Configuring nbdime with git...
nbdime config-git --enable

echo If you have .pre-commit-config.yaml in this repo, installing hooks...
pre-commit install

echo ==============================
echo Setup Complete!
echo Activate environment anytime with:
echo     call .venv\Scripts\activate.bat
echo ==============================
pause
