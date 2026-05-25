@echo off
REM Install script for CPU users (Windows)
REM Creates venv, activates it, installs CPU PyTorch then other requirements.

python -m venv venv
call venv\Scripts\activate
python -m pip install --upgrade pip

REM Install CPU PyTorch wheels from PyPI (plain packages)
pip install torch==2.5.1 torchvision==0.20.1 torchaudio==2.5.1

REM Install remaining dependencies
pip install -r requirements-base.txt

echo CPU install complete. Activate with:
echo   call venv\Scripts\activate
pause
