# 🎮 COMANDO - AI-Powered Combat Game

> An interactive action and combat game powered by AI, where enemies use machine learning to adapt to your fighting style and generate dynamic dialogue using local language models.

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776ab?style=flat-square)
![Pygame](https://img.shields.io/badge/Pygame-2.0%2B-00a86b?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

---

## 🌟 Key Features

### 🤖 **Advanced AI**
- **Dynamic enemy behavior** based on Machine Learning
- **Real-time dialogue generation** using local LLM (Qwen 2.5 1.5B)
- **Adaptive difficulty models** that adjust challenge based on your progress
- **Intelligent decision system** for enemies that learn from your patterns

### 🎯 **Game Mechanics**
- **2D Combat** with multiple enemy types
- **Animated spritesheet system** with fluid animations
- **Procedural level generation** with scalable difficulty
- **Epic boss battles** with special behaviors
- **Interactive dialogue system** with contextual responses

### 🎨 **Visual Experience**
- **High-quality graphics** with real-world scenes (Times Square background)
- **Smooth animations** at 144 FPS
- **Elegant interface** with main menu and completion screen
- **Dynamic visual effects** during combat

### 🔧 **Technical Features**
- **Modular architecture** and scalable design
- **ML-based difficulty system** (Scikit-learn)
- **Local LLM integration** without internet connection
- **Asynchronous dialogue management** for better performance
- **Robust error handling** with elegant fallbacks

---

## 📋 Prerequisites

Before getting started, ensure you have installed:

- **Python 3.10 or higher** ([Download](https://www.python.org/))
- **pip** (Python package manager)
- **Git** (for cloning the repository)
- **4GB RAM minimum** (8GB recommended)
- **2GB disk space** (for ML and LLM models)
- **⚠️ REQUIRED: Qwen 2.5 1.5B LLM Model** (~1.5GB) - See [Installation](#step-4️⃣-download-llm-model-required)

---

## 🚀 Installation and Setup

### Step 1️⃣: Clone or Download the Repository

```bash
# Option A: Using Git
git clone https://github.com/tu-usuario/Independent-AI-World.git
cd Independent-AI-World

# Option B: Download ZIP and extract
# Then navigate to the extracted folder
cd Independent-AI-World
```

### Step 2️⃣: Create a Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3️⃣: Install Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# For development install (with additional tools):
pip install -r requirements-dev.txt
```

**Note:** Installation may take 5-10 minutes depending on your internet connection.

### Step 4️⃣: Download LLM Model (REQUIRED ⚠️)

The Qwen 2.5 1.5B model is **MANDATORY** for full game experience with AI dialogue.

#### Option A: Manual Download (Recommended)

```bash
# Create models directory
mkdir -p game/AI/models

# Download from Hugging Face:
# 1. Visit: https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF
# 2. Download: qwen2.5-1.5b-instruct-q4_0.gguf (quantized version, ~1.5GB)
# 3. Place it in: game/AI/models/

# Verify the model is in the correct location
ls -la game/AI/models/qwen2.5-1.5b-instruct-q4_0.gguf
```

#### Option B: Using Ollama (Alternative)

```bash
# 1. Install Ollama: https://ollama.ai
# 2. Download the model:
ollama pull qwen2.5:1.5b

# The game will automatically detect Ollama
```

### Step 5️⃣: Train Enemy Decision + Emotion ML Model (MANDATORY ⚠️)

Before running the game with adaptive enemy AI, you **must** generate the enemy behavior ML model:

```bash
# From repository root
python game/AI/ML/character_decision_model.py
```

This command trains and saves:

- `game/AI/models/enemies.pkl`

If this step is skipped, the enemy decision/emotion model may be unavailable at runtime.
---

## ▶️ How to Run the Game

### Basic Execution

```bash
cd game
python main.py
```

The game will launch in fullscreen mode at 2048x1200 with 144 FPS.

### Game Controls

| Control | Action |
|---------|--------|
| **A / D** | Move left/right |
| **Shift** | Sprint (fast movement) |
| **Space** | Jump |
| **J or Left Click** | Attack |
| **M** | Open pause menu |
| **Esc** | Exit menu |

### Exit Fullscreen

- **Alt + Tab** (Windows) / **Cmd + Tab** (macOS) / **Alt + Tab** (Linux)
- Or press **Esc** from the pause menu

---

## 📁 Project Structure

```
game/
├── main.py                      # Main entry point
├── AI/                          # Artificial Intelligence system
│   ├── ai_manager.py           # AI Manager
│   ├── LLM/                     # Language models
│   │   └── dialoge_generator.py # Dialogue generator
│   ├── ML/                      # Machine Learning
│   │   ├── character_decision_model.py
│   │   ├── enemy_behavior_model.py
│   │   └── level_difficulty_model.py
│   ├── models/                  # Trained models
│   │   └── qwen2.5-1.5b-instruct-q4_0.gguf (REQUIRED)
│   ├── datasets/                # Training data
│   └── scripts/                 # Data generation scripts
├── characters/                  # Character logic
│   └── character.py
├── levels/                      # Level generation
│   ├── generate_level.py
│   ├── generate_characters.py
│   ├── generate_map.py
│   └── adjust_dificulty.py
├── screens/                     # UI screens
│   ├── game.py                 # Main game screen
│   ├── main_menu.py            # Main menu
│   ├── finish_screen.py        # Completion screen
│   └── dialogue_box.py         # Dialogue system
├── images/                      # Visual assets
│   ├── main_character/          # Main character sprites
│   ├── regular_enemy/           # Regular enemy sprites
│   ├── strong_enemy/            # Strong enemy sprites
│   └── final_boss/              # Boss sprites
├── backgrounds/                 # Game backgrounds
├── music/                       # Music and sound effects
└── scripts/                     # Utility scripts
```

---

## 🎮 Gameplay

### Level Progression

1. **Levels 1-5:** Basic enemies (Street Thug)
2. **Levels 6-10:** Strong enemies (Brutal Executor)
3. **Final Level:** Epic boss with advanced behaviors

### AI System

- Enemies **learn from your fighting style**
- Difficulty **adapts automatically** to your performance
- Dialogue is **dynamically generated** in context
- Each enemy has their own **personality and combat style**

### Progress Metrics

- Character health
- Current level
- Enemies defeated
- Combat statistics

---

## ⚙️ Advanced Configuration

### Environment Variables

```bash
# Enable debug mode
export COMANDO_DEBUG=1

# Set custom port (if applicable)
export GAME_PORT=5000
```

### Performance Adjustments

Edit `game/main.py` to modify:

```python
WIDTH, HEIGHT = 2048, 1200  # Resolution
FPS = 144                    # Frames per second
```

### Custom LLM Model

To use a different model, edit `game/AI/LLM/dialoge_generator.py`:

```python
model_path = "path/to/your/model.gguf"
```

---

## 🔴 Troubleshooting

### Issue: Game doesn't start

```bash
# Verify Python is installed
python3 --version

# Verify pygame is correctly installed
python3 -c "import pygame; print(pygame.__version__)"

# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Issue: Low performance or lag

- **Reduce resolution** in `main.py`
- **Close background applications**
- **Disable unnecessary visual effects**
- Check that your GPU/CPU isn't maxed out

### Issue: AI Dialogue not working

- Ensure the Qwen model is in the correct folder
- Verify RAM availability (minimum 2GB for the model)
- Check console logs for specific errors

### Issue: ML Models fail to load

The game has **automatic fallback** to deterministic values if models fail. If the problem persists:

```bash
# Rebuild the model pickle
cd game/AI/training
python train_level_difficulty_model.py
```

---

## 📚 Main Dependencies

| Library | Version | Purpose |
|---------|---------|---------|
| **pygame** | >=2.0.0 | 2D game engine |
| **numpy** | >=1.21.0 | Numerical computing |
| **pandas** | >=1.3.0 | Data handling |
| **scikit-learn** | >=1.0.0 | Machine Learning |
| **joblib** | >=1.1.0 | Model serialization |
| **Pillow** | >=9.0.0 | Image processing |
| **⚠️ Qwen 2.5 1.5B** | Latest | Local LLM (REQUIRED) |

---

## 🛠️ Development

### Run Tests

```bash
python -m pytest tests/ -v
```

### Linting and Formatting

```bash
# Format code with Black
black game/

# Lint with Flake8
flake8 game/
```

### Generate New Datasets

```bash
cd game/AI/scripts

# Generate enemy data
python generate_enemy_dataset.py

# Generate level data
python generate_level_dataset.py
```

---

## 🤝 Contributions

Contributions are welcome! Please:

1. Fork the repository
2. Create a branch for your feature (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Qwen/Alibaba** for the language model
- **Pygame Community** for excellent documentation
- **Scikit-learn** for ML tools
- All contributors and testers

**Enjoy the game! 🎮✨**

```
╔═════════════════════════════════╗
║   Welcome to COMANDO!           ║
║  Prepare for battle...          ║
╚═════════════════════════════════╝
```
