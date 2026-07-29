from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "datasets" / "dataset_level_difficulty.csv"
MODEL_PATH = BASE_DIR / "models" / "level_difficulty_model.pkl"

FEATURE_COLUMNS = [
    "level",
    "enemies_spawned",
    "enemies_killed",
    "player_damage_received",
    "player_health_remaining",
    "player_attacks",
    "player_hits",
    "player_accuracy",
    "time_seconds",
    "times_player_died",
    "times_hit",
]

TARGET_COLUMNS = [
    "enemy_count",
    "strong_enemy_prob",
    "enemy_health_scale",
    "enemy_strength_scale",
    "enemy_speed_scale",
]


class LevelDifficultyModel:
    def __init__(self, pipeline, feature_columns):
        self.pipeline = pipeline
        self.feature_columns = feature_columns

    def predict(self, level_statistics):
        row = pd.DataFrame([level_statistics])[self.feature_columns]
        raw_pred = self.pipeline.predict(row)[0]

        return {
            "enemy_count": max(1, int(round(raw_pred[0]))),
            "strong_enemy_prob": float(np.clip(raw_pred[1], 0.0, 0.9)),
            "enemy_health_scale": float(np.clip(raw_pred[2], 0.7, 1.8)),
            "enemy_strength_scale": float(np.clip(raw_pred[3], 0.7, 1.8)),
            "enemy_speed_scale": float(np.clip(raw_pred[4], 0.7, 1.8)),
        }


def train_level_difficulty_model():
    data = pd.read_csv(DATA_PATH)

    data = data.dropna(subset=FEATURE_COLUMNS + TARGET_COLUMNS)

    X = data[FEATURE_COLUMNS]
    y = data[TARGET_COLUMNS]

    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    preprocessor = ColumnTransformer([
        ("num", numeric_pipeline, FEATURE_COLUMNS),
    ])

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        (
            "regressor",
            MultiOutputRegressor(
                RandomForestRegressor(
                    random_state=42,
                    n_estimators=200,
                    min_samples_split=5,
                    n_jobs=-1,
                )
            ),
        ),
    ])

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    y_test_np = y_test.to_numpy()
    mse = mean_squared_error(y_test_np, y_pred)
    mae = mean_absolute_error(y_test_np, y_pred)

    print("Level difficulty model trained")
    print(f"Test MSE: {mse:.4f}")
    print(f"Test MAE: {mae:.4f}")

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {"pipeline": pipeline, "feature_columns": FEATURE_COLUMNS},
        MODEL_PATH,
    )
    print(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    train_level_difficulty_model()
