# 🎯 Detailed Installation Guide - COMANDO

This is a step-by-step guide to install and run COMANDO on your machine.

---

## 📝 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation on Windows](#installation-on-windows)
3. [Installation on macOS](#installation-on-macos)
4. [Installation on Linux](#installation-on-linux)
5. [LLM Model Installation (REQUIRED)](#llm-model-installation-required)
6. [ML Model Training (REQUIRED)](#ml-model-training-required)
7. [Installation Verification](#installation-verification)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Minimum Requirements
- **Python:** 3.10 or higher
- **RAM:** 4GB minimum (8GB recommended)
- **Disk Space:** 500MB
- **GPU:** Optional (but improves performance)

### Required Tools
- **Git** (optional, for cloning)
- **Terminal/CMD** to run commands
- **Code Editor** (VS Code, PyCharm, etc.)
- **⚠️ Qwen 2.5 1.5B LLM Model** (~1.5GB) - MANDATORY!

---

## Installation on Windows

### Step 1: Download Python

1. Visit [python.org](https://www.python.org/downloads/)
2. Download **Python 3.10+** (choose the executable installer)
3. **IMPORTANT:** In the installer, check the box **"Add Python to PATH"**
4. Complete the installation

### Step 2: Verify Python Installation

Open **PowerShell** or **CMD** and run:

```powershell
python --version
pip --version
```

### Step 3: Clone or Download the Project

```powershell
# Option A: Using Git
git clone https://github.com/tu-usuario/Independent-AI-World.git
cd Independent-AI-World

# Option B: Download ZIP from GitHub
# Extract the folder and navigate to it in the terminal
```

### Step 4: Create Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment (choose based on your shell)
# PowerShell:
.\venv\Scripts\Activate.ps1

# CMD:
venv\Scripts\activate.bat
```

**Note:** If you see `(venv)` at the beginning of your terminal, it means it's activated.

### Step 5: Install Dependencies

```powershell
# Update pip (important!)
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Step 6: Download LLM Model (REQUIRED ⚠️)

See [LLM Model Installation (REQUIRED)](#llm-model-installation-required)

### Step 7: Run the Game

Before launching the game for the first time, complete [ML Model Training (REQUIRED)](#ml-model-training-required).

```powershell
cd game
python main.py
```

---

## Installation on macOS

### Step 1: Install Python (Homebrew recommended)

```bash
# Install Homebrew (if you don't have it)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.11
```

### Step 2: Verify Installation

```bash
python3 --version
pip3 --version
```

### Step 3: Clone or Download the Project

```bash
# Option A: Using Git
git clone https://github.com/tu-usuario/Independent-AI-World.git
cd Independent-AI-World

# Option B: Download ZIP
# Extract and navigate to the folder
```

### Step 4: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### Step 5: Install Dependencies

```bash
# Update pip
python3 -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Step 6: Download LLM Model (REQUIRED ⚠️)

See [LLM Model Installation (REQUIRED)](#llm-model-installation-required)

### Step 7: Run the Game

Before launching the game for the first time, complete [ML Model Training (REQUIRED)](#ml-model-training-required).

```bash
cd game
python3 main.py
```

---

## Installation on Linux

### Step 1: Install Python and System Dependencies

```bash
# For Ubuntu/Debian:
sudo apt update
sudo apt install python3.10 python3.10-venv python3-pip
sudo apt install libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev

# For Fedora:
sudo dnf install python3.10 python3-pip
sudo dnf install SDL2-devel SDL2_image-devel SDL2_mixer-devel SDL2_ttf-devel
```

### Step 2: Verify Installation

```bash
python3 --version
pip3 --version
```

### Step 3: Clone or Download the Project

```bash
# Option A: Using Git
git clone https://github.com/tu-usuario/Independent-AI-World.git
cd Independent-AI-World

# Option B: Download ZIP
cd /path/to/Independent-AI-World
```

### Step 4: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### Step 5: Install Dependencies

```bash
# Update pip
python3 -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Step 6: Download LLM Model (REQUIRED ⚠️)

See [LLM Model Installation (REQUIRED)](#llm-model-installation-required)

### Step 7: Run the Game

Before launching the game for the first time, complete [ML Model Training (REQUIRED)](#ml-model-training-required).

```bash
cd game
python3 main.py
```

---

## LLM Model Installation (REQUIRED)

The Qwen 2.5 1.5B model is **MANDATORY** to get AI-generated dialogue (AI characters speaking):

### Option A: Download Pre-trained Qwen Model (Recommended)

```bash
# Create models directory (if it doesn't exist)
mkdir -p game/AI/models

# Download the model (requires ~1.5GB)
# From: https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF
# Download: qwen2.5-1.5b-instruct-q4_0.gguf
# And place it in: game/AI/models/

# Verify the model is in the correct location
ls -la game/AI/models/qwen2.5-1.5b-instruct-q4_0.gguf
```

### Option B: Use Ollama (Alternative)

```bash
# Install Ollama: https://ollama.ai

# Download model
ollama pull qwen2.5:1.5b

# The game will automatically detect Ollama
```

---

## ML Model Training (REQUIRED)

Before the first game run, you **must** train the enemy decision + emotion model by executing:

```bash
# Windows
python game/AI/ML/character_decision_model.py

# macOS/Linux
python3 game/AI/ML/character_decision_model.py
```

This generates:

- `game/AI/models/enemies.pkl`

Without this file, enemy AI decision/emotion inference may fail or fallback behavior may be used.

---

## Installation Verification

### Verify Everything is Correctly Installed

```bash
# Activate virtual environment (if not activated)
source venv/bin/activate  # macOS/Linux
# or
.\venv\Scripts\activate.ps1  # Windows

# Verify each dependency
python -c "import pygame; print('✓ Pygame:', pygame.__version__)"
python -c "import numpy; print('✓ NumPy:', numpy.__version__)"
python -c "import pandas; print('✓ Pandas:', pandas.__version__)"
python -c "import sklearn; print('✓ Scikit-learn:', sklearn.__version__)"
python -c "import joblib; print('✓ Joblib:', joblib.__version__)"
python -c "from PIL import Image; print('✓ Pillow OK')"

# Verify LLM model
ls -la game/AI/models/qwen2.5-1.5b-instruct-q4_0.gguf

# Verify trained enemy ML model
ls -la game/AI/models/enemies.pkl
```

### Game Startup Test

```bash
cd game
python main.py

# You should see:
# 1. A loading screen
# 2. The main menu after 2-3 seconds
# 3. Controls on screen
```

---

## Troubleshooting

### ❌ "Python not found" or "Not recognized as an internal command"

**Solution:**
- Windows: Reinstall Python and make sure to check "Add Python to PATH"
- macOS/Linux: Use `python3` instead of `python`

### ❌ "ModuleNotFoundError: No module named 'pygame'"

**Solution:**
```bash
# Verify virtual environment is activated
# Then reinstall:
pip install --upgrade pygame
```

### ❌ Game runs very slowly

**Solutions:**
1. Reduce resolution in `game/main.py`:
   ```python
   WIDTH, HEIGHT = 1024, 768  # Reduce resolution
   FPS = 60                    # Reduce FPS
   ```
2. Close background applications
3. Check CPU/GPU usage in Activity Monitor

### ❌ "Cannot find model file"

**Solution:**
1. Verify the model is in `game/AI/models/`
2. The game will fail without the model (AI dialogue is mandatory)
3. Download from: https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF

### ❌ "Cannot find enemies.pkl" or enemy AI behavior is not working

**Solution:**
1. Run the mandatory training step:
   ```bash
   python game/AI/ML/character_decision_model.py   # Windows
   python3 game/AI/ML/character_decision_model.py  # macOS/Linux
   ```
2. Verify the file exists at `game/AI/models/enemies.pkl`

### ❌ Audio or music doesn't work

**Solution:**
```bash
# macOS: Install SDL2 audio support
brew install sdl2_mixer

# Linux:
sudo apt install libsdl2-mixer-dev

# Then reinstall pygame
pip install --upgrade pygame
```

### ❌ "Permission denied" (macOS/Linux)

**Solution:**
```bash
# Give execution permissions
chmod +x game/main.py

# Or run with python explicitly
python game/main.py
```

---

## 🆘 Additional Support

If the above steps don't work:

1. **Open an Issue on GitHub** with:
   - Your operating system
   - Python version
   - The exact error message
   - The steps you followed

2. **Contact the author:**
   - Email: gabriel.diaconu@example.com
   - GitHub: [@gabrieldiaconu](https://github.com/gabrieldiaconu)

---

## ✅ Next Steps

Once installed and verified:

1. Open the README.md to understand the gameplay
2. Read the controls guide in the game menu
3. Start playing! 🎮

---

**Congratulations! 🎉 COMANDO is ready to play.**
