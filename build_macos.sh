#!/bin/bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOOTSTRAP_PYTHON="${PYTHON:-python3}"
BUILD_PYTHON="$PROJECT_ROOT/.buildvenv/bin/python"

if ! command -v "$BOOTSTRAP_PYTHON" >/dev/null 2>&1; then
    echo "Python 3 was not found. Install Python 3.10+ and rerun this script." >&2
    exit 1
fi

cd "$PROJECT_ROOT"
if [[ ! -x "$BUILD_PYTHON" ]]; then
    "$BOOTSTRAP_PYTHON" -m venv .buildvenv
fi

"$BUILD_PYTHON" -m pip install 'pygame==2.5.2' pyinstaller
"$BUILD_PYTHON" -m PyInstaller --noconfirm --clean --windowed --onedir \
    --name Comando \
    --add-data 'game/backgrounds:backgrounds' \
    --add-data 'game/images:images' \
    --add-data 'game/music:music' \
    --hidden-import AI.LLM.dialoge_generator \
    --distpath 'steam_upload/mac' \
    --workpath 'build/pyinstaller-mac' \
    'game/main.py'

APP_PATH="$PROJECT_ROOT/steam_upload/mac/Comando.app"
APP_EXECUTABLE="$APP_PATH/Contents/MacOS/Comando"
if [[ ! -x "$APP_EXECUTABLE" ]]; then
    echo "Expected app executable was not created: $APP_EXECUTABLE" >&2
    exit 1
fi

SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy "$BUILD_PYTHON" - "$APP_EXECUTABLE" <<'PY'
import os
import subprocess
import sys

environment = os.environ.copy()
environment["SDL_VIDEODRIVER"] = "dummy"
environment["SDL_AUDIODRIVER"] = "dummy"
try:
    subprocess.run([sys.argv[1], "--smoke-test"], env=environment, timeout=30, check=True)
except subprocess.TimeoutExpired:
    print("The packaged Mac game exceeded its 30-second smoke-test limit.", file=sys.stderr)
    raise SystemExit(1)
PY

cat > "$PROJECT_ROOT/steam_upload/mac/README.txt" <<'EOF'
COMANDO macOS build

Launch Comando.app. Press F10 to exit at any time, including during gameplay.
The game also closes from the pause menu.

This directory is the macOS game build for a Steam depot. Create or configure
the Steam app and macOS depot in Steamworks, then upload Comando.app with
SteamPipe. This build is for the Mac architecture of the Python environment
used to create it.
EOF

echo "Build ready and smoke-tested: $APP_PATH"
