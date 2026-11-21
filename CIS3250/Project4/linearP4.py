"""Linear regression salary prediction for CIS 3250 Project 4.

Uses the same 688-row complete dataset as k-means. Salary is measured in
thousands of dollars, matching the cleaned CSV.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent
INPUT = BASE_DIR / "exploratory_analysis_clean.csv"
OUTPUT = BASE_DIR / "linearP4_predictions.csv"
SEED = 42

FEATURES = [
    "Undergrad Grade",
    "MBA Grade",
    "Work Experience",
    "Employability Growth",
]
TARGET = "Annual Salary (000s)"


df = pd.read_csv(INPUT)
required = FEATURES + ["Undergrad Degree", TARGET]
missing = [column for column in required if column not in df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}")

# Use the same student characteristics as k-means. Status is excluded because
# the complete dataset contains only placed students.
model = pd.get_dummies(df[["Student ID", "Undergrad Degree"] + FEATURES + [TARGET]],
                       columns=["Undergrad Degree"],
                       prefix="undergrad_degree", dtype=float)
predictors = [column for column in model.columns
              if column not in {"Student ID", TARGET}]

rng = np.random.default_rng(SEED)
indices = rng.permutation(len(model))
test_size = int(round(len(model) * 0.20))
test_idx, train_idx = indices[:test_size], indices[test_size:]

x = model[predictors].to_numpy(dtype=float)
y = model[TARGET].to_numpy(dtype=float)

# Standardize predictors using training data only, then fit an intercept.
x_mean = x[train_idx].mean(axis=0)
x_scale = x[train_idx].std(axis=0)
x_scale[x_scale == 0] = 1
x_scaled = (x - x_mean) / x_scale
x_train = np.column_stack([np.ones(len(train_idx)), x_scaled[train_idx]])
x_test = np.column_stack([np.ones(len(test_idx)), x_scaled[test_idx]])

coefficients, *_ = np.linalg.lstsq(x_train, y[train_idx], rcond=None)
predicted = x_test @ coefficients
actual = y[test_idx]
residuals = actual - predicted

mae = np.mean(np.abs(residuals))
rmse = np.sqrt(np.mean(residuals ** 2))
ss_res = np.sum(residuals ** 2)
ss_tot = np.sum((actual - actual.mean()) ** 2)
r_squared = 1 - (ss_res / ss_tot) if ss_tot else float("nan")

predictions = pd.DataFrame({
    "Student ID": model.iloc[test_idx]["Student ID"].to_numpy(),
    "Actual Salary (000s)": actual,
    "Predicted Salary (000s)": predicted.round(2),
    "Residual (000s)": residuals.round(2),
})
predictions.to_csv(OUTPUT, index=False)

print("=" * 72)
print("CIS 3250 LINEAR REGRESSION: ANNUAL SALARY")
print(f"Rows used: {len(model):,}")
print(f"Predictors used: {len(predictors)}")
print(f"Training rows: {len(train_idx):,} | Test rows: {len(test_idx):,}")
print("Salary unit: thousands of dollars")
print("=" * 72)
print(f"R-squared: {r_squared:.3f}")
print(f"MAE:       {mae:.2f} thousand dollars")
print(f"RMSE:      {rmse:.2f} thousand dollars")
print(f"Predictions saved to: {OUTPUT.name}")

plt.figure(figsize=(7, 6))
plt.scatter(actual, predicted, alpha=0.75, color="#277da1")
lower = min(actual.min(), predicted.min())
upper = max(actual.max(), predicted.max())
plt.plot([lower, upper], [lower, upper], "--", color="#d62828", label="Perfect prediction")
plt.xlabel("Actual salary (000s)")
plt.ylabel("Predicted salary (000s)")
plt.title("Linear Regression: Actual vs. Predicted Salary")
plt.legend()
plt.grid(alpha=0.25)
plt.tight_layout()
plt.show()
