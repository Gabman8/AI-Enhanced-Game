import json
from pathlib import Path

import joblib
import numpy as np

from AI.ML.level_difficulty_model import LevelDifficultyModel

BASE_DIR = Path(__file__).resolve().parent
AI_DIR = BASE_DIR.parent / "AI"
MODELS_DIR = AI_DIR / "models"
STATE_PATH = MODELS_DIR / "level_difficulty_state.json"
MODEL_NAME = "level_difficulty_model.pkl"


def clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))


class DifficultyAdjuster:
    def __init__(self, model_name=MODEL_NAME, state_path=STATE_PATH):
        self.model = self._load_model(model_name)
        self.state_path = Path(state_path)
        self.state = self._load_state()

    def _load_model(self, model_name):
        model_path = MODELS_DIR / model_name
        if not model_path.exists():
            return None

        saved = joblib.load(model_path)
        return LevelDifficultyModel(
            pipeline=saved["pipeline"],
            feature_columns=saved["feature_columns"],
        )

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

    def _save_state(self):
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_path, "w", encoding="utf-8") as handle:
            json.dump(self.state, handle, indent=2)

    def _performance_signal(self, stats):
        if stats is None:
            return self.state.get("skill_estimate", 0.55)
        accuracy = stats.get("player_accuracy", 0.0)
        health_remain = stats.get("player_health_remaining", 0.0) / 100.0
        deaths = stats.get("times_player_died", 0)
        basic = 0.5 * accuracy + 0.3 * health_remain + 0.2 * (1.0 if deaths == 0 else 0.0)
        return clamp(basic, 0.05, 0.98)

    def suggest_level_config(self, level, previous_stats=None):
        self.state["current_level"] = level
        if previous_stats is not None:
            self.state["last_stats"] = previous_stats

        performance = self._performance_signal(previous_stats)

        if self.model is not None and previous_stats is not None:
            try:
                config = self.model.predict({**previous_stats, "level": level})
                config = {
                    key: float(config[key]) if key != "enemy_count" else int(round(config[key]))
                    for key in config
                }
                config["enemy_count"] = clamp(config["enemy_count"], 1, 14)
                config["strong_enemy_prob"] = clamp(config["strong_enemy_prob"], 0.05, 0.85)
                config["enemy_health_scale"] = clamp(config["enemy_health_scale"], 0.75, 1.8)
                config["enemy_strength_scale"] = clamp(config["enemy_strength_scale"], 0.75, 1.8)
                config["enemy_speed_scale"] = clamp(config["enemy_speed_scale"], 0.75, 1.8)
                return config
            except Exception:
                pass

        difficulty_bias = clamp((performance - 0.5) * 0.6, -0.3, 0.3)
        enemy_count = max(1, int(round(2 + (level - 1) * 0.5 + (performance - 0.5) * 2.0)))
        return {
            "enemy_count": clamp(enemy_count, 1, 10),
            "strong_enemy_prob": clamp(0.12 + difficulty_bias * 0.25 + (level - 1) * 0.025, 0.05, 0.70),
            "enemy_health_scale": clamp(0.80 + performance * 0.15 + (level - 1) * 0.015, 0.70, 1.50),
            "enemy_strength_scale": clamp(0.75 + performance * 0.15 + (level - 1) * 0.02, 0.70, 1.60),
            "enemy_speed_scale": clamp(0.90 + difficulty_bias * 0.15 + (level - 1) * 0.01, 0.80, 1.35),
        }

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

    def get_current_level(self):
        return int(self.state.get("current_level", 1))

    def reset_state(self):
        self.state = {
            "current_level": 1,
            "skill_estimate": 0.55,
            "history": [],
            "last_stats": None,
        }
        self._save_state()

    def get_state(self):
        return self.state
