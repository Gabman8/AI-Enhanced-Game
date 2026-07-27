
from dataclasses import dataclass
import pandas as pd


@dataclass
class BehaviorPrediction:
    decision: str
    emotion: str

    def to_dict(self):
        return {"decision": self.decision, "emotion": self.emotion}


class EnemyBehaviorModel:

    def __init__(self, pipeline, feature_columns):
        self.pipeline = pipeline
        self.feature_columns = feature_columns

    def predict(self, features: dict) -> BehaviorPrediction:
        row = pd.DataFrame([features])[self.feature_columns]
        decision, emotion = self.pipeline.predict(row)[0]
        return BehaviorPrediction(decision=decision, emotion=emotion)

    def predict_batch(self, df: pd.DataFrame):
        df = df[self.feature_columns]
        preds = self.pipeline.predict(df)
        return [BehaviorPrediction(decision=d, emotion=e) for d, e in preds]

    def predict_proba(self, features: dict):
        row = pd.DataFrame([features])[self.feature_columns]
        proba = self.pipeline.predict_proba(row)  # lista: [proba_decision, proba_emotion]
        classes = self.pipeline.named_steps["classifier"].classes_  # lista de arrays
        return {
            "decision": dict(zip(classes[0], proba[0][0])),
            "emotion": dict(zip(classes[1], proba[1][0])),
        }