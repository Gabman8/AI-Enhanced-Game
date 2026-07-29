import joblib
from pathlib import Path

from AI.ML.enemy_behavior_model import EnemyBehaviorModel


class AIManager:
    # Initialize the AIManager instance with its runtime state.
    def __init__(self, model_name):
        self.model = self._load_model(model_name)

    # Load model from the expected source.
    def _load_model(self, model_name):
        model_path = Path(__file__).resolve().parent.parent / "AI" / "models" / model_name
        saved = joblib.load(model_path)
        return EnemyBehaviorModel(
            pipeline=saved["pipeline"],
            feature_columns=saved["feature_columns"],
        )
