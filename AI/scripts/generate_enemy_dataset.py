from pathlib import Path

import numpy as np
import pandas as pd

# Set seed for reproducibility
np.random.seed(42)

sequence_length = 40
num_sequences = 5000
num_records = sequence_length * num_sequences

enemy_types = ["mage", "archer", "melee"]
enemy_type_probs = [0.30, 0.30, 0.40]
enemy_states = ["rest", "patrol", "pursuit", "combat", "retreat", "exploring"]
enemy_state_probs = [0.12, 0.30, 0.15, 0.25, 0.10, 0.08]
directions = ["N", "S", "E", "W"]
map_areas = ["forest", "cave", "dungeon", "village"]
terrains = ["grass", "stone", "road"]
weathers = ["clear", "rain", "storm"]

print(f"Generating {num_records} records as {num_sequences} temporal sequences...")


def sample_personality(enemy_type):
    if enemy_type == "melee":
        return np.round(np.random.uniform(0.7, 1.0), 2), np.round(np.random.uniform(0.2, 0.5), 2), np.round(np.random.uniform(0.35, 0.6), 2)
    if enemy_type == "archer":
        return np.round(np.random.uniform(0.2, 0.6), 2), np.round(np.random.uniform(0.4, 0.8), 2), np.round(np.random.uniform(0.4, 0.7), 2)
    return np.round(np.random.uniform(0.4, 0.8), 2), np.round(np.random.uniform(0.2, 0.6), 2), np.round(np.random.uniform(0.7, 1.0), 2)


def clamp(value, low, high):
    return max(low, min(high, value))


rows = []

for seq_idx in range(num_sequences):
    enemy_id = int(np.random.randint(1, 1001))
    enemy_type = np.random.choice(enemy_types, p=enemy_type_probs)
    enemy_level = int(np.random.choice(range(1, 11), p=[0.15, 0.15, 0.15, 0.12, 0.12, 0.10, 0.08, 0.06, 0.04, 0.03]))
    enemy_max_health = float(np.round(100.0 + 10.0 * enemy_level + np.random.uniform(-10, 10), 2))
    enemy_current_health = float(np.round(np.random.uniform(0.55, 0.95) * enemy_max_health, 2))
    enemy_energy = float(np.round(np.random.uniform(30.0, 100.0), 2))
    enemy_state = str(np.random.choice(enemy_states, p=enemy_state_probs))
    enemy_pos_x = float(np.round(np.random.uniform(0.0, 500.0), 2))
    enemy_pos_y = float(np.round(np.random.uniform(0.0, 500.0), 2))
    enemy_direction = str(np.random.choice(directions))
    enemy_speed = float(np.round(np.random.beta(a=3, b=3) * 3.0, 2))

    player_pos_x = float(np.round(np.random.uniform(0.0, 500.0), 2))
    player_pos_y = float(np.round(np.random.uniform(0.0, 500.0), 2))
    player_speed = float(np.round(np.random.uniform(0.0, 5.0), 2))
    player_direction = str(np.random.choice(directions))
    player_running = int(np.random.choice([0, 1], p=[0.70, 0.30]))
    player_attacking = int(np.random.choice([0, 1], p=[0.90, 0.10]))
    player_attack_type = str(np.random.choice(["melee", "ranged", "magic"], p=[0.50, 0.30, 0.20])) if player_attacking == 1 else "none"
    player_health = float(np.round(np.clip(np.random.normal(70, 20), 0, 100), 2))
    player_last_damage_received = float(np.round(np.random.uniform(0.0, 100.0), 2))
    player_combo = int(np.clip(np.random.geometric(p=0.15) - 1, 0, 50))
    player_visible = int(np.random.choice([0, 1], p=[0.50, 0.50]))
    player_noise = float(np.round(np.random.beta(a=1, b=3), 2))
    player_threat = float(np.round(np.clip((player_health / 100.0) * (1.0 - min(1.0, np.sqrt((player_pos_x - enemy_pos_x) ** 2 + (player_pos_y - enemy_pos_y) ** 2) / 100.0)), 0.0, 1.0), 2))

    allies_nearby = int(np.random.choice([0, 1, 2, 3, 4, 5], p=[0.50, 0.30, 0.12, 0.05, 0.02, 0.01]))
    enemies_nearby = int(np.random.choice([0, 1, 2, 3, 4, 5], p=[0.50, 0.30, 0.12, 0.05, 0.02, 0.01]))
    cover_available = int(np.random.choice([0, 1], p=[0.70, 0.30]))
    cover_distance = float(np.round(np.random.uniform(0.0, 20.0), 2)) if cover_available == 1 else float(0.0)
    medkit_visible = int(np.random.choice([0, 1], p=[0.90, 0.10]))
    time_since_last_hit = float(np.round(np.random.exponential(scale=5.0), 2))
    time_since_last_hit = float(clamp(time_since_last_hit, 0.0, 30.0))
    time_in_current_state = float(np.round(np.random.exponential(scale=7.0), 2))
    time_in_current_state = float(clamp(time_in_current_state, 0.0, 30.0))
    seconds_since_last_action = float(np.round(np.random.uniform(0.0, 15.0), 2))
    actions_last_5_seconds = int(np.random.choice([0, 1, 2, 3, 4, 5], p=[0.30, 0.30, 0.20, 0.10, 0.07, 0.03]))
    enemy_last_damage_received = float(np.round(np.random.uniform(0.0, 50.0), 2))
    recent_player_damage = float(np.round(np.random.uniform(0.0, 20.0), 2))
    enemy_kills = int(np.clip(np.random.geometric(p=0.2) - 1, 0, 100))
    player_kills = int(np.clip(np.random.geometric(p=0.05) - 1, 0, 100))
    remaining_cooldown = float(np.round(np.random.uniform(0.0, 10.0), 2))

    map_area = str(np.random.choice(map_areas))
    terrain = str(np.random.choice(terrains))
    time_of_day = str(np.random.choice(["day", "night"], p=[0.70, 0.30]))
    weather = str(np.random.choice(weathers, p=[0.75, 0.20, 0.05]))

    aggression_score, fear_score, intelligence_score = sample_personality(enemy_type)

    previous_decision = "start"

    for step in range(sequence_length):
        player_dx = player_pos_x - enemy_pos_x
        player_dy = player_pos_y - enemy_pos_y
        player_distance = float(np.round(np.sqrt(player_dx ** 2 + player_dy ** 2), 2))
        player_dir_x = float(np.round(player_dx / np.where(player_distance == 0, 1, player_distance), 2))
        player_dir_y = float(np.round(player_dy / np.where(player_distance == 0, 1, player_distance), 2))

        health_pct = float(np.round(enemy_current_health / enemy_max_health, 4))
        energy_pct = float(np.round(enemy_energy / 100.0, 4))
        line_of_sight = int(player_visible == 1 and player_distance < 100)
        attack_range = 3.0 if enemy_type == "melee" else 25.0 if enemy_type == "archer" else 20.0
        can_attack = int(player_distance < attack_range)
        can_heal = int(health_pct < 0.25 and medkit_visible == 1)
        outnumbered = int(enemies_nearby > allies_nearby)

        if can_heal == 1 and health_pct < 0.35 and enemy_energy > 25:
            decision = "heal"
        elif outnumbered == 1 and health_pct < 0.35:
            decision = "hide" if aggression_score < 0.5 else "retreat"
        elif can_attack == 1:
            if enemy_energy > 70 and aggression_score > 0.6:
                decision = "strong_attack"
            elif enemy_type in ["archer", "mage"] and player_distance > 5:
                decision = "ranged_attack"
            elif health_pct < 0.25:
                decision = "dodge"
            else:
                decision = "attack"
        elif enemy_state == "combat":
            decision = "flank" if aggression_score > 0.5 else "chase"
        elif line_of_sight == 1 or player_noise > 0.65:
            decision = "investigate"
        elif enemy_state == "patrol":
            decision = "patrol"
        else:
            decision = np.random.choice(["wait", "search", "guard"], p=[0.5, 0.3, 0.2])

        if decision in ["attack", "strong_attack", "ranged_attack"]:
            enemy_energy = float(clamp(enemy_energy - np.random.uniform(8.0, 20.0), 0.0, 100.0))
            player_health = float(clamp(player_health - np.random.uniform(4.0, 15.0), 0.0, 100.0))
            if np.random.rand() < 0.25:
                enemy_current_health = float(clamp(enemy_current_health - np.random.uniform(0.0, 10.0), 0.0, enemy_max_health))
        elif decision == "heal":
            enemy_energy = float(clamp(enemy_energy - np.random.uniform(10.0, 18.0), 0.0, 100.0))
            enemy_current_health = float(clamp(enemy_current_health + np.random.uniform(8.0, 18.0), 0.0, enemy_max_health))
        elif decision in ["retreat", "hide"]:
            player_distance = float(clamp(player_distance + np.random.uniform(8.0, 20.0), 0.0, 150.0))
        elif decision in ["chase", "flank"]:
            player_distance = float(clamp(player_distance - np.random.uniform(6.0, 18.0), 0.0, 150.0))
        elif decision in ["investigate", "search"]:
            player_distance = float(clamp(player_distance + np.random.uniform(-3.0, 5.0), 0.0, 150.0))
        else:
            player_distance = float(clamp(player_distance + np.random.uniform(-2.0, 3.0), 0.0, 150.0))

        if decision in ["attack", "strong_attack"]:
            enemy_state = "combat"
        elif decision == "ranged_attack":
            enemy_state = "combat"
        elif decision == "dodge":
            enemy_state = "combat"
        elif decision in ["chase", "flank"]:
            enemy_state = "combat"
        elif decision in ["retreat", "hide"]:
            enemy_state = "retreat"
        elif decision in ["patrol", "search", "investigate", "guard"]:
            enemy_state = "patrol"
        elif decision == "heal":
            enemy_state = "combat" if player_distance < 30 else "rest"
        else:
            enemy_state = "rest"

        angle = np.random.uniform(0.0, 2 * np.pi)
        player_dx = np.cos(angle) * player_distance
        player_dy = np.sin(angle) * player_distance
        player_pos_x = float(clamp(enemy_pos_x + player_dx, 0.0, 500.0))
        player_pos_y = float(clamp(enemy_pos_y + player_dy, 0.0, 500.0))
        player_dir_x = float(np.round(player_dx / np.where(player_distance == 0, 1, player_distance), 2))
        player_dir_y = float(np.round(player_dy / np.where(player_distance == 0, 1, player_distance), 2))

        player_direction = str(np.random.choice(directions))
        player_running = int(np.random.rand() < 0.35)
        player_attacking = int(np.random.rand() < (0.25 if player_distance < 20 else 0.10))
        player_attack_type = str(np.random.choice(["melee", "ranged", "magic"], p=[0.50, 0.30, 0.20])) if player_attacking == 1 else "none"
        player_visible = int(player_distance < 80 and np.random.rand() < 0.85)
        player_noise = float(clamp(player_running * np.random.uniform(0.5, 1.0) + player_attacking * 0.2 + np.random.beta(1, 3) * 0.5, 0.0, 1.0))
        player_threat = float(np.round(clamp((player_health / 100.0) * (1.0 - min(1.0, player_distance / 100.0)), 0.0, 1.0), 2))

        if decision in ["attack", "strong_attack", "ranged_attack", "dodge"]:
            time_since_last_hit = 0.0
        else:
            time_since_last_hit = float(clamp(time_since_last_hit + np.random.uniform(0.5, 2.5), 0.0, 30.0))

        time_in_current_state = float(clamp(time_in_current_state + np.random.uniform(-1.0, 2.0), 0.0, 30.0))
        seconds_since_last_action = float(clamp(seconds_since_last_action + np.random.uniform(0.5, 2.5), 0.0, 30.0))
        actions_last_5_seconds = int(clamp(actions_last_5_seconds + np.random.choice([-1, 0, 1], p=[0.35, 0.45, 0.20]), 0, 10))
        recent_player_damage = float(clamp(recent_player_damage + np.random.normal(0, 3.0), 0.0, 100.0))
        enemy_last_damage_received = float(clamp(enemy_last_damage_received + np.random.normal(0, 5.0), 0.0, 100.0))

        rows.append(
            {
                "enemy_id": enemy_id,
                "enemy_type": enemy_type,
                "enemy_level": enemy_level,
                "enemy_current_health": enemy_current_health,
                "enemy_max_health": enemy_max_health,
                "enemy_energy": enemy_energy,
                "enemy_state": enemy_state,
                "enemy_pos_x": enemy_pos_x,
                "enemy_pos_y": enemy_pos_y,
                "enemy_direction": enemy_direction,
                "enemy_speed": enemy_speed,
                "player_distance": player_distance,
                "player_health": player_health,
                "player_speed": player_speed,
                "player_direction": player_direction,
                "player_running": player_running,
                "player_attacking": player_attacking,
                "player_attack_type": player_attack_type,
                "player_last_damage_received": player_last_damage_received,
                "player_combo": player_combo,
                "player_visible": player_visible,
                "player_noise": player_noise,
                "player_threat": player_threat,
                "allies_nearby": allies_nearby,
                "enemies_nearby": enemies_nearby,
                "cover_available": cover_available,
                "cover_distance": cover_distance,
                "medkit_visible": medkit_visible,
                "time_since_last_hit": time_since_last_hit,
                "enemy_last_damage_received": enemy_last_damage_received,
                "enemy_kills": enemy_kills,
                "player_kills": player_kills,
                "map_area": map_area,
                "terrain": terrain,
                "time_of_day": time_of_day,
                "weather": weather,
                "health_pct": health_pct,
                "energy_pct": energy_pct,
                "distance_delta": float(np.round(np.random.normal(0, 2.0), 2)),
                "outnumbered": outnumbered,
                "recent_player_damage": recent_player_damage,
                "line_of_sight": line_of_sight,
                "remaining_cooldown": float(clamp(remaining_cooldown - np.random.uniform(0.0, 1.2), 0.0, 10.0)),
                "aggression_score": aggression_score,
                "fear_score": fear_score,
                "intelligence_score": intelligence_score,
                "time_in_current_state": time_in_current_state,
                "seconds_since_last_action": seconds_since_last_action,
                "actions_last_5_seconds": actions_last_5_seconds,
                "player_dir_x": player_dir_x,
                "player_dir_y": player_dir_y,
                "previous_decision": previous_decision,
                "decision": decision,
            }
        )

        previous_decision = decision

# Build the DataFrame
df = pd.DataFrame(rows)

# Save to CSV file
output_dir = Path(__file__).resolve().parent / "../datasets"
output_dir.mkdir(parents=True, exist_ok=True)
out_path = output_dir / "dataset_enemies_ml.csv"
df.to_csv(out_path, index=False)
print(f"File '{out_path}' exported successfully with {len(df)} records ({sequence_length}-step sequences).")
