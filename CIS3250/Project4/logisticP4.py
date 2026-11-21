"""Create and run the CIS 3250 logistic-regression model."""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

BASE_DIR = Path(__file__).resolve().parent
SOURCE = BASE_DIR / "original_cleaned.csv"
DATASET = BASE_DIR / "logisticP4_data.csv"

NON_SALARY_FIELDS = [
    "Student ID", "Undergrad Degree", "Undergrad Grade", "MBA Grade",
    "Work Experience", "Employability (Before)", "Employability (After)",
    "Employability Growth", "Status",
]


df = pd.read_csv(SOURCE)
complete = df.dropna(subset=NON_SALARY_FIELDS).copy()

# Before and After are intentionally excluded; Growth is retained as the
# single employability predictor requested for this model.
model = complete[[
    "Student ID", "Undergrad Degree", "Undergrad Grade", "MBA Grade",
    "Work Experience", "Employability Growth", "Status",
]].copy()

# Convert the categorical degree into five numeric indicator predictors.
model = pd.get_dummies(model, columns=["Undergrad Degree"],
                       prefix="undergrad_degree", dtype=int)
model.to_csv(DATASET, index=False)

target = "Status"
predictor_columns = [c for c in model.columns if c not in {"Student ID", target}]
X = model[predictor_columns].astype(float)
y = model[target].astype(int)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

classifier = LogisticRegression(max_iter=2000, random_state=42)
classifier.fit(X_train_scaled, y_train)
predictions = classifier.predict(X_test_scaled)
probabilities = classifier.predict_proba(X_test_scaled)[:, 1]

print("=" * 72)
print("CIS 3250 LOGISTIC REGRESSION")
print(f"Rows in dataset: {len(model):,}")
print(f"Predictors used: {len(predictor_columns)}")
print(f"Predictor names: {', '.join(predictor_columns)}")
print(f"Placed: {(y == 1).sum():,} | Not placed: {(y == 0).sum():,}")
print("=" * 72)
print(f"Accuracy: {accuracy_score(y_test, predictions):.3f}")
print(f"ROC-AUC:  {roc_auc_score(y_test, probabilities):.3f}")
print("\nClassification report:")
print(classification_report(y_test, predictions, target_names=["Not Placed", "Placed"], zero_division=0))

matrix = confusion_matrix(y_test, predictions)
fig, ax = plt.subplots(figsize=(6, 5))
image = ax.imshow(matrix, cmap="Blues")
fig.colorbar(image, ax=ax)
ax.set_title("Logistic Regression Confusion Matrix")
ax.set_xlabel("Predicted status")
ax.set_ylabel("Actual status")
ax.set_xticks([0, 1], ["Not Placed", "Placed"])
ax.set_yticks([0, 1], ["Not Placed", "Placed"])
for row in range(2):
    for col in range(2):
        ax.text(col, row, matrix[row, col], ha="center", va="center")
plt.tight_layout()
plt.show()
