---
name: ml-deposit-prediction
description: Machine learning models for REE deposit prediction — classification, regression, anomaly detection, and uncertainty quantification using scikit-learn, XGBoost, and probabilistic methods.
---

# Machine Learning for REE Deposit Prediction

## When to use

- You have labeled training data (known mineralized vs. barren locations) and want to predict new targets.
- You want to classify deposit type from geochemical signatures.
- You need to predict grade at unsampled locations using multivariate features.
- You want uncertainty estimates on predictions (critical for resource decisions).

## Problem Types

| Type | Target | Features | Example |
|---|---|---|---|
| **Binary Classification** | Mineralized (1) vs. Barren (0) | Geochem, geophysics, satellite | Target generation |
| **Multi-class Classification** | Deposit type (carbonatite, IAC, hydrothermal, placer) | REE pattern ratios | Prospect ranking |
| **Regression** | TREO grade (% or ppm) | Spatial coords + geochem + remote sensing | Grade interpolation |
| **Anomaly Detection** | Outlier = potential target | All multivariate features | Greenfield exploration |
| **Clustering** | Groups of similar geochemical signatures | REE + pathfinder elements | Domain definition |

## Feature Engineering for REE

### Essential Features
```python
# REE pattern ratios
features['La_Nd_ratio'] = df['La_ppm'] / df['Nd_ppm']
features['HREO_TREO'] = df[['Gd','Tb','Dy','Ho','Er','Tm','Yb','Lu','Y']].sum(axis=1) / df[ree_elements].sum(axis=1)
features['Ce_anomaly'] = df['Ce_ppm'] / np.sqrt(df['La_ppm'] * df['Pr_ppm'])
features['Eu_anomaly'] = df['Eu_ppm'] / np.sqrt(df['Sm_ppm'] * df['Gd_ppm'])
features['Y_Ho_ratio'] = df['Y_ppm'] / df['Ho_ppm']  # Y/Ho ≈ 28 in seawater, different in magmatic

# Pathfinder elements
features['Th_U_ratio'] = df['Th_ppm'] / df['U_ppm']
features['Nb_Ta_ratio'] = df['Nb_ppm'] / df['Ta_ppm']
features['Zr_Hf_ratio'] = df['Zr_ppm'] / df['Hf_ppm']

# Spatial features
features['dist_to_fault'] = distance_to_nearest_fault(df[['X','Y']], fault_lines)
features['dist_to_intrusion'] = distance_to_nearest(df[['X','Y']], intrusion_boundary)
features['elevation'] = get_elevation(df[['X','Y']])
features['slope'] = calculate_slope(dem, df[['X','Y']])

# Remote sensing features
features['iron_oxide'] = sample_raster('iron_oxide.tif', df[['X','Y']])
features['clay_index'] = sample_raster('clay_index.tif', df[['X','Y']])
features['magnetic_anomaly'] = sample_raster('mag_tmi.tif', df[['X','Y']])
features['radiometric_th'] = sample_raster('rad_th.tif', df[['X','Y']])
```

### Chondrite-Normalized Pattern Features
```python
chondrite_values = {
    'La': 0.237, 'Ce': 0.612, 'Pr': 0.095, 'Nd': 0.467,
    'Sm': 0.153, 'Eu': 0.058, 'Gd': 0.205, 'Tb': 0.037,
    'Dy': 0.254, 'Ho': 0.057, 'Er': 0.166, 'Tm': 0.026,
    'Yb': 0.165, 'Lu': 0.025, 'Y': 1.57
}

for elem in ree_elements:
    features[f'{elem}_cn'] = df[f'{elem}_ppm'] / chondrite_values[elem]

# Pattern shape descriptors
features['LREE_slope'] = (features['La_cn'] - features['Sm_cn']) / 4
features['HREE_slope'] = (features['Gd_cn'] - features['Lu_cn']) / 7
features['MREE_bulge'] = features['Eu_cn'] / ((features['Sm_cn'] + features['Gd_cn']) / 2)
```

## Model Selection

| Model | Pros | Cons | Best For |
|---|---|---|---|
| **Random Forest** | Handles non-linearity, feature importance, robust | Can overfit, no uncertainty | Baseline, feature selection |
| **XGBoost / LightGBM** | State-of-art accuracy, fast, regularized | Hyperparameter tuning needed | Production predictions |
| **Support Vector Machine** | Good with few samples, kernel tricks | Slow at scale, black box | Small datasets |
| **Logistic Regression** | Interpretable coefficients, probabilities | Linear only | Benchmark, interpretability |
| **Gaussian Process** | Native uncertainty, probabilistic | O(n³) scaling, slow | Uncertainty-critical decisions |
| **Neural Network (MLP)** | Captures complex interactions | Needs lots of data, black box | Large multivariate datasets |
| **Isolation Forest** | Unsupervised anomaly detection | No probabilities natively | Greenfield target generation |

## Training Pipeline

```python
import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import joblib

# Load data
X = pd.read_csv('features.csv')
y = pd.read_csv('labels.csv')['mineralized']  # 1 = mineralized, 0 = barren

# Train-test split (spatial — not random!)
from sklearn.model_selection import GroupShuffleSplit
groups = X[' geological_domain']  # Never split across domains
splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42)
train_idx, test_idx = next(splitter.split(X, y, groups))

X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

# Scale
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Random Forest
rf = RandomForestClassifier(
    n_estimators=500,
    max_depth=12,
    min_samples_leaf=5,
    class_weight='balanced',  # Critical if mineralized samples are rare
    random_state=42,
    n_jobs=-1
)
rf.fit(X_train, y_train)

# Evaluation
y_pred = rf.predict(X_test)
y_proba = rf.predict_proba(X_test)[:, 1]

print(classification_report(y_test, y_pred))
print(f"ROC-AUC: {roc_auc_score(y_test, y_proba):.3f}")

# Feature importance
importances = pd.Series(rf.feature_importances_, index=X.columns)
print(importances.sort_values(ascending=False).head(15))
```

## XGBoost (Recommended for Production)

```python
# Handle class imbalance with scale_pos_weight
scale_pos_weight = len(y_train[y_train==0]) / len(y_train[y_train==1])

xgb_model = xgb.XGBClassifier(
    n_estimators=1000,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=scale_pos_weight,
    eval_metric='auc',
    early_stopping_rounds=50,
    random_state=42
)

xgb_model.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    verbose=False
)

# Save model
joblib.dump(xgb_model, 'ree_deposit_classifier.pkl')
joblib.dump(scaler, 'feature_scaler.pkl')
```

## Uncertainty Quantification

### Monte Carlo Dropout (for Neural Networks)
```python
import tensorflow as tf

# Enable dropout at inference time
model = tf.keras.Sequential([
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(64, activation='relu'),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(1, activation='sigmoid')
])

# Run T forward passes
T = 100
predictions = np.array([model(X_test, training=True) for _ in range(T)])
mean_pred = predictions.mean(axis=0)
uncertainty = predictions.std(axis=0)
```

### Conformal Prediction (Model-agnostic)
```python
from nonconformist.cp import IcpClassifier
from nonconformist.nc import NcFactory

nc = NcFactory.create_nc(rf)
icp = IcpClassifier(nc)

icp.calibrate(X_calib, y_calib)
prediction_sets = icp.predict(X_test, significance=0.1)
# prediction_sets contains sets of labels with 90% coverage guarantee
```

## Deposit Type Classification

```python
deposit_types = ['carbonatite', 'ion_adsorption', 'hydrothermal_hree', 'placer_monazite', 'barren']

# Multi-class XGBoost
xgb_multi = xgb.XGBClassifier(
    objective='multi:softprob',
    num_class=5,
    n_estimators=1000,
    max_depth=8,
    learning_rate=0.05
)

xgb_multi.fit(X_train, y_type_train)

# Predict with probabilities
probs = xgb_multi.predict_proba(X_new)
type_pred = deposit_types[np.argmax(probs)]
confidence = np.max(probs)

# Only report if confidence > 0.7
if confidence < 0.7:
    type_pred = "uncertain"
```

## Greenfield Anomaly Detection

```python
from sklearn.ensemble import IsolationForest

# Train only on "background" / barren samples
background = X[y == 0]

iso = IsolationForest(
    n_estimators=500,
    contamination=0.05,  # Expect 5% anomalies
    random_state=42
)
iso.fit(background)

# Score new samples
anomaly_scores = iso.decision_function(X_new)
# Negative = more anomalous = potential target
```

## Best Practices

1. **Spatial cross-validation:** Never random split. Use spatial blocks or geological domains.
2. **Class imbalance:** Mineralized samples are rare. Use `class_weight='balanced'`, SMOTE, or scale_pos_weight.
3. **Leakage prevention:** Don't include target-derived features (e.g., TREO if predicting mineralization).
4. **Feature correlation:** Remove highly correlated features (r > 0.95) to reduce multicollinearity.
5. **Geological plausibility:** ML finds patterns, but geological sense-checks are mandatory.
6. **Ensemble:** Combine RF + XGBoost + SVM predictions for robustness.
7. **Threshold tuning:** Don't use 0.5 default. Tune threshold for precision vs. recall based on exploration budget.

## Model Monitoring

Track these in production:
- Prediction drift (feature distributions changing)
- Concept drift (mineralization controls changing with depth/laterally)
- Calibration (predicted probabilities matching observed frequencies)
