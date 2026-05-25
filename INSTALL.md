Installation (Windows)

This project supports both CPU-only and CUDA (GPU) installs. Use the appropriate script below.

CPU install

1. Run `install_cpu.bat` from the project root (double-click or run in PowerShell/CMD):

   install_cpu.bat

This will create a `venv` directory, activate it and install a CPU build of PyTorch and all other dependencies.

GPU (CUDA) install

1. Run `install_gpu.bat` from the project root (double-click or run in PowerShell/CMD):

   install_gpu.bat

This script installs the CUDA wheels from the official PyTorch index then installs the rest of the dependencies.

Notes

- Scripts create a virtual environment in `venv` inside the project folder. Activate it with:

  call venv\Scripts\activate

- If you prefer manual steps, the GPU install command is:

  pip install --index-url https://download.pytorch.org/whl/cu121 --extra-index-url https://pypi.org/simple \
    torch==2.5.1+cu121 torchvision==0.20.1+cu121 torchaudio==2.5.1+cu121

- The scripts install dependencies from `requirements-base.txt` (the project requirements excluding the torch wheel entries).

- After installation, run the app with:

  call venv\Scripts\activate
  python main.py

Problems

- If `pip` fails to find CUDA wheels, ensure your Python version and OS match the wheel availability on PyTorch's index, and that your GPU drivers and CUDA runtime are compatible.
