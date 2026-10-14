import json
from importlib import import_module
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
AI_DIR = BASE_DIR.parent / "AI"
MODELS_DIR = AI_DIR / "models"
STATE_PATH = MODELS_DIR / "level_difficulty_state.json"
MODEL_NAME = "level_difficulty_model.pkl"


# Clamp a value so it stays inside the allowed range.
def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


class DifficultyAdjuster:
    # Initialize the DifficultyAdjuster instance with its runtime state.
    def __init__(self, model_name=MODEL_NAME, state_path=STATE_PATH):
        self.model = self._load_model(model_name)
        self.state_path = Path(state_path)
        self.state = self._load_state()

    # Load model from the expected source.
    def _load_model(self, model_name):
        model_path = MODELS_DIR / model_name
        if not model_path.exists():
            return None

        try:
            import joblib

            saved = joblib.load(model_path)
            model_type = import_module("AI.ML.level_difficulty_model").LevelDifficultyModel
            return model_type(
                pipeline=saved["pipeline"],
                feature_columns=saved["feature_columns"],
            )
        except Exception as exc:
            print(f"[Difficulty] Could not load model '{model_name}': {exc}. Using fallback scaler.")
            return None

    # Load state from the expected source.
    def _load_state(self):
        if not self.state_path.exists():
            return {
                "current_level": 1,
                "skill_estimate": 0.55,
                "history": [],
                "last_stats": None,
            }
        try:
            with open(self.state_path, "r", encoding="utf-8") as handle:
                return json.load(handle)
        except Exception:
            return {
                "current_level": 1,
                "skill_estimate": 0.55,
                "history": [],
                "last_stats": None,
            }

    # Save state to the expected destination.
    def _save_state(self):
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_path, "w", encoding="utf-8") as handle:
            json.dump(self.state, handle, indent=2)

    # Handle performance signal for the current workflow.
    def _performance_signal(self, stats):
        if stats is None:
            return self.state.get("skill_estimate", 0.55)
        accuracy = stats.get("player_accuracy", 0.0)
        health_remain = stats.get("player_health_remaining", 0.0) / 100.0
        deaths = stats.get("times_player_died", 0)
        basic = 0.5 * accuracy + 0.3 * health_remain + 0.2 * (1.0 if deaths == 0 else 0.0)
        return clamp(basic, 0.05, 0.98)

    # Handle level progression floor for the current workflow.
    def _level_progression_floor(self, level):
        # Ensure difficulty rises with level even when ML output is noisy.
        lvl = max(1, int(level))
        return {
            "enemy_count": min(16, 2 + (lvl // 2)),
            "strong_enemy_prob": clamp(0.10 + (lvl - 1) * 0.05, 0.10, 0.92),
            "enemy_health_scale": clamp(0.85 + (lvl - 1) * 0.06, 0.85, 1.95),
            "enemy_strength_scale": clamp(0.85 + (lvl - 1) * 0.065, 0.85, 2.0),
            "enemy_speed_scale": clamp(0.90 + (lvl - 1) * 0.025, 0.90, 1.55),
        }

    # Handle suggest level config for the current workflow.
    def suggest_level_config(self, level, previous_stats=None):
        self.state["current_level"] = level
        if previous_stats is not None:
            self.state["last_stats"] = previous_stats

        level = max(1, int(level))
        performance = self._performance_signal(previous_stats)
        floor_cfg = self._level_progression_floor(level)

        if self.model is not None and previous_stats is not None:
            try:
                config = self.model.predict({**previous_stats, "level": level})
                config = {
                    key: float(config[key]) if key != "enemy_count" else int(round(config[key]))
                    for key in config
                }
                config["enemy_count"] = int(clamp(max(config["enemy_count"], floor_cfg["enemy_count"]), 1, 16))
                config["strong_enemy_prob"] = clamp(max(config["strong_enemy_prob"], floor_cfg["strong_enemy_prob"]), 0.08, 0.95)
                config["enemy_health_scale"] = clamp(max(config["enemy_health_scale"], floor_cfg["enemy_health_scale"]), 0.75, 2.0)
                config["enemy_strength_scale"] = clamp(max(config["enemy_strength_scale"], floor_cfg["enemy_strength_scale"]), 0.75, 2.1)
                config["enemy_speed_scale"] = clamp(max(config["enemy_speed_scale"], floor_cfg["enemy_speed_scale"]), 0.80, 1.6)

                # Final boss behavior for late game: guaranteed every 5th level from 10 onward.
                if level >= 10:
                    config["boss_spawn_chance"] = clamp(0.15 + (level - 10) * 0.05, 0.15, 0.5)
                    config["force_final_boss"] = (level % 5 == 0)
                else:
                    config["boss_spawn_chance"] = 0.0
                    config["force_final_boss"] = False
                return config
            except Exception:
                pass

        difficulty_bias = clamp((performance - 0.5) * 0.6, -0.3, 0.3)
        enemy_count = max(1, int(round(2 + (level - 1) * 0.5 + (performance - 0.5) * 2.0)))
        fallback = {
            "enemy_count": clamp(enemy_count, 1, 16),
            "strong_enemy_prob": clamp(0.12 + difficulty_bias * 0.25 + (level - 1) * 0.03, 0.08, 0.90),
            "enemy_health_scale": clamp(0.80 + performance * 0.15 + (level - 1) * 0.025, 0.75, 1.90),
            "enemy_strength_scale": clamp(0.75 + performance * 0.15 + (level - 1) * 0.03, 0.75, 2.0),
            "enemy_speed_scale": clamp(0.90 + difficulty_bias * 0.15 + (level - 1) * 0.015, 0.85, 1.55),
        }

        fallback["enemy_count"] = int(max(fallback["enemy_count"], floor_cfg["enemy_count"]))
        fallback["strong_enemy_prob"] = max(fallback["strong_enemy_prob"], floor_cfg["strong_enemy_prob"])
        fallback["enemy_health_scale"] = max(fallback["enemy_health_scale"], floor_cfg["enemy_health_scale"])
        fallback["enemy_strength_scale"] = max(fallback["enemy_strength_scale"], floor_cfg["enemy_strength_scale"])
        fallback["enemy_speed_scale"] = max(fallback["enemy_speed_scale"], floor_cfg["enemy_speed_scale"])
        fallback["boss_spawn_chance"] = clamp(0.15 + (level - 10) * 0.05, 0.15, 0.5) if level >= 10 else 0.0
        fallback["force_final_boss"] = level >= 10 and (level % 5 == 0)
        return fallback

    # Record level result in the stored state.
    def record_level_result(self, stats):
        if stats is None:
            return

        performance = self._performance_signal(stats)
        previous_skill = self.state.get("skill_estimate", 0.55)
        self.state["skill_estimate"] = clamp(previous_skill * 0.75 + performance * 0.25, 0.05, 0.98)
        self.state["last_stats"] = stats
        self.state["current_level"] = stats["level"] + (1 if stats.get("level_passed", 1) else 0)
        self.state.setdefault("history", []).append(
            {
                "level": stats["level"],
                "passed": bool(stats.get("level_passed", 1)),
                "performance": round(performance, 3),
                "stats": stats,
            }
        )
        self._save_state()

    # Return current level for the current flow.
    def get_current_level(self):
        return int(self.state.get("current_level", 1))

    # Handle reset state for the current workflow.
    def reset_state(self):
        self.state = {
            "current_level": 1,
            "skill_estimate": 0.55,
            "history": [],
            "last_stats": None,
        }
        self._save_state()

    # Return state for the current flow.
    def get_state(self):
        return self.state
