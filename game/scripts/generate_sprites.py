from pathlib import Path

import cv2
import numpy as np

try:
    from rembg import remove
except ModuleNotFoundError:
    remove = None


CHARACTER = "regular_enemy"
MIN_SPRITE_AREA = 500
ALPHA_THRESHOLD = 5
BACKGROUND_TOLERANCE = 38

SCRIPT_DIR = Path(__file__).resolve().parent
GAME_ROOT = SCRIPT_DIR.parent
RAW_DIR = GAME_ROOT / "characters_images_raw"
OUTPUT_ROOT = GAME_ROOT / "images" / CHARACTER

SPRITE_SHEETS = {
    "running": RAW_DIR / "regular_enemy_running.png",
    "attack": RAW_DIR / "regular_enemy_Attack.png",
    "death": RAW_DIR / "regular_enemy_death.png"
}


def _remove_background(image_path, output_path):
    img = cv2.imread(str(image_path), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise FileNotFoundError(image_path)

    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGRA)
    elif len(img.shape) == 3 and img.shape[2] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

    # Detectar fondo blanco con tolerancia, evitando dejar un hilo blanco alrededor del sprite
    lower = np.array([255 - BACKGROUND_TOLERANCE] * 3, dtype=np.uint8)
    upper = np.array([255, 255, 255], dtype=np.uint8)
    mask = cv2.inRange(img[:, :, :3], lower, upper)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # Fondo transparente
    img[:, :, 3] = 255 - mask

    cv2.imwrite(str(output_path), img)

def _trim_transparent_pixels(sprite):
    alpha = sprite[:, :, 3]
    points = cv2.findNonZero((alpha > ALPHA_THRESHOLD).astype(np.uint8))
    if points is None:
        return sprite

    x, y, w, h = cv2.boundingRect(points)
    return sprite[y : y + h, x : x + w]


def _find_sprite_bounds(img):
    alpha = img[:, :, 3]
    mask = (alpha > ALPHA_THRESHOLD).astype(np.uint8)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
        mask,
        connectivity=8,
    )

    sprites = []
    for i in range(1, num_labels):
        x = stats[i, cv2.CC_STAT_LEFT]
        y = stats[i, cv2.CC_STAT_TOP]
        w = stats[i, cv2.CC_STAT_WIDTH]
        h = stats[i, cv2.CC_STAT_HEIGHT]
        area = stats[i, cv2.CC_STAT_AREA]

        if area < MIN_SPRITE_AREA:
            continue

        sprites.append((x, y, w, h))

    return sorted(sprites, key=lambda bounds: (bounds[1], bounds[0]))


def _clear_old_frames(out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    for old_frame in out_dir.glob("frame_*.png"):
        old_frame.unlink()


def generate_sprite_sheet(name, image_path, out_dir):
    if not image_path.exists():
        raise FileNotFoundError(f"Sprite sheet not found: {image_path}")

    out_dir.mkdir(parents=True, exist_ok=True)
    no_bg_path = out_dir / f"{name}_no_bg.png"

    print(f"Removing background: {image_path}")
    _remove_background(image_path, no_bg_path)

    img = cv2.imread(str(no_bg_path), cv2.IMREAD_UNCHANGED)
    if img is None:
        raise FileNotFoundError(no_bg_path)
    if len(img.shape) != 3 or img.shape[2] != 4:
        raise ValueError(f"Expected an RGBA image after background removal: {no_bg_path}")

    sprite_bounds = _find_sprite_bounds(img)
    _clear_old_frames(out_dir)

    print(f"Detected {len(sprite_bounds)} {name} sprites")
    for i, (x, y, w, h) in enumerate(sprite_bounds):
        sprite = _trim_transparent_pixels(img[y : y + h, x : x + w])
        filename = out_dir / f"frame_{i:02d}.png"
        cv2.imwrite(str(filename), sprite)
        print(f"Saved {filename}")

    return sprite_bounds


def generate_sprites(sprite_sheets=None):
    sprite_sheets = sprite_sheets or SPRITE_SHEETS
    generated = {}

    for name, image_path in sprite_sheets.items():
        out_dir = OUTPUT_ROOT / name
        generated[name] = generate_sprite_sheet(name, image_path, out_dir)

    print("Finished.")
    return generated


if __name__ == "__main__":
    generate_sprites()
