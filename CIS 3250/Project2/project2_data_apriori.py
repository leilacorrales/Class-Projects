"""Project 2 Data C: Apriori market-basket analysis.

Before running, replace DATA_PATH with the path to Project 2.3 data.xlsx.
The file is intentionally read with header=None because the first row contains
the first horizontal transaction rather than column headers.
"""

from collections import Counter
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# Replace this with your own path. Because the input is Excel, use read_excel.
DATA_PATH = r""
OUTPUT_DIR = Path("project2_data_c_outputs")
MIN_SUPPORT = 0.01
MIN_CONFIDENCE = 0.20
TOP_N_RULES = 10


def support_counts(transactions):
    counts = Counter()
    for transaction in transactions:
        for itemset_size in range(1, len(transaction) + 1):
            # This helper is not used for all sizes at once; it is retained
            # only for clarity. Apriori counting below is more efficient.
            for itemset in combinations(sorted(transaction), itemset_size):
                counts[frozenset(itemset)] += 1
    return counts


def apriori(transactions, min_support):
    """Generate all frequent itemsets using the Apriori property."""
    n_transactions = len(transactions)
    min_count = int(np.ceil(min_support * n_transactions))
    item_counts = Counter()
    for transaction in transactions:
        for item in transaction:
            item_counts[frozenset([item])] += 1
    frequent = {
        itemset: count
        for itemset, count in item_counts.items()
        if count >= min_count
    }
    all_frequent = dict(frequent)
    previous = set(frequent)
    k = 2
    while previous:
        candidates = set()
        previous_list = list(previous)
        for i in range(len(previous_list)):
            for j in range(i + 1, len(previous_list)):
                candidate = previous_list[i] | previous_list[j]
                if len(candidate) != k:
                    continue
                if all(frozenset(subset) in previous for subset in combinations(candidate, k - 1)):
                    candidates.add(candidate)
        if not candidates:
            break
        counts = Counter()
        for transaction in transactions:
            for candidate in candidates:
                if candidate.issubset(transaction):
                    counts[candidate] += 1
        frequent = {itemset: count for itemset, count in counts.items() if count >= min_count}
        all_frequent.update(frequent)
        previous = set(frequent)
        k += 1
    return all_frequent, n_transactions


def main():
    if not DATA_PATH:
        raise ValueError("Replace DATA_PATH with the path to Project 2.3 data.xlsx.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    # The dataset is horizontal: one row is one transaction and cells are items.
    df = pd.read_excel(DATA_PATH, header=None)
    df.to_csv(OUTPUT_DIR / "data_c_horizontal_loaded_data.csv", index=False, header=False)

    transactions = []
    for row in df.itertuples(index=False, name=None):
        items = {
            str(value).strip()
            for value in row
            if not pd.isna(value) and str(value).strip() != ""
        }
        if items:
            transactions.append(items)

    if not transactions:
        raise ValueError("No non-empty transactions were found.")

    itemsets, n_transactions = apriori(transactions, MIN_SUPPORT)
    itemset_rows = []
    support_lookup = {}
    for itemset, count in itemsets.items():
        support = count / n_transactions
        support_lookup[itemset] = support
        itemset_rows.append({
            "itemset": ", ".join(sorted(itemset)),
            "item_count": len(itemset),
            "support_count": count,
            "support": support,
        })
    frequent_itemsets = pd.DataFrame(itemset_rows).sort_values(
        ["item_count", "support"], ascending=[True, False]
    )
    frequent_itemsets.to_csv(OUTPUT_DIR / "data_c_frequent_itemsets.csv", index=False)

    rules = []
    for itemset, itemset_support in support_lookup.items():
        if len(itemset) < 2:
            continue
        itemset_items = sorted(itemset)
        for antecedent_size in range(1, len(itemset_items)):
            for antecedent_tuple in combinations(itemset_items, antecedent_size):
                antecedent = frozenset(antecedent_tuple)
                consequent = itemset - antecedent
                antecedent_support = support_lookup.get(antecedent)
                consequent_support = support_lookup.get(consequent)
                if not antecedent_support or not consequent_support:
                    continue
                confidence = itemset_support / antecedent_support
                lift = confidence / consequent_support
                if confidence >= MIN_CONFIDENCE:
                    rules.append({
                        "antecedent": ", ".join(sorted(antecedent)),
                        "consequent": ", ".join(sorted(consequent)),
                        "antecedent_size": len(antecedent),
                        "consequent_size": len(consequent),
                        "support": itemset_support,
                        "confidence": confidence,
                        "lift": lift,
                        "two_item_rule": len(itemset) == 2,
                    })

    rules_df = pd.DataFrame(rules)
    if rules_df.empty:
        raise ValueError("No rules met the selected support and confidence thresholds.")
    rules_df = rules_df.sort_values(
        ["lift", "confidence", "support"], ascending=[False, False, False]
    )
    rules_df.to_csv(OUTPUT_DIR / "data_c_all_association_rules.csv", index=False)

    top_rules = rules_df[rules_df["two_item_rule"]].head(TOP_N_RULES).copy()
    top_rules.to_csv(OUTPUT_DIR / "data_c_top_10_two_item_rules.csv", index=False)

    # Scatter plot of all generated rules, with top rules labeled.
    fig, ax = plt.subplots(figsize=(10, 7))
    scatter = ax.scatter(
        rules_df["support"], rules_df["confidence"],
        c=rules_df["lift"], cmap="viridis", alpha=0.75, edgecolor="none"
    )
    fig.colorbar(scatter, ax=ax, label="Lift")
    for _, row in top_rules.iterrows():
        ax.annotate(
            f"{row['antecedent']} → {row['consequent']}",
            (row["support"], row["confidence"]),
            xytext=(4, 4), textcoords="offset points", fontsize=8,
        )
    ax.set_xlabel("Support")
    ax.set_ylabel("Confidence")
    ax.set_title("Association rules: support, confidence, and lift")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "data_c_support_confidence_lift.png", dpi=200)
    plt.close(fig)

    report_lines = [
        "DATA C: APRIORI MARKET-BASKET ANALYSIS REPORT",
        "",
        f"Transactions analyzed: {n_transactions}",
        f"Minimum support: {MIN_SUPPORT:.2%}",
        f"Minimum confidence: {MIN_CONFIDENCE:.2%}",
        f"Frequent itemsets identified: {len(frequent_itemsets)}",
        f"Association rules generated: {len(rules_df)}",
        "The data was read horizontally: each row is a transaction and each non-empty cell is an item.",
        "The first row was retained as a transaction, so all original item positions, including olive oil, were preserved.",
        "",
        "TOP 10 TWO-ITEM RULES",
        top_rules.to_string(index=False),
        "",
        "INTERPRETATION",
        "Support measures how often the combination appears in all transactions.",
        "Confidence measures how often the consequent appears when the antecedent appears.",
        "Lift compares the observed combination with the frequency expected if the items were independent.",
        "Lift above 1 indicates a positive association.",
        "",
        "BUSINESS RECOMMENDATIONS",
        "1. Consider placing high-lift product pairs closer together.",
        "2. Test bundles or promotions for rules with useful support and high lift.",
        "3. Use confidence to estimate the likelihood of the consequent after an antecedent purchase.",
        "4. Avoid relying on lift alone; prioritize rules that also have meaningful support.",
    ]
    (OUTPUT_DIR / "data_c_report.txt").write_text("\n".join(report_lines), encoding="utf-8")
    print(f"Completed Data C. Outputs saved in: {OUTPUT_DIR.resolve()}")


if __name__ == "__main__":
    main()
