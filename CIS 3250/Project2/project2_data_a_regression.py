"""Project 2 Data A: Multiple linear regression for video-game sales.

Before running, replace DATA_PATH with the path to Project 2.1 data.xlsx.
The script creates a project2_data_a_outputs folder containing tables,
figures, cleaned data, and a text report.
"""

from pathlib import Path
import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# Replace this with your own path. Because the input is Excel, use read_excel.
DATA_PATH = r"C:/Users/anici/Class-Projects/CIS 3250/Project2/Project2.1data-1.xlsx"
OUTPUT_DIR = Path("project2_data_a_outputs")
TEST_SIZE = 0.20
RANDOM_STATE = 42


def safe_name(text):
    return re.sub(r"[^A-Za-z0-9_]+", "_", str(text)).strip("_")[:80]


def ols_fit(X, y):
    """Return OLS coefficients, standard errors, p-values, and fit statistics."""
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    n, p_total = X.shape
    k = p_total - 1  # predictors, excluding intercept
    xtx_inv = np.linalg.pinv(X.T @ X)
    coefficients = xtx_inv @ X.T @ y
    fitted = X @ coefficients
    residuals = y - fitted
    df_resid = max(n - p_total, 1)
    sse = float(residuals @ residuals)
    y_bar = float(np.mean(y))
    sst = float((y - y_bar) @ (y - y_bar))
    r2 = 1 - sse / sst if sst else np.nan
    adj_r2 = 1 - (1 - r2) * (n - 1) / df_resid if n > p_total else np.nan
    mse = sse / df_resid
    standard_errors = np.sqrt(np.maximum(np.diag(mse * xtx_inv), 0))
    t_values = np.divide(
        coefficients,
        standard_errors,
        out=np.full_like(coefficients, np.nan),
        where=standard_errors > 0,
    )
    p_values = 2 * stats.t.sf(np.abs(t_values), df=df_resid)
    ssr = max(sst - sse, 0)
    f_stat = (ssr / k) / (sse / df_resid) if k > 0 and sse > 0 else np.nan
    f_p_value = stats.f.sf(f_stat, k, df_resid) if np.isfinite(f_stat) else np.nan
    return {
        "coefficients": coefficients,
        "standard_errors": standard_errors,
        "t_values": t_values,
        "p_values": p_values,
        "n": n,
        "p_total": p_total,
        "df_resid": df_resid,
        "r2": r2,
        "adj_r2": adj_r2,
        "f_stat": f_stat,
        "f_p_value": f_p_value,
        "fitted": fitted,
    }


def main():
    if not DATA_PATH:
        raise ValueError("Replace DATA_PATH with the path to Project 2.1 data.xlsx.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_excel(DATA_PATH)

    required = {
        "Year", "Genre", "Platform", "Publisher", "NA_Sales", "EU_Sales",
        "JP_Sales", "Other_Sales", "Global_Sales",
    }
    missing_columns = required - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    original_rows = len(df)
    # User decision: remove rows missing Year or Publisher.
    df = df.dropna(subset=["Year", "Publisher"]).copy()
    df.to_csv(OUTPUT_DIR / "data_a_cleaned.csv", index=False)

    numeric_predictors = ["Year", "NA_Sales", "EU_Sales", "JP_Sales", "Other_Sales"]
    categorical_options = {
        "Numeric_only": None,
        "Genre": "Genre",
        "Platform": "Platform",
        "Publisher": "Publisher",
    }

    # Use the same split for all four models for a fair comparison.
    train_idx, test_idx = train_test_split(
        np.arange(len(df)), test_size=TEST_SIZE, random_state=RANDOM_STATE
    )
    y_all = df["Global_Sales"].astype(float).to_numpy()
    y_train, y_test = y_all[train_idx], y_all[test_idx]

    model_rows = []
    coefficient_tables = []
    prediction_tables = []
    reference_rows = []

    for model_name, categorical in categorical_options.items():
        columns = numeric_predictors.copy()
        if categorical is not None:
            encoded = pd.get_dummies(
                df[[categorical]].astype(str).reset_index(drop=True),
                columns=[categorical],
                drop_first=True,
                dtype=float,
            )
            X_frame = pd.concat([df[numeric_predictors].reset_index(drop=True), encoded], axis=1)
            dummy_columns = [c for c in X_frame.columns if c not in numeric_predictors]
            reference_category = sorted(df[categorical].astype(str).unique())[0]
            reference_rows.append({
                "model": model_name,
                "categorical_variable": categorical,
                "reference_category": reference_category,
                "number_of_dummy_variables": len(dummy_columns),
            })
        else:
            X_frame = df[numeric_predictors].reset_index(drop=True).astype(float)
            reference_rows.append({
                "model": model_name,
                "categorical_variable": "None",
                "reference_category": "None",
                "number_of_dummy_variables": 0,
            })

        X_frame = X_frame.astype(float)
        # Remove any zero-variance columns from the training data only.
        train_frame = X_frame.iloc[train_idx]
        usable_columns = [c for c in X_frame.columns if train_frame[c].std(ddof=0) > 0]
        X_frame = X_frame[usable_columns]
        X_train = X_frame.iloc[train_idx].to_numpy()
        X_test = X_frame.iloc[test_idx].to_numpy()

        X_train_i = np.column_stack([np.ones(len(X_train)), X_train])
        X_test_i = np.column_stack([np.ones(len(X_test)), X_test])
        fit = ols_fit(X_train_i, y_train)
        pred_train = X_train_i @ fit["coefficients"]
        pred_test = X_test_i @ fit["coefficients"]

        # Standardized Beta = B * predictor SD / outcome SD, using training data.
        x_sd = X_train.std(axis=0, ddof=0)
        y_sd = y_train.std(ddof=0)
        beta = np.divide(
            fit["coefficients"][1:] * x_sd,
            y_sd,
            out=np.full(len(x_sd), np.nan),
            where=y_sd > 0,
        )
        coefficient_tables.append(pd.DataFrame({
            "model": model_name,
            "predictor": list(X_frame.columns),
            "B_unstandardized": fit["coefficients"][1:],
            "Beta_standardized": beta,
            "standard_error": fit["standard_errors"][1:],
            "t_value": fit["t_values"][1:],
            "p_value": fit["p_values"][1:],
            "significant_at_0.05": fit["p_values"][1:] < 0.05,
        }))
        prediction_tables.append(pd.DataFrame({
            "model": model_name,
            "actual_global_sales": y_test,
            "predicted_global_sales": pred_test,
            "residual": y_test - pred_test,
        }))
        model_rows.append({
            "model": model_name,
            "n_cleaned_rows": len(df),
            "n_training_rows": len(train_idx),
            "n_testing_rows": len(test_idx),
            "number_of_predictors": X_train.shape[1],
            "R_squared_training": fit["r2"],
            "Adjusted_R_squared_training": fit["adj_r2"],
            "F_statistic": fit["f_stat"],
            "F_p_value": fit["f_p_value"],
            "Test_R_squared": r2_score(y_test, pred_test),
            "Test_RMSE": np.sqrt(mean_squared_error(y_test, pred_test)),
            "Test_MAE": mean_absolute_error(y_test, pred_test),
        })

    model_summary = pd.DataFrame(model_rows)
    coefficients = pd.concat(coefficient_tables, ignore_index=True)
    predictions = pd.concat(prediction_tables, ignore_index=True)
    references = pd.DataFrame(reference_rows)
    model_summary.to_csv(OUTPUT_DIR / "data_a_model_comparison.csv", index=False)
    coefficients.to_csv(OUTPUT_DIR / "data_a_all_coefficients.csv", index=False)
    references.to_csv(OUTPUT_DIR / "data_a_dummy_reference_categories.csv", index=False)
    predictions.to_csv(OUTPUT_DIR / "data_a_test_predictions.csv", index=False)

    top_coefficients = (
        coefficients[coefficients["significant_at_0.05"]]
        .assign(abs_beta=lambda x: x["Beta_standardized"].abs())
        .sort_values(["model", "abs_beta"], ascending=[True, False])
        .groupby("model", as_index=False)
        .head(15)
    )
    top_coefficients.to_csv(OUTPUT_DIR / "data_a_top_significant_coefficients.csv", index=False)

    # Comparison figure: predictive accuracy and model fit.
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    x = np.arange(len(model_summary))
    labels = model_summary["model"]
    axes[0].bar(x - 0.18, model_summary["R_squared_training"], width=0.36, label="Training R²")
    axes[0].bar(x + 0.18, model_summary["Test_R_squared"], width=0.36, label="Test R²")
    axes[0].set_xticks(x, labels, rotation=20)
    axes[0].set_ylim(0, 1.05)
    axes[0].set_ylabel("R²")
    axes[0].set_title("Model fit and predictive R²")
    axes[0].legend()
    axes[1].bar(x - 0.18, model_summary["Test_RMSE"], width=0.36, label="RMSE")
    axes[1].bar(x + 0.18, model_summary["Test_MAE"], width=0.36, label="MAE")
    axes[1].set_xticks(x, labels, rotation=20)
    axes[1].set_ylabel("Sales units")
    axes[1].set_title("Test prediction error")
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "data_a_model_comparison.png", dpi=200)
    plt.close(fig)

    # Plot the strongest standardized effects from each model.
    plot_df = top_coefficients.copy()
    plot_df["label"] = plot_df["predictor"].map(str).map(lambda x: x[:28])
    models = list(categorical_options.keys())
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    for ax, model_name in zip(axes.ravel(), models):
        sub = plot_df[plot_df["model"] == model_name].head(10).sort_values("Beta_standardized")
        if sub.empty:
            ax.text(0.5, 0.5, "No significant predictors", ha="center", va="center")
        else:
            ax.barh(sub["label"], sub["Beta_standardized"])
            ax.axvline(0, color="black", linewidth=0.8)
        ax.set_title(f"{model_name}: strongest significant effects")
        ax.set_xlabel("Standardized Beta")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "data_a_standardized_feature_weights.png", dpi=200)
    plt.close(fig)

    # Report text follows the template's results and business-insight structure.
    best_model = model_summary.sort_values("Test_RMSE").iloc[0]
    report_lines = [
        "DATA A: LINEAR REGRESSION REPORT",
        "",
        f"Original rows: {original_rows}",
        f"Rows after removing missing Year or Publisher: {len(df)}",
        "Missing-row rule: removed rows missing Year or Publisher.",
        "Numeric predictors in every model: Year, NA_Sales, EU_Sales, JP_Sales, Other_Sales.",
        "Regional sales were retained as requested. Because they are components of Global_Sales, the resulting accuracy may be unusually high.",
        "",
        "MODEL COMPARISON",
        model_summary.to_string(index=False),
        "",
        f"Lowest test RMSE: {best_model['model']}.",
        "",
        "INTERPRETATION GUIDANCE",
        "B measures the expected change in Global_Sales for a one-unit predictor increase.",
        "Standardized Beta compares relative influence across predictors.",
        "Dummy coefficients compare each category with its reference category.",
        "See data_a_dummy_reference_categories.csv for the reference categories.",
        "",
        "BUSINESS INSIGHTS",
        "1. Use the coefficient table to identify statistically significant positive and negative effects.",
        "2. Prioritize predictors with large absolute standardized Beta values, while checking their p-values.",
        "3. Use significant platform, genre, or publisher effects to guide portfolio and marketing decisions.",
        "4. Treat regional-sales recommendations cautiously because regional sales are components of Global_Sales.",
    ]
    (OUTPUT_DIR / "data_a_report.txt").write_text("\n".join(report_lines), encoding="utf-8")
    print(f"Completed Data A. Outputs saved in: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
