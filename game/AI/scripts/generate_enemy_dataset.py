from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------

np.random.seed(42)

# =============================== CONFIG =====================================

SEQUENCE_LENGTH = 40
NUM_SEQUENCES = 5000
SCREEN_WIDTH = 1280
ATTACK_DISTANCE = 90
SCREEN_ENTRY_MARGIN = 150
DELTA_TIME = 1 / 144

ENEMY_TYPE_STATS = {
    "regular_enemy": {
        "health": 20,
        "strength": 20,
        "speed_range": (220.0, 340.0),
        "personalities": ["hostile"],
    },
    "strong_enemy": {
        "health": 50,
        "strength": 50,
        "speed_range": (180.0, 280.0),
        "personalities": ["aggressive", "ruthless"],
    },
    "final_boss": {
        "health": 100,
        "strength": 100,
        "speed_range": (250.0, 440.0),
        "personalities": ["calculating", "merciless"],
    },
}
ENEMY_TYPES = list(ENEMY_TYPE_STATS.keys())
ENEMY_TYPE_PROBS = [0.60, 0.30, 0.10]

MAIN_CHARACTER_STATS = {
    "health": 100,
    "strength": 100,
    "speed_range": (220.0, 450.0),
    "personalities": ["resolute"],
}

# El "actor" es el personaje sobre el que se registra la decisión (columnas
# enemy_*); puede ser un enemigo o el personaje principal en modo auto.
ACTOR_TYPES = ENEMY_TYPES + ["main_character"]
ACTOR_TYPE_PROBS = [0.45, 0.22, 0.08, 0.25]

BASE_ATTACK_PROB = {
    "hostile": 0.55,
    "aggressive": 0.65,
    "ruthless": 0.78,
    "calculating": 0.60,
    "merciless": 0.82,
    "resolute": 0.62,
}
FEAR_MULTIPLIER = {
    "hostile": 1.0,
    "aggressive": 0.8,
    "ruthless": 0.3,
    "calculating": 0.6,
    "merciless": 0.2,
    "resolute": 0.7,
}
ANGER_MULTIPLIER = {
    "hostile": 1.2,
    "aggressive": 1.3,
    "ruthless": 1.1,
    "calculating": 0.7,
    "merciless": 1.0,
    "resolute": 1.0,
}

PLAYER_MAX_HEALTH = 100.0
PLAYER_STRENGTH = 100.0

ANIMATION_STATES = ["idle", "running", "attack", "death"]
DECISIONS = ["ATTACK", "MOVE_RIGHT", "MOVE_LEFT"]

PLAYER_HIT_CHANCE = 0.70
ENEMY_HIT_CHANCE = 0.70
OPPONENT_ENEMY_APPROACH_PROB = 0.85
OPPONENT_ENEMY_ATTACK_PROB = 0.50

print(f"Generando {NUM_SEQUENCES * SEQUENCE_LENGTH} registros como "
      f"{NUM_SEQUENCES} encuentros de {SEQUENCE_LENGTH} frames...")


def clamp(value, low, high):
    return max(low, min(high, value))


def new_encounter():
    """Crea el estado inicial de un encuentro nuevo. El actor (enemy_*) puede
    ser un enemigo o el personaje principal; el oponente (player_*) es
    siempre el otro participante del combate."""
    actor_type = str(np.random.choice(ACTOR_TYPES, p=ACTOR_TYPE_PROBS))
    is_player_actor = actor_type == "main_character"
    stats = MAIN_CHARACTER_STATS if is_player_actor else ENEMY_TYPE_STATS[actor_type]

    personality = str(np.random.choice(stats["personalities"]))
    jitter = np.random.uniform(0.9, 1.1)

    actor_max_health = float(np.round(stats["health"] * jitter, 2))
    actor_health = float(np.round(actor_max_health * np.random.uniform(0.55, 1.0), 2))
    actor_strength = float(np.round(stats["strength"] * jitter, 2))
    actor_speed = float(np.round(np.random.uniform(*stats["speed_range"]), 2))

    anger = clamp(np.random.uniform(0.05, 0.35) * ANGER_MULTIPLIER[personality] / 1.2, 0.0, 1.0)
    fear = clamp(np.random.uniform(0.05, 0.30) * FEAR_MULTIPLIER[personality], 0.0, 1.0)
    confidence = clamp(np.random.uniform(0.3, 0.6), 0.0, 1.0)

    if is_player_actor:
        opponent_kind = "enemy"
        opponent_type = str(np.random.choice(ENEMY_TYPES, p=ENEMY_TYPE_PROBS))
        opponent_stats = ENEMY_TYPE_STATS[opponent_type]
        opponent_jitter = np.random.uniform(0.9, 1.1)
        opponent_max_health = float(np.round(opponent_stats["health"] * opponent_jitter, 2))
        opponent_strength = float(np.round(opponent_stats["strength"] * opponent_jitter, 2))
        opponent_speed = float(np.round(np.random.uniform(*opponent_stats["speed_range"]), 2))
    else:
        opponent_kind = "player"
        opponent_max_health = PLAYER_MAX_HEALTH
        opponent_strength = PLAYER_STRENGTH
        opponent_speed = float(np.random.uniform(150.0, 300.0))

    opponent_health = float(np.round(opponent_max_health * np.random.uniform(0.5, 1.0), 2))

    state = {
        "is_player_actor": is_player_actor,
        "opponent_kind": opponent_kind,
        "enemy_type": actor_type,
        "enemy_personality": personality,
        "enemy_max_health": actor_max_health,
        "enemy_health": actor_health,
        "enemy_strength": actor_strength,
        "enemy_speed": actor_speed,
        "enemy_running": 0,
        "enemy_jumping": 0,
        "enemy_attacking": 0,
        "enemy_dead": 0,
        "enemy_facing_right": True,
        "enemy_animation_state": "idle",
        "enemy_x": 0.0,
        "enemy_y": 0.0,
        "enemy_anger": round(anger, 3),
        "enemy_fear": round(fear, 3),
        "enemy_confidence": round(confidence, 3),
        "enemy_last_action": "start",
        "enemy_times_hit": 0,
        "enemy_times_attack": 0,
        "player_max_health": opponent_max_health,
        "player_health": opponent_health,
        "player_strength": opponent_strength,
        "player_speed": opponent_speed,
        "player_running": 0,
        "player_jumping": 0,
        "player_attacking": 0,
        "player_dead": 0,
        "player_facing_right": opponent_kind == "player",
        "player_animation_state": "idle",
        "player_x": 0.0,
        "player_y": 0.0,
    }

    entry_x = SCREEN_WIDTH - SCREEN_ENTRY_MARGIN
    jitter_x = float(np.random.uniform(-40.0, 40.0))

    if is_player_actor:
        # El enemigo (oponente) entra desde el margen derecho, igual que en
        # Game._spawn_enemy / _update_entering_enemy; el personaje principal
        # se mueve libremente por la pantalla.
        state["player_x"] = clamp(entry_x + jitter_x, 0.0, SCREEN_WIDTH)
        state["enemy_x"] = float(np.round(np.random.uniform(0.0, SCREEN_WIDTH), 2))
        state["enemy_facing_right"] = True
    else:
        state["enemy_x"] = clamp(entry_x + jitter_x, 0.0, SCREEN_WIDTH)
        state["player_x"] = float(np.round(np.random.uniform(0.0, SCREEN_WIDTH), 2))
        state["enemy_facing_right"] = False

    return state


def dominant_emotion(anger, fear, confidence):
    scores = {"angry": anger, "afraid": fear, "confident": confidence}
    label, value = max(scores.items(), key=lambda kv: kv[1])
    if value < 0.4:
        return "calm"
    return label


def move_toward(enemy_x, player_x):
    return "MOVE_RIGHT" if enemy_x < player_x else "MOVE_LEFT"


def move_away(enemy_x, player_x):
    return "MOVE_LEFT" if enemy_x < player_x else "MOVE_RIGHT"


def decide_action(personality, distance, health_pct, anger, fear, confidence, opponent_health_pct):
    in_range = distance <= ATTACK_DISTANCE
    base_attack = BASE_ATTACK_PROB[personality]
    fearless = personality in ("ruthless", "merciless")
    critical_health = health_pct < 0.20

    if in_range:
        flee_prob = clamp(
            fear * 0.55 + (0.35 if critical_health else 0.0),
            0.0, 0.85,
        )
        if fearless:
            flee_prob *= 0.25
        if np.random.rand() < flee_prob:
            return "flee"

        attack_prob = clamp(
            base_attack
            + anger * 0.35
            + confidence * 0.30
            - fear * 0.25
            + (0.15 if opponent_health_pct < 0.3 else 0.0),
            0.15, 0.97,
        )
        if np.random.rand() < attack_prob:
            return "attack"
        return "approach"

    flee_prob = 0.0
    if critical_health:
        flee_prob = clamp(fear * 0.5, 0.0, 0.5)
        if fearless:
            flee_prob *= 0.2
    if np.random.rand() < flee_prob:
        return "flee"

    return "approach"


def simulate_opponent_step(s):
    if s["opponent_kind"] == "player":
        move = np.random.choice([-1, 0, 1], p=[0.35, 0.30, 0.35])
        speed = float(np.random.uniform(150.0, 300.0))
        s["player_x"] = clamp(s["player_x"] + move * speed * DELTA_TIME, 0.0, SCREEN_WIDTH)
        s["player_facing_right"] = move >= 0 if move != 0 else s["player_facing_right"]
        s["player_running"] = int(move != 0 and np.random.rand() < 0.7)
        s["player_jumping"] = int(np.random.rand() < 0.05)
        s["player_y"] = -40.0 if s["player_jumping"] else 0.0

        distance = abs(s["enemy_x"] - s["player_x"])
        s["player_attacking"] = int(
            np.random.rand() < (0.30 if distance <= ATTACK_DISTANCE else 0.05)
        )
    else:
        distance = abs(s["enemy_x"] - s["player_x"])
        if distance > ATTACK_DISTANCE:
            s["player_attacking"] = 0
            if np.random.rand() < OPPONENT_ENEMY_APPROACH_PROB:
                sign = 1.0 if s["player_x"] < s["enemy_x"] else -1.0
                s["player_x"] = clamp(s["player_x"] + sign * s["player_speed"] * DELTA_TIME, 0.0, SCREEN_WIDTH)
                s["player_facing_right"] = sign > 0
                s["player_running"] = 1
            else:
                s["player_running"] = 0
        else:
            s["player_running"] = 0
            s["player_attacking"] = int(np.random.rand() < OPPONENT_ENEMY_ATTACK_PROB)

        s["player_jumping"] = int(np.random.rand() < 0.03)
        s["player_y"] = -40.0 if s["player_jumping"] else 0.0

    s["player_animation_state"] = (
        "attack" if s["player_attacking"] else "running" if s["player_running"] else "idle"
    )


rows = []

for seq_idx in range(NUM_SEQUENCES):

    s = new_encounter()

    for step in range(SEQUENCE_LENGTH):

        distance = float(np.round(abs(s["enemy_x"] - s["player_x"]), 2))
        health_pct = s["enemy_health"] / s["enemy_max_health"] if s["enemy_max_health"] else 0.0
        opponent_health_pct = s["player_health"] / s["player_max_health"] if s["player_max_health"] else 0.0

        intent = decide_action(
            s["enemy_personality"], distance, health_pct,
            s["enemy_anger"], s["enemy_fear"], s["enemy_confidence"],
            opponent_health_pct,
        )

        if intent == "attack":
            decision = "ATTACK"
        elif intent == "approach":
            decision = move_toward(s["enemy_x"], s["player_x"])
        else:  # flee
            decision = move_away(s["enemy_x"], s["player_x"])

        s["enemy_emotion"] = dominant_emotion(s["enemy_anger"], s["enemy_fear"], s["enemy_confidence"])

        # -------------------- registrar la fila (estado ANTES de aplicar la decisión) --------------------
        rows.append({
            "enemy_type": s["enemy_type"],
            "enemy_personality": s["enemy_personality"],
            "enemy_emotion": s["enemy_emotion"],
            "enemy_health": round(s["enemy_health"], 2),
            "enemy_strength": round(s["enemy_strength"], 2),
            "enemy_speed": round(s["enemy_speed"], 2),
            "enemy_running": s["enemy_running"],
            "enemy_jumping": s["enemy_jumping"],
            "enemy_attacking": s["enemy_attacking"],
            "enemy_dead": s["enemy_dead"],
            "enemy_facing_right": int(s["enemy_facing_right"]),
            "enemy_animation_state": s["enemy_animation_state"],
            "enemy_x": round(s["enemy_x"], 2),
            "enemy_y": round(s["enemy_y"], 2),
            "enemy_anger": round(s["enemy_anger"], 3),
            "enemy_fear": round(s["enemy_fear"], 3),
            "enemy_confidence": round(s["enemy_confidence"], 3),
            "enemy_last_action": s["enemy_last_action"],
            "enemy_times_hit": s["enemy_times_hit"],
            "enemy_times_attack": s["enemy_times_attack"],
            "player_health": round(s["player_health"], 2),
            "player_strength": round(s["player_strength"], 2),
            "player_running": s["player_running"],
            "player_jumping": s["player_jumping"],
            "player_attacking": s["player_attacking"],
            "player_dead": s["player_dead"],
            "player_facing_right": int(s["player_facing_right"]),
            "player_animation_state": s["player_animation_state"],
            "player_x": round(s["player_x"], 2),
            "player_y": round(s["player_y"], 2),
            "distance": distance,
            "decision": decision,
        })

        # -------------------- aplicar la decisión / física del actor (Character.move_left/right) --------------------
        if decision == "ATTACK":
            s["enemy_times_attack"] += 1
            s["enemy_attacking"] = 1
            s["enemy_running"] = 0
            s["enemy_animation_state"] = "attack"
            hit_chance = PLAYER_HIT_CHANCE if s["is_player_actor"] else ENEMY_HIT_CHANCE
            if np.random.rand() < hit_chance:
                dmg = s["enemy_strength"] * 0.2
                s["player_health"] = clamp(s["player_health"] - dmg, 0.0, s["player_max_health"])
                s["enemy_confidence"] = clamp(s["enemy_confidence"] + np.random.uniform(0.08, 0.18), 0.0, 1.0)
                s["enemy_anger"] = clamp(s["enemy_anger"] + np.random.uniform(0.02, 0.08), 0.0, 1.0)
            else:
                s["enemy_confidence"] = clamp(s["enemy_confidence"] - 0.03, 0.0, 1.0)
                s["enemy_anger"] = clamp(s["enemy_anger"] - np.random.uniform(0.0, 0.05), 0.0, 1.0)
        else:
            s["enemy_attacking"] = 0
            s["enemy_running"] = 1
            s["enemy_animation_state"] = "running"
            sign = 1.0 if decision == "MOVE_RIGHT" else -1.0
            s["enemy_x"] = clamp(s["enemy_x"] + sign * s["enemy_speed"] * DELTA_TIME, 0.0, SCREEN_WIDTH)
            s["enemy_facing_right"] = sign > 0
            # deriva emocional pasiva
            s["enemy_anger"] = clamp(s["enemy_anger"] + np.random.normal(0, 0.02), 0.0, 1.0)
            s["enemy_fear"] = clamp(s["enemy_fear"] + np.random.normal(0, 0.02), 0.0, 1.0)
            s["enemy_confidence"] = clamp(s["enemy_confidence"] + np.random.normal(0, 0.01), 0.0, 1.0)

        s["enemy_jumping"] = int(np.random.rand() < 0.03)
        s["enemy_y"] = -40.0 if s["enemy_jumping"] else 0.0

        # -------------------- simular al oponente --------------------
        simulate_opponent_step(s)

        new_distance = float(np.round(abs(s["enemy_x"] - s["player_x"]), 2))

        # Daño del oponente al actor (misma condición que Game._update_enemies / _try_hit)
        if s["player_attacking"] == 1 and new_distance <= ATTACK_DISTANCE:
            hit_chance = ENEMY_HIT_CHANCE if s["opponent_kind"] == "enemy" else PLAYER_HIT_CHANCE
            if np.random.rand() < hit_chance:
                dmg = s["player_strength"] * 0.2
                s["enemy_health"] = clamp(s["enemy_health"] - dmg, 0.0, s["enemy_max_health"])
                s["enemy_times_hit"] += 1

                fearless = s["enemy_personality"] in ("ruthless", "merciless")
                s["enemy_fear"] = clamp(
                    s["enemy_fear"] + np.random.uniform(0.10, 0.25) * (0.4 if fearless else 1.0),
                    0.0, 1.0,
                )
                s["enemy_anger"] = clamp(
                    s["enemy_anger"] + np.random.uniform(0.05, 0.20) * ANGER_MULTIPLIER[s["enemy_personality"]] / 1.2,
                    0.0, 1.0,
                )
                s["enemy_confidence"] = clamp(s["enemy_confidence"] - np.random.uniform(0.05, 0.15), 0.0, 1.0)

        # -------------------- comprobar muertes y "reiniciar" el encuentro si hace falta --------------------
        if s["enemy_health"] <= 0:
            s["enemy_dead"] = 1
            s["enemy_animation_state"] = "death"

        if s["player_health"] <= 0:
            s["player_dead"] = 1
            s["player_animation_state"] = "death"

        s["enemy_last_action"] = decision

        if s["enemy_dead"] or s["player_dead"]:
            # simulamos que empieza un nuevo combate dentro de la misma secuencia
            fresh = new_encounter()
            s.update(fresh)

df = pd.DataFrame(rows)

output_dir = Path(__file__).resolve().parent.parent / "datasets"
output_dir.mkdir(parents=True, exist_ok=True)
out_path = output_dir / "dataset_enemies_ml.csv"
df.to_csv(out_path, index=False)

print(f"Archivo '{out_path}' exportado con {len(df)} registros.")
print("Distribución de 'decision':")
print(df["decision"].value_counts(normalize=True))
print("\nDistribución de 'enemy_type':")
print(df["enemy_type"].value_counts(normalize=True))
print("\nDistribución de 'enemy_emotion':")
print(df["enemy_emotion"].value_counts(normalize=True))