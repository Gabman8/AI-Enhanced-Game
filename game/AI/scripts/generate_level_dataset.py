from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PATH = BASE_DIR / "datasets" / "dataset_level_difficulty.csv"
NUM_SAMPLES = 50000


# Clamp a value so it stays inside the allowed range.
def clamp(value, low, high):
    return max(low, min(high, value))


# Generate sample for the current workflow.
def generate_sample(level, player_skill):
    base_difficulty = 1.0 + (level - 1) * 0.08
    performance_noise = np.random.normal(0.0, 0.08)
    performance = clamp(
        player_skill * 0.6 + (1.0 / base_difficulty) * 0.3 + performance_noise,
        0.05,
        0.98,
    )

    enemies_spawned = int(clamp(np.round(4 + base_difficulty * 2 + np.random.normal(0, 1.2)), 2, 12))
    enemies_killed = int(clamp(np.round(enemies_spawned * (0.4 + performance * 0.5 + np.random.normal(0, 0.05))), 0, enemies_spawned))
    player_attacks = int(clamp(np.round(enemies_spawned * (2.8 + performance * 1.5 + np.random.normal(0, 1.0))), 1, 80))
    player_hits = int(clamp(np.round(player_attacks * (0.35 + performance * 0.5 + np.random.normal(0, 0.05))), 0, player_attacks))
    player_accuracy = player_hits / player_attacks if player_attacks else 0.0
    player_health_remaining = clamp(np.round(100 * (0.25 + performance * 0.65 + np.random.normal(0, 0.06))), 0, 100)
    player_damage_received = clamp(100 - player_health_remaining + np.random.normal(0, 8), 0, 120)
    times_player_died = 0 if performance > 0.35 else int(np.random.choice([0, 1], p=[0.75, 0.25]))
    times_hit = int(clamp(np.round(player_hits * (0.5 + np.random.normal(0, 0.12))), 0, 50))
    time_seconds = clamp(np.round(30 + enemies_spawned * 5 + (1.0 - performance) * 40 + np.random.normal(0, 7)), 15, 220)

    difficulty_signal = performance * 0.55 + (1.0 - times_player_died * 0.2) * 0.45
    enemy_count = int(clamp(np.round(2 + (1.0 - difficulty_signal) * 3.5 + np.random.normal(0, 0.4)), 1, 12))
    strong_enemy_prob = clamp(0.18 + difficulty_signal * 0.35 + np.random.normal(0, 0.06), 0.05, 0.75)
    enemy_health_scale = clamp(1.0 + (1.0 - difficulty_signal) * 0.22 + np.random.normal(0, 0.04), 0.75, 1.45)
    enemy_strength_scale = clamp(1.0 + (1.0 - difficulty_signal) * 0.20 + np.random.normal(0, 0.05), 0.75, 1.55)
    enemy_speed_scale = clamp(1.0 + (difficulty_signal - 0.5) * 0.18 + np.random.normal(0, 0.04), 0.8, 1.4)

    return {
        "level": level,
        "enemies_spawned": enemies_spawned,
        "enemies_killed": enemies_killed,
        "player_damage_received": round(player_damage_received, 2),
        "player_health_remaining": round(player_health_remaining, 2),
        "player_attacks": player_attacks,
        "player_hits": player_hits,
        "player_accuracy": round(player_accuracy, 3),
        "time_seconds": round(time_seconds, 2),
        "times_player_died": times_player_died,
        "times_hit": times_hit,
        "enemy_count": enemy_count,
        "strong_enemy_prob": round(strong_enemy_prob, 3),
        "enemy_health_scale": round(enemy_health_scale, 3),
        "enemy_strength_scale": round(enemy_strength_scale, 3),
        "enemy_speed_scale": round(enemy_speed_scale, 3),
    }


rows = []
for _ in range(NUM_SAMPLES):
    level = int(np.random.randint(1, 11))
    player_skill = float(np.clip(np.random.beta(2.5, 2.2), 0.05, 0.98))
    rows.append(generate_sample(level, player_skill))

output_dir = OUTPUT_PATH.parent
output_dir.mkdir(parents=True, exist_ok=True)

pd.DataFrame(rows).to_csv(OUTPUT_PATH, index=False)
print(f"Level difficulty dataset saved to {OUTPUT_PATH} with {len(rows)} records.")
