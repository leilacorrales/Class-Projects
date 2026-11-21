"""K-means salary-grouping workflow for CIS 3250 Project 4.

Salary is excluded while forming clusters to prevent leakage. After clustering,
each cluster receives an average salary that can be used as a group-based salary
estimate for existing or new students.
"""

from pathlib import Path
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
INPUT = BASE_DIR / "exploratory_analysis_clean.csv"
OUTPUT = BASE_DIR / "kmeans_salary_results.csv"
K = 3
SEED = 42

FEATURES = [
    "Undergrad Grade",
    "MBA Grade",
    "Work Experience",
    "Employability Growth",
]
SALARY = "Annual Salary (000s)"


def fit_kmeans(x, k=3, seed=42, iterations=200, starts=20):
    """Fit a small NumPy-only k-means model and return labels and centers."""
    rng = np.random.default_rng(seed)
    best_labels, best_centers, best_sse = None, None, np.inf

    for _ in range(starts):
        centers = x[rng.choice(len(x), size=k, replace=False)].copy()
        for _ in range(iterations):
            distances = ((x[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
            labels = distances.argmin(axis=1)
            new_centers = np.array([
                x[labels == cluster].mean(axis=0)
                if np.any(labels == cluster) else centers[cluster]
                for cluster in range(k)
            ])
            if np.allclose(new_centers, centers):
                break
            centers = new_centers

        sse = ((x - centers[labels]) ** 2).sum()
        if sse < best_sse:
            best_labels, best_centers, best_sse = labels, centers, sse

    return best_labels, best_centers


def standardize(values):
    means = values.mean(axis=0)
    scales = values.std(axis=0, ddof=0)
    scales[scales == 0] = 1
    return (values - means) / scales, means, scales


def assign_new_student(student, centers, feature_means, feature_scales, salary_by_cluster):
    """Return a cluster and salary estimate for one new student.

    The student dictionary must contain the six names in FEATURES. Salary is not
    required because it is the value being estimated.
    """
    values = np.array([[float(student[name]) for name in FEATURES]])
    scaled = (values - feature_means) / feature_scales
    distances = ((scaled[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2)
    cluster = int(distances.argmin(axis=1)[0])
    return {
        "kmeans_cluster": cluster,
        "estimated_salary_000s": float(salary_by_cluster[cluster]),
    }


df = pd.read_csv(INPUT)
required = FEATURES + [SALARY]
missing_columns = [column for column in required if column not in df.columns]
if missing_columns:
    raise ValueError(f"Missing required columns: {missing_columns}")
if df[required].isna().any().any():
    raise ValueError("The input contains missing values in clustering or salary fields.")

raw_features = df[FEATURES].astype(float).to_numpy()
scaled_features, feature_means, feature_scales = standardize(raw_features)
labels, centers = fit_kmeans(scaled_features, K, SEED)
df["KMeans Cluster"] = labels

salary_by_cluster = df.groupby("KMeans Cluster")[SALARY].mean().to_dict()
median_by_cluster = df.groupby("KMeans Cluster")[SALARY].median().to_dict()
df["Cluster Average Salary (000s)"] = df["KMeans Cluster"].map(salary_by_cluster)
df["Cluster Median Salary (000s)"] = df["KMeans Cluster"].map(median_by_cluster)
df.to_csv(OUTPUT, index=False)

summary = (df.groupby("KMeans Cluster", as_index=False)[SALARY]
             .agg(Student_Count="size", Average_Salary_000s="mean",
                  Median_Salary_000s="median"))
print(f"Created {OUTPUT.name} with {len(df):,} rows.")
print("Salary is used only after clustering to estimate each cluster's typical salary.")
print(summary.to_string(index=False))
centers_original = centers * feature_scales + feature_means
print("\nCluster centers in original feature units:")
print(pd.DataFrame(centers_original, columns=FEATURES).round(2).to_string(index=True))
