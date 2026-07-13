from pathlib import Path

import cv2
import numpy as np
from rembg import remove

# ---------------- CONFIG ----------------

character = "main_character"

script_dir = Path(__file__).resolve().parent
game_root = script_dir.parent

image_path = game_root / "characters_images_raw" / "Main_running.png"
output_path = game_root / "Main_running_no_bg.png"

out_dir = game_root / "images" / character
out_dir.mkdir(parents=True, exist_ok=True)

print(f"Using image: {image_path}")

# ---------------- REMOVE BACKGROUND ----------------

with open(image_path, "rb") as f:
    input_data = f.read()

output = remove(input_data)

with open(output_path, "wb") as f:
    f.write(output)

print(f"Background removed -> {output_path}")

# ---------------- LOAD IMAGE ----------------

img = cv2.imread(str(output_path), cv2.IMREAD_UNCHANGED)

if img is None:
    raise FileNotFoundError(output_path)

if img.shape[2] != 4:
    raise ValueError("Expected an RGBA image.")

alpha = img[:, :, 3]

# ---------------- CREATE MASK ----------------

mask = (alpha > 5).astype(np.uint8)

# ---------------- FIND COMPONENTS ----------------

num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(
    mask,
    connectivity=8
)

sprites = []

for i in range(1, num_labels):

    x = stats[i, cv2.CC_STAT_LEFT]
    y = stats[i, cv2.CC_STAT_TOP]
    w = stats[i, cv2.CC_STAT_WIDTH]
    h = stats[i, cv2.CC_STAT_HEIGHT]
    area = stats[i, cv2.CC_STAT_AREA]

    # ignorar ruido
    if area < 500:
        continue

    sprites.append((x, y, w, h))

# Orden izquierda->derecha
sprites.sort(key=lambda s: s[0])

print(f"Detected {len(sprites)} sprites")

# ---------------- SAVE ----------------

for i, (x, y, w, h) in enumerate(sprites):

    sprite = img[y:y+h, x:x+w]

    filename = out_dir / f"frame_{i:02d}.png"

    cv2.imwrite(str(filename), sprite)

    print(f"Saved {filename}")

print("Finished.")