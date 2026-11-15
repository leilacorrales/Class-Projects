"""K-means customer segmentation. Run from any directory; see requirements-project2.txt."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, davies_bouldin_score
from threadpoolctl import threadpool_limits

BASE = Path(__file__).resolve().parent
OUTPUT_DIR = BASE / "project2_data_b_outputs"
FEATURES = ["PURCHASES", "CASH_ADVANCE", "BALANCE"]
SEED = 42


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    raw = pd.read_excel(BASE / "Project2.2data-1.xlsx")
    df = raw.drop_duplicates().drop_duplicates(subset="CUST_ID").copy()
    for col in FEATURES:
        df[col] = pd.to_numeric(df[col], errors="coerce").replace([np.inf, -np.inf], np.nan)
        df.loc[df[col] < 0, col] = np.nan
    missing = df[FEATURES].isna().sum()
    medians = df[FEATURES].median()
    if medians.isna().any():
        raise ValueError("A selected feature has no valid values.")
    df[FEATURES] = df[FEATURES].fillna(medians)
    scaler = StandardScaler()
    # Log transform tempers monetary skew without discarding large customers.
    X = scaler.fit_transform(np.log1p(df[FEATURES]))
    evaluations, models = [], {}
    for k in range(2, 11):
        model = KMeans(n_clusters=k, n_init=20, random_state=SEED).fit(X)
        labels = model.labels_
        score = silhouette_score(X, labels, sample_size=min(2500, len(X)), random_state=SEED)
        evaluations.append({"k": k, "inertia": model.inertia_, "silhouette_sample_2500": score,
            "Davies_Bouldin_index": davies_bouldin_score(X, labels),
            "smallest_cluster_count": np.bincount(labels).min()})
        models[k] = model
    evaluation = pd.DataFrame(evaluations)
    xnorm = (evaluation.k.to_numpy() - 2) / 8
    ynorm = (evaluation.inertia.to_numpy() - evaluation.inertia.iloc[-1]) / (evaluation.inertia.iloc[0] - evaluation.inertia.iloc[-1])
    evaluation["elbow_chord_distance"] = (1 - xnorm - ynorm) / np.sqrt(2)
    elbow_k = int(evaluation.loc[evaluation.elbow_chord_distance.idxmax(), "k"])
    chosen = int(evaluation.sort_values(["silhouette_sample_2500", "Davies_Bouldin_index"], ascending=[False, True]).iloc[0].k)
    model = models[chosen]
    df["cluster"] = model.labels_
    evaluation.to_csv(OUTPUT_DIR / "data_b_cluster_evaluation.csv", index=False)
    df.to_csv(OUTPUT_DIR / "data_b_customers_with_clusters.csv", index=False)
    pd.DataFrame({"feature": FEATURES, "imputed_values": missing.values, "imputation_median": medians.values,
        "log1p_mean": scaler.mean_, "log1p_sd": scaler.scale_}).to_csv(OUTPUT_DIR / "data_b_preprocessing.csv", index=False)
    profile = df.groupby("cluster")[FEATURES].agg(["mean", "median"])
    profile.columns = [f"{a}_{b}" for a, b in profile.columns]
    profile.insert(0, "customers", df.groupby("cluster").size())
    profile.insert(1, "percent", profile.customers / len(df) * 100)
    centers = np.expm1(scaler.inverse_transform(model.cluster_centers_))
    for i, col in enumerate(FEATURES):
        profile[f"{col}_inverse_log_centroid"] = centers[:, i]
    profile.to_csv(OUTPUT_DIR / "data_b_cluster_profiles.csv")
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    for ax, column, title in zip(axes, ["inertia", "silhouette_sample_2500", "Davies_Bouldin_index"], ["Elbow: lower inertia", "Silhouette: higher is better", "Davies-Bouldin: lower is better"]):
        ax.plot(evaluation.k, evaluation[column], marker="o")
        ax.axvline(chosen, color="tab:red", linestyle="--", label=f"Chosen k={chosen}")
        ax.set(xlabel="Number of clusters", title=title)
        ax.legend()
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "data_b_cluster_selection.png", dpi=180)
    plt.close(fig)
    fig = plt.figure(figsize=(11, 8))
    ax = fig.add_subplot(111, projection="3d")
    cmap = plt.get_cmap("tab10")
    for cluster in range(chosen):
        points = X[model.labels_ == cluster]
        ax.scatter(*points.T, s=7, alpha=.25, color=cmap(cluster), label=f"Cluster {cluster} (n={len(points):,})")
        ax.text(*model.cluster_centers_[cluster], f"  Cluster {cluster}", fontsize=10, weight="bold")
    ax.scatter(*model.cluster_centers_.T, marker="X", s=180, c="black", label="Centroids")
    ax.set(xlabel="Purchases (standardized log1p)", ylabel="Cash advance (standardized log1p)", zlabel="Balance (standardized log1p)", title="Credit-card customer segments")
    ax.set_box_aspect((1, 1, 1), zoom=.80)
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "data_b_customer_segments_3d.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    report = ["DATA B: CUSTOMER SEGMENTATION FOR TARGETED BANK MARKETING", "",
        "Business question: Which customer types emerge from credit-card usage, and how can the bank tailor its marketing?", "",
        "DATA PREPARATION AND FEATURE CHOICE",
        f"Input: {len(raw):,} rows. Analyzed: {len(df):,}; removed {len(raw)-len(df)} duplicate rows/customer IDs.",
        "Selected three features by business reasoning: PURCHASES measures purchasing activity, CASH_ADVANCE measures cash-access usage, and BALANCE measures outstanding balance.",
        "These describe purchasing, cash usage and balance levels. They are not supervised feature-importance scores.",
        "CUST_ID is an identifier, excluded from clustering. The selected variables are numeric; categorical encoding is unnecessary.",
        "Missing, non-finite or negative selected values are replaced with feature medians. Other columns are retained for context but do not enter the model.",
        f"Imputed counts: {missing.to_dict()}. Applied log1p to reduce monetary skew, then standardized each feature to mean zero and unit variance.",
        "Large valid values were retained. Inverse-transformed log centroids are not arithmetic means.", "",
        "CHOOSING THE NUMBER OF CLUSTERS", evaluation.to_string(index=False),
        f"The endpoint-chord elbow heuristic suggests k={elbow_k}. The primary rule (highest silhouette, DB as tie-breaker) selects k={chosen}.",
        f"The lowest Davies-Bouldin index occurs at k={int(evaluation.loc[evaluation.Davies_Bouldin_index.idxmin(), 'k'])}.",
        "Silhouette uses the same reproducible random sample of up to 2,500 customers for each k; inertia and DB use all customers.",
        "The elbow and DB are cross-checks, not guarantees of a uniquely correct segmentation. See the selection figure to assess disagreements.",
        "K-means uses 20 initializations and random seed 42; labels have no inherent order.", "",
        "CUSTOMER PROFILES", profile.to_string(), "",
        "See data_b_business_deliverable.txt for segment-specific interpretations and recommendations.",
        "The 3D figure shows all three transformed, standardized model inputs and labels each cluster and centroid.",
        "This is descriptive segmentation, without a target label or classification accuracy. It does not establish creditworthiness, repayment capacity or causation.",
        "Pilot offers within each segment and compare acceptance, incremental usage, retention and cost before broader rollout."]
    (OUTPUT_DIR / "data_b_report.txt").write_text("\n".join(report), encoding="utf-8")
    business = ["DATA B: CUSTOMER TYPES AND TARGETED MARKETING RECOMMENDATIONS", "",
        f"K-means separates the {len(df):,} customers into {chosen} groups based on purchases, cash advances and outstanding balance. The analysis uses log-transformed, standardized values so that monetary scale and extreme observations do not dominate distances.",
        "The features were chosen for their business relevance: purchases indicate card spending, cash advances distinguish cash-access usage, and balance describes outstanding amounts. No customer identifier, protected attribute or supervised target enters the model.",
        f"For k={chosen}, silhouette is {evaluation.loc[evaluation.k == chosen, 'silhouette_sample_2500'].iloc[0]:.4f} (higher is better), and Davies-Bouldin is {evaluation.loc[evaluation.k == chosen, 'Davies_Bouldin_index'].iloc[0]:.4f} (lower is better). The elbow heuristic suggests {elbow_k} clusters. Scores compare k=2 through k=10; silhouette uses a fixed random sample of 2,500 customers.", "",
        "SUMMARY TABLE (MEDIANS IN ORIGINAL DATASET MONETARY UNITS)",
        "Cluster | Customers | Share | Purchases | Cash advance | Balance | Customer type"]
    details = []
    for cluster, row in profile.iterrows():
        purchase, cash, balance = [row[f"{c}_inverse_log_centroid"] for c in FEATURES]
        if purchase < 1:
            name = "Cash-advance-focused, minimal purchases"
            interpretation = "Customers use the card primarily for cash advances, with almost no purchasing activity. Their outstanding balances are substantial relative to the low-balance group."
            action = "Offer clear cash-access cost information, optional payment reminders and budgeting tools. Test a modest purchase-activation incentive for customers who want to use the card for everyday spending. Avoid treating cash usage alone as proof of financial distress or eligibility for more borrowing."
            measurement = "Track voluntary purchase activation, offer cost, engagement with payment tools and customer retention."
        elif cash > 100:
            name = "Mixed purchases and cash advances"
            interpretation = "Customers combine purchase activity with cash advances and have relatively high balances. They represent a distinct mixed-use group."
            action = "Test retention messaging and rewards tied to existing purchase activity, alongside transparent cash-access costs and optional payment-management tools. Do not infer repayment capacity or automatically raise credit limits from this segment."
            measurement = "Track incremental purchases, retention, reward cost and payment-tool engagement."
        elif balance < 100:
            name = "Low-balance purchasers"
            interpretation = "Customers make purchases while holding low observed balances and using very little cash advance. Low balances alone do not prove that they pay in full every period."
            action = "Test low-cost everyday-purchase rewards and card-engagement messages. Keep incentives modest because current purchase amounts are lower than those of the purchase-focused group."
            measurement = "Track active-card usage, incremental purchases, incentive cost and retention."
        else:
            name = "Purchase-focused customers with balances"
            interpretation = "Customers emphasize purchases, with almost no cash advances, and maintain higher balances than the low-balance purchasers."
            action = "Test purchase-category rewards or merchant offers, paired with useful spending summaries and optional payment reminders. Tailor messages to purchase activity without assuming that these customers are premium, profitable or low risk."
            measurement = "Track offer redemption, incremental purchases, retention and net campaign contribution."
        business.append(f"{cluster} | {int(row.customers):,} | {row.percent:.2f}% | {row.PURCHASES_median:,.2f} | {row.CASH_ADVANCE_median:,.2f} | {row.BALANCE_median:,.2f} | {name}")
        details += [f"Cluster {cluster}: {name}", interpretation,
            f"Arithmetic mean purchases: {row.PURCHASES_mean:,.2f}; cash advances: {row.CASH_ADVANCE_mean:,.2f}; balance: {row.BALANCE_mean:,.2f}.",
            "Recommended strategy: " + action, "Evaluate the pilot: " + measurement, ""]
    business += ["", "SEGMENT INTERPRETATION AND STRATEGIES", *details,
        "FIGURE AND IMPLEMENTATION",
        "data_b_customer_segments_3d.png plots all customers on the three standardized log1p feature axes. Colors and labels identify clusters; black X markers identify centroids. The figure uses the same coordinates used by K-means.",
        "data_b_cluster_selection.png shows the elbow curve, silhouette scores and Davies-Bouldin indices. data_b_cluster_profiles.csv contains arithmetic means, medians and inverse-transformed log centroids. Medians are emphasized in the summary because monetary distributions are skewed.",
        "Run small controlled marketing pilots before rollout. Measure incremental campaign contribution after rewards and communication costs, rather than treating cluster membership as proof of profitability.",
        "This segmentation describes observed behavior. It does not establish income, creditworthiness, repayment capacity, full-payment behavior or causal effects. Cluster labels are arbitrary, and conclusions depend on selected features and transformations. Reassess profiles with refreshed data before reusing them."]
    (OUTPUT_DIR / "data_b_business_deliverable.txt").write_text("\n".join(business), encoding="utf-8")
    print(evaluation.to_string(index=False))
    print(f"Selected k={chosen}; elbow k={elbow_k}")
    print(profile.to_string())


if __name__ == "__main__":
    with threadpool_limits(limits=2):
        main()
