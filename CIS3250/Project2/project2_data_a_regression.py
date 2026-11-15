"""One OLS model: Global_Sales ~ NA_Sales + Year + Publisher + Genre + Platform.
Run from any directory. Numeric results only; requires requirements-project2.txt.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import linalg, stats
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from threadpoolctl import threadpool_limits

BASE = Path(__file__).resolve().parent
DATA_PATH = BASE / "Project2.1data-1.xlsx"
OUTPUT_DIR = BASE / "project2_data_a_outputs"
NUMERIC = ["NA_Sales", "Year"]
CATEGORICAL = ["Publisher", "Genre", "Platform"]
SEED = 42


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    raw = pd.read_excel(DATA_PATH)
    df = raw.copy()
    for col in NUMERIC + ["Global_Sales"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in CATEGORICAL:
        df[col] = df[col].replace(r"^\s*$", np.nan, regex=True)
    df = df.replace([np.inf, -np.inf], np.nan).dropna(subset=NUMERIC + CATEGORICAL + ["Global_Sales"])
    df.to_csv(OUTPUT_DIR / "data_a_cleaned.csv", index=False)
    train, test = train_test_split(np.arange(len(df)), test_size=.2, random_state=SEED)
    frames = [df[NUMERIC].reset_index(drop=True)]
    groups = {c: c for c in NUMERIC}
    references, unknowns = [], []
    for col in CATEGORICAL:
        values = df[col].astype(str).reset_index(drop=True)
        counts = values.iloc[train].value_counts()
        reference = counts.index[0]
        levels = [reference] + sorted(set(counts.index) - {reference})
        references.append({"variable": col, "reference_category": reference, "training_levels": len(levels)})
        unknowns.append(f"{col}: {int((~values.iloc[test].isin(levels)).sum())} test rows with unseen levels (coded as reference)")
        dummy = pd.DataFrame({f"{col}={level}": (values == level).astype(float) for level in levels[1:]})
        groups.update({name: col for name in dummy.columns})
        frames.append(dummy)
    X = pd.concat(frames, axis=1).astype(float)
    means, sd = X.iloc[train].mean(), X.iloc[train].std(ddof=0)
    usable = sd[sd > 0].index
    X, means, sd = X[usable], means[usable], sd[usable]
    Z = ((X - means) / sd).to_numpy()
    # Remove exact aliases so inference uses the actual design rank.
    _, R, pivot = linalg.qr(Z[train], mode="economic", pivoting=True)
    tolerance = np.finfo(float).eps * max(Z[train].shape) * abs(R[0, 0])
    rank = int((np.abs(np.diag(R)) > tolerance).sum())
    keep = sorted(pivot[:rank])
    dropped = [str(X.columns[i]) for i in range(X.shape[1]) if i not in keep]
    X, means, sd, Z = X.iloc[:, keep], means.iloc[keep], sd.iloc[keep], Z[:, keep]
    y = df.Global_Sales.to_numpy(float)
    design = np.column_stack([np.ones(len(train)), Z[train]])
    U, s, Vt = linalg.svd(design, full_matrices=False)
    b_scaled = Vt.T @ ((U.T @ y[train]) / s)
    prediction = b_scaled[0] + Z @ b_scaled[1:]
    residual = y[train] - prediction[train]
    n, p = design.shape
    dof = n - p
    sse = residual @ residual
    sst = np.sum((y[train] - y[train].mean()) ** 2)
    r2 = 1 - sse / sst
    adj = 1 - (1 - r2) * (n - 1) / dof
    f = ((sst - sse) / (p - 1)) / (sse / dof)
    fp = stats.f.sf(f, p - 1, dof)
    covariance = (Vt.T / s**2) @ Vt * (sse / dof)
    transform = np.zeros((p, p))
    transform[0, 0] = 1
    transform[0, 1:] = -means.to_numpy() / sd.to_numpy()
    transform[1:, 1:] = np.diag(1 / sd.to_numpy())
    b = transform @ b_scaled
    se = np.sqrt(np.maximum(np.diag(transform @ covariance @ transform.T), 0))
    t = b / se
    pv = 2 * stats.t.sf(abs(t), dof)
    beta = np.r_[np.nan, b_scaled[1:] / y[train].std(ddof=0)]
    coefficients = pd.DataFrame({"predictor": ["Intercept"] + list(X.columns),
        "B_unstandardized": b, "Beta_standardized": beta, "standard_error": se,
        "t_value": t, "p_value": pv, "significant_at_0.05_unadjusted": pv < .05})
    coefficients.to_csv(OUTPUT_DIR / "data_a_all_coefficients.csv", index=False)
    weights = coefficients.iloc[1:].assign(abs_standardized_beta=lambda d: d.Beta_standardized.abs()).sort_values("abs_standardized_beta", ascending=False)
    weights.to_csv(OUTPUT_DIR / "data_a_standardized_feature_weights.csv", index=False)
    # Permute each original variable as a group, keeping its dummies together.
    rng = np.random.default_rng(SEED)
    baseline = r2_score(y[test], prediction[test])
    importance = []
    for group in NUMERIC + CATEGORICAL:
        mask = np.array([groups[c] == group for c in X.columns])
        contribution = Z[test][:, mask] @ b_scaled[1:][mask]
        decreases = [baseline - r2_score(y[test], prediction[test] - contribution + contribution[rng.permutation(len(test))]) for _ in range(20)]
        importance.append({"feature": group, "test_R2_decrease_mean": np.mean(decreases), "test_R2_decrease_sd": np.std(decreases)})
    importance = pd.DataFrame(importance).sort_values("test_R2_decrease_mean", ascending=False)
    importance.to_csv(OUTPUT_DIR / "data_a_feature_importance.csv", index=False)
    metrics = pd.DataFrame([{"model": "Single_OLS", "n_original": len(raw), "n_cleaned": len(df),
        "n_train": n, "n_test": len(test), "n_encoded_predictors": p - 1,
        "R_squared_training": r2, "Adjusted_R_squared_training": adj,
        "F_statistic": f, "F_df_numerator": p-1, "F_df_denominator": dof, "F_p_value": fp,
        "Test_R_squared": baseline, "Test_RMSE": np.sqrt(mean_squared_error(y[test], prediction[test])),
        "Test_MAE": mean_absolute_error(y[test], prediction[test])}])
    metrics.to_csv(OUTPUT_DIR / "data_a_model_summary.csv", index=False)
    pd.DataFrame(references).to_csv(OUTPUT_DIR / "data_a_dummy_reference_categories.csv", index=False)
    pd.DataFrame({"source_excel_row": df.index[test] + 2, "actual_global_sales": y[test],
        "predicted_global_sales": prediction[test], "residual": y[test] - prediction[test]}).to_csv(OUTPUT_DIR / "data_a_test_predictions.csv", index=False)
    report = ["DATA A: ONE MULTIPLE LINEAR REGRESSION MODEL", "",
        "Outcome: Global_Sales. Predictors: NA_Sales, Year, Publisher, Genre, Platform.",
        "EU_Sales, JP_Sales, Other_Sales and Rank are excluded as predictors.",
        f"Dropped {len(raw)-len(df)} rows with missing/non-finite required values. Random 80/20 split; seed 42.",
        "Categories use training-only dummy encoding; most frequent training category is the reference.",
        *unknowns, f"Aliased columns removed: {dropped}", "", "MODEL FIT AND TEST ACCURACY", metrics.to_string(index=False),
        "F is the overall regression F-statistic, not a classification F1 score.",
        "A stored p-value of 0.0 underflows floating-point precision; report p < 0.001, not literally zero.",
        "Adjusted R-squared and the F-test describe training fit; test R-squared, RMSE and MAE measure held-out accuracy.",
        "", "FEATURE IMPORTANCE (NUMERIC)", importance.to_string(index=False),
        "Importance is the mean decrease in held-out R-squared across 20 permutations of each original variable; categorical dummy columns move together.",
        "Larger decreases mean greater predictive importance. Correlated features can share or mask importance; values are not percentages or causal effects.",
        "", "TOP 20 STANDARDIZED COEFFICIENTS", weights.head(20).to_string(index=False),
        "", "COEFFICIENT INTERPRETATION",
        "B is the expected change in Global_Sales per unit increase, holding the other included predictors constant.",
        "Dummy B compares a category with its reference. Standardized Beta = B * training SD(X) / training SD(Y); the intercept has no standardized Beta.",
        "The coefficient CSV includes all retained terms, standard errors, t-values and unadjusted p-values.",
        "Category p < .05 flags are exploratory; no multiple-comparison adjustment is applied.",
        "OLS p-values assume a correctly specified model with homoskedastic independent errors; causal effects are not established.",
        "NA_Sales is part of Global_Sales. This estimates global totals conditional on known North American sales, rather than pre-release forecasts."]
    (OUTPUT_DIR / "data_a_report.txt").write_text("\n".join(report), encoding="utf-8")
    print(metrics.to_string(index=False))
    print(importance.to_string(index=False))


if __name__ == "__main__":
    with threadpool_limits(limits=2):
        main()
