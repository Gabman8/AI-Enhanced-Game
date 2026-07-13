import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib

from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# =========================
# 1. DATA LOADING
# =========================

data = pd.read_csv("datasets/dataset_enemies_ml.csv")

data = data.dropna(subset=["decision"])

# =========================
# 2. FEATURES AMD OBJECTIVE
# =========================

feature_columns = [
    'enemy_type',
    'enemy_level',
    'enemy_state',
    'enemy_direction',
    'enemy_speed',
    'player_distance',
    'player_health',
    'player_speed',
    'player_direction',
    'player_running',
    'player_attacking',
    'player_attack_type',
    'player_last_damage_received',
    'player_combo',
    'player_visible',
    'player_noise',
    'player_threat',
    'allies_nearby',
    'enemies_nearby',
    'cover_available',
    'cover_distance',
    'medkit_visible',
    'time_since_last_hit',
    'enemy_last_damage_received',
    'enemy_kills',
    'player_kills',
    'map_area',
    'terrain',
    'time_of_day',
    'weather',
    'health_pct',
    'energy_pct',
    'distance_delta',
    'outnumbered',
    'recent_player_damage',
    'line_of_sight',
    'remaining_cooldown',
    'aggression_score',
    'fear_score',
    'player_dir_x',
    'player_dir_y',
    'time_in_current_state',
    'seconds_since_last_action',
    'actions_last_5_seconds',
    'previous_decision',
]

X = data[feature_columns]
y = data['decision']

# =========================
# 3. TARGET ENCODING
# =========================

label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# =========================
# 4. ONE HOT ENCODING DE FEATURES
# =========================

X = pd.get_dummies(X, drop_first=True)

# =========================
# 5. IMPUTATION
# =========================

imputer = SimpleImputer(strategy="median")
X = pd.DataFrame(
    imputer.fit_transform(X),
    columns=X.columns,
    index=X.index
)

# =========================
# 6. TRAIN / TEST SPLIT
# =========================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y_encoded,
    test_size=0.2,
    random_state=42,
    stratify=y_encoded,
)

# =========================
# 7. MODEL + GRID SEARCH
# =========================

param_grid = {
    "n_estimators": [100, 200],
    "max_depth": [10, 20, None],
    "min_samples_split": [2, 5],
}

grid = GridSearchCV(
    RandomForestClassifier(random_state=42, class_weight="balanced"),
    param_grid,
    cv=3,
    scoring="accuracy",
    n_jobs=-1,
)

grid.fit(X_train, y_train)
model = grid.best_estimator_

print("Mejores parámetros:", grid.best_params_)

# =========================
# 8. PREDICCTION
# =========================

y_pred = model.predict(X_test)

# =========================
# 9. EVALUATION
# =========================

accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.4f}")
print("\nClassification report:\n", classification_report(y_test, y_pred, target_names=label_encoder.classes_))

print("\nConfusion matrix:")
print(confusion_matrix(y_test, y_pred))

# =========================
# 10. CROSS VALIDATION
# =========================

scores = cross_val_score(
    model,
    X_train,
    y_train,
    cv=5,
    scoring="accuracy",
    n_jobs=-1,
)
print(f"Mean CV Accuracy: {scores.mean():.4f}")

# =========================
# 11. Save model
# =========================

joblib.dump(model, "models/enemies.pkl") 
