"""Pearson and Spearman correlation heatmaps for CIS 3250 Project 4."""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent
SOURCE = BASE_DIR / "original_cleaned.csv"

NON_SALARY_FIELDS = [
    "Student ID", "Undergrad Degree", "Undergrad Grade", "MBA Grade",
    "Work Experience", "Employability (Before)", "Employability (After)",
    "Employability Growth", "Status",
]

FEATURES = [
    "Undergrad Grade",
    "MBA Grade",
    "Work Experience",
    "Employability Growth",
    "Status",
]


def draw_heatmap(matrix, title, axis):
    image = axis.imshow(matrix, cmap="coolwarm", vmin=-1, vmax=1)
    axis.set_title(title, fontweight="bold")
    axis.set_xticks(range(len(FEATURES)), FEATURES, rotation=40, ha="right")
    axis.set_yticks(range(len(FEATURES)), FEATURES)
    for row in range(len(FEATURES)):
        for col in range(len(FEATURES)):
            axis.text(col, row, f"{matrix.iloc[row, col]:.2f}",
                      ha="center", va="center", fontsize=9)
    return image


df = pd.read_csv(SOURCE).dropna(subset=NON_SALARY_FIELDS).copy()
values = df[FEATURES].astype(float)
pearson = values.corr(method="pearson")

print(f"Rows analyzed: {len(df):,}")
print("\nPearson correlation matrix:")
print(pearson.round(3).to_string())

figure, axis = plt.subplots(figsize=(9, 7))
draw_heatmap(pearson, "Pearson Correlation", axis)
figure.suptitle("Pearson Feature Correlations: 1,153 Complete Non-Salary Records",
                fontsize=16, fontweight="bold")
figure.colorbar(plt.cm.ScalarMappable(cmap="coolwarm", norm=plt.Normalize(-1, 1)),
                ax=axis, shrink=0.8, label="Correlation")
plt.tight_layout()
plt.show()
