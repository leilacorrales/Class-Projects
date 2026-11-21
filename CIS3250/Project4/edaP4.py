"""One-click exploratory data analysis for CIS 3250 Project 4."""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent
INPUT = BASE_DIR / "exploratory_analysis_clean.csv"

NUMERIC_COLUMNS = [
    "Undergrad Grade",
    "MBA Grade",
    "Employability (Before)",
    "Employability (After)",
    "Employability Growth",
    "Annual Salary (000s)",
]


def main():
    df = pd.read_csv(INPUT)
    missing = [column for column in NUMERIC_COLUMNS + ["Undergrad Degree"] if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    numeric = df[NUMERIC_COLUMNS].apply(pd.to_numeric, errors="coerce")
    summary = pd.DataFrame({
        "Mean": numeric.mean(),
        "Median": numeric.median(),
        "Mode": numeric.mode().iloc[0],
        "Minimum": numeric.min(),
        "Maximum": numeric.max(),
    }).round(2)

    degree_growth = (df.groupby("Undergrad Degree", as_index=False)["Employability Growth"]
                       .mean()
                       .sort_values("Employability Growth", ascending=False))

    print("=" * 72)
    print("CIS 3250 EXPLORATORY DATA ANALYSIS")
    print(f"Rows analyzed: {len(df):,}")
    print("=" * 72)
    print("\nNumerical summary:")
    print(summary.to_string())
    print("\nAverage employability growth by undergraduate degree:")
    print(degree_growth.to_string(index=False, formatters={
        "Employability Growth": "{:.2f}".format
    }))

    fig = plt.figure(figsize=(16, 10))
    grid = fig.add_gridspec(2, 4, height_ratios=[1.25, 1], hspace=0.38, wspace=0.28)
    fig.suptitle("MBA Student Exploratory Data Analysis", fontsize=18, fontweight="bold")

    # One boxplot per numerical variable so units remain interpretable.
    for index, column in enumerate(NUMERIC_COLUMNS):
        row, col = divmod(index, 4)
        ax = fig.add_subplot(grid[row, col])
        ax.boxplot(numeric[column].dropna(), patch_artist=True,
                   boxprops=dict(facecolor="#8ecae6", color="#126782"),
                   medianprops=dict(color="#d62828", linewidth=2))
        ax.set_title(column.replace(" (000s)", " (thousands)"), fontsize=10)
        ax.set_xticks([])
        ax.grid(axis="y", alpha=0.25)

    # Replace the lower-right boxplot position with the degree comparison.
    ax_growth = fig.add_subplot(grid[1, 2:4])
    bars = ax_growth.bar(degree_growth["Undergrad Degree"],
                         degree_growth["Employability Growth"],
                         color="#2a9d8f")
    ax_growth.set_title("Average Employability Growth by Degree", fontsize=10)
    ax_growth.set_ylabel("Average Growth")
    ax_growth.tick_params(axis="x", rotation=35)
    ax_growth.grid(axis="y", alpha=0.25)
    for bar in bars:
        height = bar.get_height()
        ax_growth.text(bar.get_x() + bar.get_width() / 2, height,
                       f"{height:.1f}", ha="center", va="bottom", fontsize=9)

    plt.show()


if __name__ == "__main__":
    main()
