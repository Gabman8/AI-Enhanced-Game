
from dataclasses import dataclass
import pandas as pd


@dataclass
class BehaviorPrediction:
    decision: str
    emotion: str

    # Convert this object into a plain dictionary representation.
    def to_dict(self):
        return {"decision": self.decision, "emotion": self.emotion}


class EnemyBehaviorModel:

    # Initialize the EnemyBehaviorModel instance with its runtime state.
    def __init__(self, pipeline, feature_columns):
        self.pipeline = pipeline
        self.feature_columns = feature_columns

    # Predict the relevant data from the available inputs.
    def predict(self, features: dict) -> BehaviorPrediction:
        row = pd.DataFrame([features])[self.feature_columns]
        decision, emotion = self.pipeline.predict(row)[0]
        return BehaviorPrediction(decision=decision, emotion=emotion)

    # Predict batch from the available inputs.
    def predict_batch(self, df: pd.DataFrame):
        df = df[self.feature_columns]
        preds = self.pipeline.predict(df)
        return [BehaviorPrediction(decision=d, emotion=e) for d, e in preds]

    # Predict proba from the available inputs.
    def predict_proba(self, features: dict):
        row = pd.DataFrame([features])[self.feature_columns]
        proba = self.pipeline.predict_proba(row)  # lista: [proba_decision, proba_emotion]
        classes = self.pipeline.named_steps["classifier"].classes_  # lista de arrays
        return {
            "decision": dict(zip(classes[0], proba[0][0])),
            "emotion": dict(zip(classes[1], proba[1][0])),
        }
