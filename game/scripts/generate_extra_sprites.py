"""
Generate:
  - frame_02 for strong_enemy running animation (mid-stride interpolation)
  - All sprite frames for final_boss (large muscular commander, no sleeves)

Run from the game/ directory:
    python3 scripts/generate_extra_sprites.py
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import numpy as np

GAME_ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = GAME_ROOT / "images"

# ─────────────────────────────────────────────────────────────────────────────
# Utility helpers
# ─────────────────────────────────────────────────────────────────────────────

# Save the relevant data to the expected destination.
def _save(img: Image.Image, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(path), "PNG")
    print(f"Saved: {path}")


# Handle blend for the current workflow.
def _blend(a: Image.Image, b: Image.Image, t: float) -> Image.Image:
    """Alpha-aware blend between two RGBA frames."""
    a = a.convert("RGBA")
    b = b.convert("RGBA")
    if a.size != b.size:
        b = b.resize(a.size, Image.LANCZOS)
    return Image.blend(a, b, t)


# Handle shift for the current workflow.
def _shift(img: Image.Image, dx: int, dy: int) -> Image.Image:
    """Shift image by (dx, dy), filling empty space with transparent."""
    result = Image.new("RGBA", img.size, (0, 0, 0, 0))
    result.paste(img, (dx, dy))
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Strong enemy – frame_02  (mid-stride, between frame_00 and frame_01)
# ─────────────────────────────────────────────────────────────────────────────

# Generate strong enemy frame 02 for the current workflow.
def generate_strong_enemy_frame_02():
    """Generate frame_02 by stretching frame_01 slightly and shifting."""
    src_dir = IMAGES_DIR / "strong_enemy" / "running"
    f0 = Image.open(src_dir / "frame_00.png").convert("RGBA")
    f1 = Image.open(src_dir / "frame_01.png").convert("RGBA")

    # Create a canvas and place both frames
    w = max(f0.width, f1.width) + 20
    h = max(f0.height, f1.height)

    c0 = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    c0.paste(f0, ((w - f0.width) // 2 - 8, h - f0.height), f0)

    c1_scaled = f1.resize(
        (int(f1.width * 1.05), int(f1.height * 1.02)),
        Image.LANCZOS
    )
    c1 = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    c1.paste(c1_scaled, ((w - c1_scaled.width) // 2 + 4, h - c1_scaled.height), c1_scaled)

    # 70% toward running pose (mid-stride)
    mid = Image.blend(c0, c1, 0.70)

    # Trim to bounding box
    bbox = mid.getbbox()
    if bbox:
        mid = mid.crop(bbox)

    _save(mid, src_dir / "frame_02.png")


# ─────────────────────────────────────────────────────────────────────────────
# Final boss – pixel-art style programmatic sprites
#   Palette: military green/khaki armour, bare muscular arms, dark skin tones
# ─────────────────────────────────────────────────────────────────────────────

# Colour palette
_SKIN       = (190, 130, 90, 255)
_SKIN_DARK  = (150, 95, 60, 255)
_SKIN_HIGH  = (220, 165, 120, 255)
_MILITARY   = (72, 95, 55, 255)
_MIL_DARK   = (45, 62, 35, 255)
_MIL_HIGH   = (100, 130, 75, 255)
_KHAKI      = (130, 115, 75, 255)
_KHAKI_DRK  = (90, 78, 48, 255)
_BOOTS      = (40, 30, 20, 255)
_OUTLINE    = (20, 15, 10, 255)
_BELT       = (50, 38, 22, 255)
_BUCKLE     = (200, 175, 90, 255)
_METAL      = (130, 140, 145, 255)
_METAL_HIGH = (200, 210, 215, 255)
_MEDAL      = (210, 160, 40, 255)
_EYE        = (55, 35, 20, 255)
_WHITE      = (245, 245, 240, 255)
_SCAR       = (160, 100, 75, 255)
_BLOOD      = (160, 30, 30, 255)
_TRANSP     = (0, 0, 0, 0)

W, H = 240, 340   # canvas size for final boss


# Draw boss body on the current screen or surface.
def _draw_boss_body(draw: ImageDraw.Draw, lean_x: int = 0, arm_raise: int = 0):
    """Draw a standing/slightly-posed final boss figure."""
    cx = W // 2 + lean_x

    # ── Legs ──────────────────────────────────────────────────────────────
    # Left leg
    draw.rectangle([cx - 50, H - 130, cx - 15, H - 10], fill=_KHAKI)
    draw.rectangle([cx - 52, H - 132, cx - 13, H - 8], outline=_OUTLINE, width=2)
    # knee pad
    draw.ellipse([cx - 48, H - 95, cx - 18, H - 65], fill=_METAL, outline=_OUTLINE, width=1)
    # boot
    draw.rectangle([cx - 54, H - 12, cx - 10, H], fill=_BOOTS)
    draw.rectangle([cx - 56, H - 14, cx - 8, H + 2], outline=_OUTLINE, width=2)

    # Right leg
    draw.rectangle([cx + 15, H - 130, cx + 50, H - 10], fill=_KHAKI_DRK)
    draw.rectangle([cx + 13, H - 132, cx + 52, H - 8], outline=_OUTLINE, width=2)
    # knee pad
    draw.ellipse([cx + 18, H - 95, cx + 48, H - 65], fill=_METAL, outline=_OUTLINE, width=1)
    # boot
    draw.rectangle([cx + 10, H - 12, cx + 56, H], fill=_BOOTS)
    draw.rectangle([cx + 8, H - 14, cx + 58, H + 2], outline=_OUTLINE, width=2)

    # ── Torso ─────────────────────────────────────────────────────────────
    draw.rectangle([cx - 52, H - 270, cx + 52, H - 120], fill=_MILITARY)
    draw.rectangle([cx - 54, H - 272, cx + 54, H - 118], outline=_OUTLINE, width=2)
    # armour plate / chest detail
    draw.rectangle([cx - 38, H - 258, cx + 38, H - 175], fill=_MIL_DARK, outline=_OUTLINE, width=1)
    draw.line([cx, H - 258, cx, H - 175], fill=_OUTLINE, width=2)
    # medals / badge
    draw.ellipse([cx - 28, H - 248, cx - 14, H - 234], fill=_MEDAL, outline=_OUTLINE, width=1)
    draw.ellipse([cx - 8, H - 240, cx + 6, H - 226], fill=_MEDAL, outline=_OUTLINE, width=1)
    # belt
    draw.rectangle([cx - 52, H - 132, cx + 52, H - 118], fill=_BELT)
    draw.rectangle([cx - 12, H - 132, cx + 12, H - 118], fill=_BUCKLE, outline=_OUTLINE, width=1)

    # ── Bare arms (no sleeves – massive) ──────────────────────────────────
    ar = arm_raise
    # Left arm
    draw.rectangle([cx - 88, H - 268 + ar, cx - 52, H - 190 + ar], fill=_SKIN)
    draw.rectangle([cx - 90, H - 270 + ar, cx - 50, H - 188 + ar], outline=_OUTLINE, width=2)
    # forearm
    draw.rectangle([cx - 86, H - 192 + ar, cx - 50, H - 140 + ar], fill=_SKIN_DARK)
    draw.rectangle([cx - 88, H - 194 + ar, cx - 48, H - 138 + ar], outline=_OUTLINE, width=2)
    # fist left
    draw.ellipse([cx - 88, H - 148 + ar, cx - 52, H - 112 + ar], fill=_SKIN, outline=_OUTLINE, width=2)
    # tattoo hint
    draw.line([cx - 78, H - 240 + ar, cx - 58, H - 210 + ar], fill=_SCAR, width=2)
    draw.line([cx - 82, H - 220 + ar, cx - 62, H - 198 + ar], fill=_SCAR, width=1)

    # Right arm
    draw.rectangle([cx + 52, H - 268, cx + 88, H - 190], fill=_SKIN_HIGH)
    draw.rectangle([cx + 50, H - 270, cx + 90, H - 188], outline=_OUTLINE, width=2)
    # forearm
    draw.rectangle([cx + 50, H - 192, cx + 86, H - 140], fill=_SKIN)
    draw.rectangle([cx + 48, H - 194, cx + 88, H - 138], outline=_OUTLINE, width=2)
    # fist right
    draw.ellipse([cx + 52, H - 148, cx + 88, H - 112], fill=_SKIN, outline=_OUTLINE, width=2)
    # vein detail
    draw.line([cx + 58, H - 195, cx + 80, H - 155], fill=_SKIN_DARK, width=2)

    # ── Neck ──────────────────────────────────────────────────────────────
    draw.rectangle([cx - 22, H - 300, cx + 22, H - 268], fill=_SKIN_DARK)
    draw.rectangle([cx - 24, H - 302, cx + 24, H - 266], outline=_OUTLINE, width=2)

    # ── Head ──────────────────────────────────────────────────────────────
    # Head base (large, square jaw)
    draw.rectangle([cx - 40, H - 370, cx + 40, H - 296], fill=_SKIN)
    draw.rectangle([cx - 42, H - 372, cx + 42, H - 294], outline=_OUTLINE, width=2)
    # jaw
    draw.rectangle([cx - 36, H - 310, cx + 36, H - 294], fill=_SKIN_DARK, outline=_OUTLINE, width=1)
    # forehead / brow
    draw.rectangle([cx - 40, H - 370, cx + 40, H - 348], fill=_SKIN_DARK)
    # scar on cheek
    draw.line([cx + 18, H - 330, cx + 30, H - 316], fill=_SCAR, width=3)
    # eyes
    draw.ellipse([cx - 26, H - 348, cx - 10, H - 334], fill=_WHITE, outline=_OUTLINE, width=1)
    draw.ellipse([cx + 10, H - 348, cx + 26, H - 334], fill=_WHITE, outline=_OUTLINE, width=1)
    draw.ellipse([cx - 22, H - 345, cx - 14, H - 337], fill=_EYE)
    draw.ellipse([cx + 14, H - 345, cx + 22, H - 337], fill=_EYE)
    # eyebrows (heavy, military scowl)
    draw.line([cx - 28, H - 352, cx - 8, H - 350], fill=_OUTLINE, width=4)
    draw.line([cx + 8, H - 350, cx + 28, H - 352], fill=_OUTLINE, width=4)
    # nose
    draw.ellipse([cx - 6, H - 330, cx + 6, H - 318], fill=_SKIN_HIGH, outline=_OUTLINE, width=1)
    # mouth (stern expression)
    draw.line([cx - 14, H - 308, cx + 14, H - 308], fill=_OUTLINE, width=3)
    draw.line([cx - 10, H - 308, cx - 6, H - 311], fill=_OUTLINE, width=2)

    # ── Commander cap ──────────────────────────────────────────────────────
    # cap body
    draw.rectangle([cx - 42, H - 388, cx + 42, H - 365], fill=_MIL_DARK)
    draw.rectangle([cx - 44, H - 390, cx + 44, H - 363], outline=_OUTLINE, width=2)
    # cap brim
    draw.rectangle([cx - 50, H - 372, cx + 50, H - 364], fill=_OUTLINE)
    # cap band + insignia
    draw.rectangle([cx - 42, H - 375, cx + 42, H - 368], fill=_KHAKI)
    draw.polygon(
        [cx - 8, H - 384, cx, H - 394, cx + 8, H - 384],
        fill=_MEDAL, outline=_OUTLINE,
    )


# Draw weapon on the current screen or surface.
def _draw_weapon(draw: ImageDraw.Draw, cx: int, cy_base: int, variant: int = 0):
    """Draw a large military combat knife / machete."""
    # Handle
    draw.rectangle([cx - 6, cy_base - 80, cx + 6, cy_base - 30], fill=_BELT, outline=_OUTLINE, width=1)
    draw.rectangle([cx - 9, cy_base - 40, cx + 9, cy_base - 28], fill=_METAL, outline=_OUTLINE, width=1)
    # Blade
    pts = [
        (cx - 4, cy_base - 82),
        (cx + 4, cy_base - 82),
        (cx + 2, cy_base - 150 - variant * 10),
        (cx - 2, cy_base - 150 - variant * 10),
    ]
    draw.polygon(pts, fill=_METAL_HIGH, outline=_OUTLINE)


# Generate final boss sprites for the current workflow.
def generate_final_boss_sprites():
    out_base = IMAGES_DIR / "final_boss"

    # ── Running ─────────────────────────────────────────────────────────────
    running_dir = out_base / "running"
    running_dir.mkdir(parents=True, exist_ok=True)

    for i, (lean, arm_r) in enumerate([(0, 0), (8, -12), (-8, 8)]):
        canvas = Image.new("RGBA", (W, H), _TRANSP)
        draw = ImageDraw.Draw(canvas)
        _draw_boss_body(draw, lean_x=lean, arm_raise=arm_r)
        # Add a slight weapon in one hand
        _draw_weapon(draw, cx=W // 2 + lean + 72, cy_base=H - 100)
        bbox = canvas.getbbox()
        if bbox:
            canvas = canvas.crop(bbox)
        _save(canvas, running_dir / f"frame_{i:02d}.png")

    # ── Attack ──────────────────────────────────────────────────────────────
    attack_dir = out_base / "attack"
    attack_dir.mkdir(parents=True, exist_ok=True)

    # Frame 0: wind-up (arms raised)
    canvas = Image.new("RGBA", (W, H), _TRANSP)
    draw = ImageDraw.Draw(canvas)
    _draw_boss_body(draw, lean_x=-10, arm_raise=-40)
    _draw_weapon(draw, cx=W // 2 - 10 - 70, cy_base=H - 148)
    _draw_weapon(draw, cx=W // 2 - 10 + 70, cy_base=H - 148)
    bbox = canvas.getbbox()
    if bbox:
        canvas = canvas.crop(bbox)
    _save(canvas, attack_dir / "frame_00.png")

    # Frame 1: strike (forward lean, arms down-diagonal)
    canvas = Image.new("RGBA", (W, H), _TRANSP)
    draw = ImageDraw.Draw(canvas)
    _draw_boss_body(draw, lean_x=16, arm_raise=24)
    _draw_weapon(draw, cx=W // 2 + 16 + 80, cy_base=H - 106, variant=1)
    bbox = canvas.getbbox()
    if bbox:
        canvas = canvas.crop(bbox)
    _save(canvas, attack_dir / "frame_01.png")

    # Frame 2: follow-through
    canvas = Image.new("RGBA", (W, H), _TRANSP)
    draw = ImageDraw.Draw(canvas)
    _draw_boss_body(draw, lean_x=20, arm_raise=35)
    _draw_weapon(draw, cx=W // 2 + 20 + 75, cy_base=H - 95, variant=2)
    bbox = canvas.getbbox()
    if bbox:
        canvas = canvas.crop(bbox)
    _save(canvas, attack_dir / "frame_02.png")

    # ── Death ───────────────────────────────────────────────────────────────
    death_dir = out_base / "death"
    death_dir.mkdir(parents=True, exist_ok=True)

    # Frame 0: staggering
    canvas = Image.new("RGBA", (W, H), _TRANSP)
    draw = ImageDraw.Draw(canvas)
    _draw_boss_body(draw, lean_x=30, arm_raise=18)
    # blood detail
    draw.ellipse([W // 2 + 10, H - 220, W // 2 + 30, H - 200], fill=_BLOOD)
    bbox = canvas.getbbox()
    if bbox:
        canvas = canvas.crop(bbox)
    _save(canvas, death_dir / "frame_00.png")

    # Frame 1: falling/kneeling (compress vertically)
    canvas = Image.new("RGBA", (W, H), _TRANSP)
    draw = ImageDraw.Draw(canvas)
    # Draw only lower body (on ground) – squish by skipping head high point
    lean = 40
    cx = W // 2 + lean
    draw.rectangle([cx - 50, H - 80, cx - 15, H - 10], fill=_KHAKI, outline=_OUTLINE, width=2)
    draw.rectangle([cx + 15, H - 60, cx + 50, H - 10], fill=_KHAKI_DRK, outline=_OUTLINE, width=2)
    draw.rectangle([cx - 54, H - 12, cx - 10, H], fill=_BOOTS, outline=_OUTLINE, width=2)
    draw.rectangle([cx + 10, H - 12, cx + 56, H], fill=_BOOTS, outline=_OUTLINE, width=2)
    draw.rectangle([cx - 50, H - 170, cx + 50, H - 78], fill=_MILITARY, outline=_OUTLINE, width=2)
    draw.rectangle([cx - 38, H - 160, cx + 38, H - 95], fill=_MIL_DARK, outline=_OUTLINE, width=1)
    # head on ground angle
    draw.ellipse([cx - 30, H - 195, cx + 30, H - 155], fill=_SKIN, outline=_OUTLINE, width=2)
    draw.rectangle([cx - 32, H - 210, cx + 32, H - 190], fill=_MIL_DARK, outline=_OUTLINE, width=2)
    bbox = canvas.getbbox()
    if bbox:
        canvas = canvas.crop(bbox)
    _save(canvas, death_dir / "frame_01.png")

    print("\nFinal boss sprite generation complete.")


if __name__ == "__main__":
    print("Generating strong_enemy frame_02...")
    generate_strong_enemy_frame_02()
    print("\nGenerating final_boss sprites...")
    generate_final_boss_sprites()
    print("\nAll done.")
