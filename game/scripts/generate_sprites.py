from pathlib import Path

import cv2
import numpy as np

try:
    from rembg import remove
except ModuleNotFoundError:
    remove = None


CHARACTER = "main_character"
MIN_SPRITE_AREA = 500
ALPHA_THRESHOLD = 5
BACKGROUND_TOLERANCE = 38

SCRIPT_DIR = Path(__file__).resolve().parent
GAME_ROOT = SCRIPT_DIR.parent
RAW_DIR = GAME_ROOT / "characters_images_raw"
OUTPUT_ROOT = GAME_ROOT / "images" / CHARACTER

SPRITE_SHEETS = {
    "running": RAW_DIR / "Main_running.png",
    "attack": RAW_DIR / "Main_Attack.png",
}


def _remove_background_with_rembg(image_path, output_path):
    with open(image_path, "rb") as image_file:
        output = remove(image_file.read())

    with open(output_path, "wb") as image_file:
        image_file.write(output)


def _remove_background_with_corner_color(image_path, output_path):
    img = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(image_path)

    h, w = img.shape[:2]
    corner_size = max(12, min(w, h) // 20)
    corners = np.concatenate(
        [
            img[:corner_size, :corner_size].reshape(-1, 3),
            img[:corner_size, -corner_size:].reshape(-1, 3),
            img[-corner_size:, :corner_size].reshape(-1, 3),
            img[-corner_size:, -corner_size:].reshape(-1, 3),
        ]
    )
    background_color = np.median(corners, axis=0)
    distance = np.linalg.norm(img.astype(np.float32) - background_color, axis=2)
    background_mask = (distance < BACKGROUND_TOLERANCE).astype(np.uint8) * 255

    kernel = np.ones((3, 3), np.uint8)
    background_mask = cv2.morphologyEx(background_mask, cv2.MORPH_OPEN, kernel)
    foreground_mask = cv2.bitwise_not(background_mask)

    rgba = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
    rgba[:, :, 3] = foreground_mask
    cv2.imwrite(str(output_path), rgba)


def _remove_background(image_path, output_path):
    if remove is not None:
        _remove_background_with_rembg(image_path, output_path)
        return

    print("rembg is not installed; using corner-color background removal fallback.")
    _remove_background_with_corner_color(image_path, output_path)


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
