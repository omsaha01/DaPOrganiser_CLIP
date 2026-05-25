@echo off
REM Install script for GPU users (Windows)
REM Creates venv, activates it, installs CUDA PyTorch wheels then other requirements.

python -m venv venv
call venv\Scripts\activate
python -m pip install --upgrade pip

REM Install PyTorch GPU wheels from official index
pip install --index-url https://download.pytorch.org/whl/cu121 --extra-index-url https://pypi.org/simple \
  torch==2.5.1+cu121 torchvision==0.20.1+cu121 torchaudio==2.5.1+cu121

REM Install remaining dependencies
pip install -r requirements-base.txt

echo GPU install complete. Activate with:
echo   call venv\Scripts\activate
pause
