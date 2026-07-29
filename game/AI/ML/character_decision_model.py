from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    make_scorer,
)
from sklearn.model_selection import GridSearchCV, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "datasets" / "dataset_enemies_ml.csv"
MODEL_PATH = BASE_DIR / "models" / "enemies.pkl"
IMPORTANCE_PLOT_PATH = BASE_DIR / "models" / "feature_importance.png"

# =========================
# 1. DATA LOADING
# =========================

data = pd.read_csv(DATA_PATH)

data = data.dropna(subset=["decision", "enemy_emotion"])

# Un enemigo muerto nunca debería estar pidiendo una decisión: se descartan
data = data[data["enemy_dead"] == 0].copy()

data["player_is_right"] = (data["player_x"] > data["enemy_x"]).astype(int)

# =========================
# 2. FEATURES Y OBJETIVOS
# =========================

CATEGORICAL_FEATURES = [
    "enemy_type",
    "enemy_personality",
    "enemy_animation_state",
    "enemy_last_action",
    "player_animation_state",
]

NUMERIC_FEATURES = [
    "enemy_health",
    "enemy_strength",
    "enemy_speed",
    "enemy_running",
    "enemy_jumping",
    "enemy_attacking",
    "enemy_facing_right",
    "enemy_anger",
    "enemy_fear",
    "enemy_confidence",
    "enemy_times_hit",
    "enemy_times_attack",
    "player_health",
    "player_running",
    "player_jumping",
    "player_attacking",
    "player_facing_right",
    "distance",
    "player_is_right",
]

feature_columns = CATEGORICAL_FEATURES + NUMERIC_FEATURES
TARGET_COLUMNS = ["decision", "enemy_emotion"]

X = data[feature_columns]
y = data[TARGET_COLUMNS]  # CAMBIO: ahora y tiene 2 columnas, no 1

# =========================
# 3. PREPROCESADO (dentro del Pipeline, no manual)
# =========================

numeric_pipeline = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
])

categorical_pipeline = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(handle_unknown="ignore")),
])

preprocessor = ColumnTransformer(transformers=[
    ("num", numeric_pipeline, NUMERIC_FEATURES),
    ("cat", categorical_pipeline, CATEGORICAL_FEATURES),
])

pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("classifier", RandomForestClassifier(random_state=42, class_weight="balanced")),
])

# =========================
# 4. TRAIN / TEST SPLIT
# =========================


strat_key = y["decision"].astype(str) + "|" + y["enemy_emotion"].astype(str)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=strat_key,
)

# =========================
# 5. MODELO + GRID SEARCH
# =========================


# Handle combined accuracy for the current workflow.
def combined_accuracy(y_true, y_pred):
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    acc_decision = (y_true[:, 0] == y_pred[:, 0]).mean()
    acc_emotion = (y_true[:, 1] == y_pred[:, 1]).mean()
    return (acc_decision + acc_emotion) / 2

combined_scorer = make_scorer(combined_accuracy)

param_grid = {
    "classifier__n_estimators": [200],
    "classifier__max_depth": [20],
    "classifier__min_samples_split": [2],
}

grid = GridSearchCV(
    pipeline,
    param_grid,
    cv=3,
    scoring=combined_scorer,
    n_jobs=-1,
)

grid.fit(X_train, y_train)
model = grid.best_estimator_

print("Mejores parámetros:", grid.best_params_)

# =========================
# 6. PREDICCIÓN
# =========================

y_pred = model.predict(X_test)  # array (n_samples, 2): columnas [decision, emotion]
y_pred_decision = y_pred[:, 0]
y_pred_emotion = y_pred[:, 1]

y_test_decision = y_test["decision"]
y_test_emotion = y_test["enemy_emotion"]

# =========================
# 7. EVALUACIÓN (por separado para cada salida)
# =========================

decision_labels = sorted(y["decision"].unique())
emotion_labels = sorted(y["enemy_emotion"].unique())

print(f"\nAccuracy combinada (media decision+emotion): "
      f"{combined_accuracy(y_test.to_numpy(), y_pred):.4f}")

print(f"\nAccuracy decision: {accuracy_score(y_test_decision, y_pred_decision):.4f}")
print(
    "Classification report (decision):\n",
    classification_report(y_test_decision, y_pred_decision, labels=decision_labels),
)
print(f"Confusion matrix (decision), orden = {decision_labels}:")
print(confusion_matrix(y_test_decision, y_pred_decision, labels=decision_labels))

print(f"\nAccuracy emotion: {accuracy_score(y_test_emotion, y_pred_emotion):.4f}")
print(
    "Classification report (emotion):\n",
    classification_report(y_test_emotion, y_pred_emotion, labels=emotion_labels),
)
print(f"Confusion matrix (emotion), orden = {emotion_labels}:")
print(confusion_matrix(y_test_emotion, y_pred_emotion, labels=emotion_labels))

# =========================
# 8. VALIDACIÓN CRUZADA
# =========================

scores = cross_val_score(
    model,
    X_train,
    y_train,
    cv=5,
    scoring=combined_scorer,
    n_jobs=-1,
)
print(f"\nMean CV Accuracy (combinada): {scores.mean():.4f}")

# =========================
# 10. GUARDAR MODELO
# =========================

MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(
    {"pipeline": model, "feature_columns": feature_columns},
    MODEL_PATH,
)
print(f"\nModelo guardado en '{MODEL_PATH}'")
