"""Week 6A customer credit-risk analysis.

Run this file in VS Code or Jupyter. Put the source workbook in the same
folder as this script, or change INPUT_FILE below.

The script:
1. Removes records missing saving/checking account values.
2. Creates age_group, with age 65 classified as Senior.
3. Encodes the requested categorical variables.
4. Fits a decision tree, logistic regression, and neural network.
5. Saves diagnostic text, confusion matrices, ROC curves, and an Excel file.
"""

from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.special import expit
from scipy.optimize import minimize
from scipy.stats import norm

from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (
    confusion_matrix,
    ConfusionMatrixDisplay,
    roc_curve,
    roc_auc_score,
)
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

warnings.filterwarnings("ignore")

# Change this only if the workbook is not beside this Python file.
BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "Week 6A data.xlsx"
if not INPUT_FILE.exists():
    # This fallback is useful when the uploaded workbook is kept in a
    # project_sources folder. Users can still place the workbook beside the
    # script when running it on their own computer.
    uploaded_copy = BASE_DIR / "project_sources" / "01-Week-6A-data.xlsx"
    if uploaded_copy.exists():
        INPUT_FILE = uploaded_copy
OUTPUT_DIR = BASE_DIR / "week6a_outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

RANDOM_STATE = 42


def make_age_group(age):
    # 65 is intentionally included in Senior, as requested.
    if age < 18:
        return 0
    if age <= 25:
        return 1
    if age <= 35:
        return 2
    if age <= 50:
        return 3
    if age <= 64:
        return 4
    return 5


def preprocess_data():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Could not find {INPUT_FILE}. Put 'Week 6A data.xlsx' beside this script."
        )

    raw = pd.read_excel(INPUT_FILE)
    required = {
        "customer_id", "risk level", "age", "gender", "housing",
        "saving acc", "checking acc", "loan purpose"
    }
    missing_columns = required - set(raw.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    id_count = raw["customer_id"].nunique()
    if id_count != len(raw):
        raise ValueError("customer_id is not unique. The script stopped for review.")

    # Remove incomplete account records, as requested. No account value is imputed.
    clean = raw.dropna(subset=["saving acc", "checking acc"]).copy()
    clean["age_group"] = clean["age"].apply(make_age_group)

    mappings = {
        "risk level": {"low": 0, "high": 1},
        "gender": {"female": 0, "male": 1},
        "housing": {"no housing": 0, "rented": 1, "own": 2},
        "saving acc": {"unknown": 0, "small": 1, "average": 2, "rich": 3, "quite rich": 4},
        "checking acc": {"unknown": 0, "small": 1, "average": 2, "rich": 4},
    }
    for column, mapping in mappings.items():
        clean[column] = clean[column].map(mapping)
        if clean[column].isna().any():
            raise ValueError(f"An unmapped value exists in column '{column}'.")

    clean["risk level"] = clean["risk level"].astype(int)
    for column in ["gender", "housing", "saving acc", "checking acc", "age_group"]:
        clean[column] = clean[column].astype(int)

    output_file = OUTPUT_DIR / "Week 6A data_preprocessed.xlsx"
    clean.to_excel(output_file, index=False)
    return raw, clean, output_file, id_count


def sigmoid_fit(X, y):
    """Fit an unregularized logistic model for diagnostic calculations."""
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)

    def objective(beta):
        z = X @ beta
        return np.sum(np.logaddexp(0, z) - y * z)

    result = minimize(objective, np.zeros(X.shape[1]), method="BFGS")
    beta = result.x
    p = expit(X @ beta)
    W = p * (1 - p)
    covariance = np.linalg.pinv(X.T @ (W[:, None] * X))
    return beta, p, covariance


def calculate_vif(X):
    X = np.asarray(X, dtype=float)
    values = []
    for i in range(X.shape[1]):
        y = X[:, i]
        others = np.delete(X, i, axis=1)
        design = np.column_stack([np.ones(len(X)), others])
        fitted = design @ np.linalg.lstsq(design, y, rcond=None)[0]
        ss_res = np.sum((y - fitted) ** 2)
        ss_tot = np.sum((y - y.mean()) ** 2)
        r2 = 0 if ss_tot == 0 else 1 - ss_res / ss_tot
        values.append(np.inf if r2 >= 1 else 1 / (1 - r2))
    return values


def logistic_diagnostics(clean):
    features = ["age_group", "gender", "housing", "saving acc", "checking acc"]
    X0 = clean[features].astype(float).to_numpy()
    y = clean["risk level"].astype(int).to_numpy()
    X = np.column_stack([np.ones(len(clean)), X0])
    beta, p, covariance = sigmoid_fit(X, y)

    # Linearity in the logit: Box-Tidwell-style interaction for age_group.
    age_shifted = clean["age_group"].to_numpy(float) + 1
    interaction = age_shifted * np.log(age_shifted)
    X_bt = np.column_stack([X, interaction])
    beta_bt, _, cov_bt = sigmoid_fit(X_bt, y)
    se_bt = np.sqrt(max(cov_bt[-1, -1], 0))
    z_bt = beta_bt[-1] / se_bt if se_bt else np.nan
    p_bt = 2 * norm.sf(abs(z_bt)) if np.isfinite(z_bt) else np.nan

    # VIF for the five model predictors. Intercept is excluded.
    vifs = calculate_vif(X0)
    max_vif = max(vifs)

    # Approximate logistic Cook's distance using the fitted weighted-least-
    # squares influence formula.
    W = p * (1 - p)
    hat = np.diag(np.sqrt(W)[:, None] * X @ covariance @ X.T * np.sqrt(W)[None, :])
    deviance_resid = np.sign(y - p) * np.sqrt(
        2 * np.where(
            y == 1,
            np.log(np.maximum(1 / p, 1)),
            np.log(np.maximum(1 / (1 - p), 1)),
        )
    )
    cooks = (deviance_resid ** 2 * hat) / (X.shape[1] * np.maximum((1 - hat) ** 2, 1e-12))
    cook_threshold = 4 / len(clean)
    influential_count = int(np.sum(cooks > cook_threshold))

    events = int(y.sum())
    predictors = len(features)
    epv = events / predictors

    lines = [
        "LOGISTIC REGRESSION DIAGNOSTICS",
        f"Complete records used: {len(clean)}",
        f"High-risk events: {events}",
        "",
        "Independence of errors: NEEDS REVIEW",
        "Evidence: customer_id is unique for every original record and no customer is repeated; this supports one row per customer but does not prove independence of all observations.",
        "",
        ("Linearity in the logit: NEEDS REVIEW" if not np.isfinite(p_bt) or p_bt < 0.05 else "Linearity in the logit: MET"),
        f"Evidence: Box-Tidwell-style age_group interaction p-value = {p_bt:.6g}; age_group is grouped/ordinal, so this result should be interpreted cautiously.",
        "",
        ("Multicollinearity: MET" if max_vif < 5 else "Multicollinearity: NEEDS REVIEW"),
        "Evidence: calculated VIF values were " + ", ".join(f"{f}={v:.3f}" for f, v in zip(features, vifs)) + "; the largest VIF was " + f"{max_vif:.3f}.",
        "",
        ("Influential outliers: MET" if influential_count == 0 else "Influential outliers: NEEDS REVIEW"),
        f"Evidence: approximate Cook's distance used the 4/n threshold of {cook_threshold:.6f}; {influential_count} record(s) exceeded the threshold and the maximum Cook's distance was {cooks.max():.6f}.",
        "",
        ("Events per predictor: MET" if epv >= 20 else "Events per predictor: NEEDS REVIEW" if epv >= 10 else "Events per predictor: NOT MET"),
        f"Evidence: {events} high-risk events / {predictors} predictors = {epv:.2f} events per predictor, above the commonly recommended 10–20 range.",
    ]
    diagnostic_file = OUTPUT_DIR / "logistic_regression_diagnostics.txt"
    diagnostic_file.write_text("\n".join(lines), encoding="utf-8")
    return diagnostic_file, lines


def save_confusion_matrix(model_name, y_true, y_pred):
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    fig, ax = plt.subplots(figsize=(5, 4))
    ConfusionMatrixDisplay(cm, display_labels=["Low (0)", "High (1)"]).plot(ax=ax, cmap="Blues", colorbar=False)
    ax.set_title(f"{model_name} Confusion Matrix")
    fig.tight_layout()
    path = OUTPUT_DIR / f"{model_name.lower().replace(' ', '_')}_confusion_matrix.png"
    fig.savefig(path, dpi=200)
    plt.close(fig)
    return path


def run_models(clean):
    # The same stratified 60/40 split is used for all models.
    indices = np.arange(len(clean))
    train_idx, test_idx = train_test_split(
        indices,
        test_size=0.40,
        random_state=RANDOM_STATE,
        stratify=clean["risk level"],
    )
    y = clean["risk level"].to_numpy()

    tree_features = ["age", "gender", "housing", "saving acc", "checking acc"]
    logistic_features = ["age_group", "gender", "housing", "saving acc", "checking acc"]

    models = [
        ("Decision Tree", tree_features, DecisionTreeClassifier(random_state=RANDOM_STATE)),
        ("Logistic Regression", logistic_features, LogisticRegression(max_iter=2000, random_state=RANDOM_STATE)),
        ("Neural Network", logistic_features, make_pipeline(StandardScaler(), MLPClassifier(hidden_layer_sizes=(10,), max_iter=2000, random_state=RANDOM_STATE))),
    ]

    roc_data = []
    summary = []
    for name, features, model in models:
        X = clean[features].astype(float).to_numpy()
        model.fit(X[train_idx], y[train_idx])
        pred = model.predict(X[test_idx])
        probability = model.predict_proba(X[test_idx])[:, 1]
        cm_path = save_confusion_matrix(name, y[test_idx], pred)
        auc = roc_auc_score(y[test_idx], probability)
        fpr, tpr, _ = roc_curve(y[test_idx], probability)
        roc_data.append((name, fpr, tpr, auc))
        summary.append({"model": name, "test_records": len(test_idx), "accuracy": np.mean(pred == y[test_idx]), "roc_auc": auc, "confusion_matrix_file": cm_path.name})

    fig, ax = plt.subplots(figsize=(7, 5))
    for name, fpr, tpr, auc in roc_data:
        ax.plot(fpr, tpr, linewidth=2, label=f"{name} (AUC={auc:.3f})")
    ax.plot([0, 1], [0, 1], "k--", linewidth=1)
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curves: Customer Credit-Risk Models")
    ax.legend()
    fig.tight_layout()
    roc_path = OUTPUT_DIR / "three_model_roc_curves.png"
    fig.savefig(roc_path, dpi=200)
    plt.close(fig)

    pd.DataFrame(summary).to_csv(OUTPUT_DIR / "model_summary.csv", index=False)
    return len(train_idx), len(test_idx), roc_path


def main():
    raw, clean, preprocessed_file, unique_ids = preprocess_data()
    diagnostic_file, diagnostic_lines = logistic_diagnostics(clean)
    train_n, test_n, roc_path = run_models(clean)
    run_summary = [
        f"Input records: {len(raw)}",
        f"Unique customer IDs: {unique_ids}",
        f"Complete records retained: {len(clean)}",
        f"Records removed for missing saving/checking values: {len(raw) - len(clean)}",
        f"Training records: {train_n}",
        f"Testing records: {test_n}",
        f"Preprocessed workbook: {preprocessed_file.name}",
        f"ROC plot: {roc_path.name}",
        "",
        *diagnostic_lines,
    ]
    (OUTPUT_DIR / "run_summary.txt").write_text("\n".join(run_summary), encoding="utf-8")
    print("Completed. Outputs saved in:", OUTPUT_DIR)
    for item in sorted(OUTPUT_DIR.iterdir()):
        print(item.name)


if __name__ == "__main__":
    main()
