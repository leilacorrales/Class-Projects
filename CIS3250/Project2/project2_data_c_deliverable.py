"""Validate existing Apriori results against baskets and write the business deliverable.
Does not rerun or replace the user's Apriori analysis.
"""
from pathlib import Path
import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parent
OUT = BASE / "project2_data_c_outputs"


def main():
    rules = pd.read_csv(OUT / "data_c_all_association_rules.csv")
    frequent = pd.read_csv(OUT / "data_c_frequent_itemsets.csv")
    raw = pd.read_excel(BASE / "Project2.3data-1.xlsx", header=None)
    baskets = [{str(v).strip() for v in row if not pd.isna(v) and str(v).strip()} for row in raw.itertuples(index=False, name=None)]
    baskets = [b for b in baskets if b]
    n = len(baskets)
    counts = {}
    def count(items):
        key = frozenset(items)
        if key not in counts:
            counts[key] = sum(key.issubset(b) for b in baskets)
        return counts[key]
    # The existing item labels do not contain comma separators.
    for row in rules.itertuples():
        a, b = set(row.antecedent.split(", ")), set(row.consequent.split(", "))
        support = count(a | b) / n
        confidence = count(a | b) / count(a)
        lift = confidence / (count(b) / n)
        if not np.allclose([support, confidence, lift], [row.support, row.confidence, row.lift], rtol=1e-9):
            raise ValueError(f"Saved rule differs from source baskets: {a} -> {b}")
        if support < .01 or confidence < .20:
            raise ValueError("Rule falls below configured thresholds")
    pairs = rules[(rules.antecedent_size == 1) & (rules.consequent_size == 1) & (rules.lift > 1)].copy()
    pairs = pairs.sort_values(["lift", "confidence", "support"], ascending=False)
    pairs["pair_key"] = pairs.apply(lambda r: " + ".join(sorted([r.antecedent, r.consequent])), axis=1)
    pairs = pairs.drop_duplicates("pair_key").head(10)
    strategy = {
        frozenset(["herb & pepper", "ground beef"]): "Offer a seasoning-and-beef recipe promotion; add shelf signage between meat and seasonings.",
        frozenset(["tomatoes", "frozen vegetables"]): "Promote vegetable meal ideas with signs linking fresh produce and frozen vegetables.",
        frozenset(["shrimp", "frozen vegetables"]): "Test a shrimp-and-vegetable stir-fry bundle and coordinated freezer displays.",
        frozenset(["soup", "milk"]): "Test a soup-and-dairy meal promotion with cross-aisle reminders.",
        frozenset(["spaghetti", "ground beef"]): "Prioritize a pasta-and-meat dinner offer, using recipe cards and coordinated stock planning.",
        frozenset(["grated cheese", "ground beef"]): "Test a cheese-and-beef meal add-on coupon and recipe signage.",
        frozenset(["olive oil", "ground beef"]): "Recommend olive oil alongside beef recipes through shelf signs or digital offers.",
        frozenset(["red wine", "spaghetti"]): "Test a pasta-and-wine meal display where store policy permits.",
        frozenset(["olive oil", "spaghetti"]): "Cross-promote pasta and olive oil as a pantry meal combination.",
        frozenset(["olive oil", "milk"]): "Test recipe-based cross-aisle reminders for dairy and cooking oil; confirm incremental purchases before discounting.",
    }
    rows = []
    for r in pairs.itertuples():
        ab = count({r.antecedent, r.consequent})
        rows.append({"product_A": r.antecedent, "product_B": r.consequent, "basket_count": ab,
            "support_percent": 100*r.support, "confidence_A_to_B_percent": 100*r.confidence,
            "confidence_B_to_A_percent": 100*ab/count({r.consequent}), "lift": r.lift,
            "recommendation": strategy.get(frozenset([r.antecedent, r.consequent]), "Pilot a paired-product offer and measure incremental margin before expansion.")})
    table = pd.DataFrame(rows)
    table.to_csv(OUT / "data_c_business_associations.csv", index=False)
    compact = []
    for r in table.itertuples():
        compact.append(f"{r.product_A} -> {r.product_B} | {r.basket_count} | {r.support_percent:.2f}% | {r.confidence_A_to_B_percent:.2f}% | {r.confidence_B_to_A_percent:.2f}% | {r.lift:.3f}")
    broad = rules[(rules.antecedent_size == 1) & (rules.consequent_size == 1) & (rules.lift > 1)].sort_values("support", ascending=False).iloc[0]
    report = ["DATA C: VALUABLE PRODUCT COMBINATIONS AND RETAIL STRATEGIES", "",
        "BUSINESS ANSWER",
        "The strongest association is herb & pepper with ground beef. For a promotion with broader observed reach, ground beef with spaghetti is a strong candidate because it combines meaningful basket frequency with a lift above two. Olive oil with spaghetti also supports a practical meal promotion. These are priorities for testing, not established profit rankings, because prices, margins and promotion costs were not supplied.", "",
        "METHOD AND EVALUATION",
        f"The existing Apriori analysis uses {n:,} non-empty shopping baskets. Each row is one basket, including the first row; blanks are removed and repeated items within a basket count once.",
        f"Minimum support is 1% (at least {int(np.ceil(.01*n))} baskets), and minimum confidence is 20%. The saved results contain {len(frequent)} frequent itemsets and {len(rules)} directional association rules.",
        "Support is the share of all baskets containing both products. Confidence A -> B is the share of A baskets also containing B. Lift is confidence divided by B's overall purchase frequency; lift above one indicates a positive association.",
        "The table lists the ten strongest distinct two-product combinations by lift among qualifying positive rules. Reverse directions are combined to avoid counting the same pair twice. The displayed A -> B direction met both thresholds; reverse confidence is descriptive and may be below 20%.",
        "All saved rule metrics were checked against the original transaction workbook. No statistical significance tests or multiple-testing corrections were performed; these are threshold-qualified positive associations, not claims of statistical significance.", "",
        "SUMMARY TABLE",
        "Rule (A -> B) | Baskets | Support | Confidence A -> B | Confidence B -> A | Lift",
        *compact, "",
        "INTERPRETATION AND PRIORITIES",
        "Herb & pepper -> ground beef has support 1.60% (120 baskets), confidence 32.35%, and lift 3.292. Ground beef appears about 3.29 times as frequently among herb & pepper baskets as it does overall. This is the strongest association, although its reach is relatively narrow.",
        "Ground beef and spaghetti occur together in 294 baskets (3.92%). Among ground-beef baskets, 39.89% include spaghetti; among spaghetti baskets, 22.51% include ground beef. Lift is 2.291 in either direction. The greater frequency makes this pair a sensible first meal-bundle pilot.",
        "Olive oil -> spaghetti has support 2.29% (172 baskets), confidence 34.82%, and lift 2.000. This provides a pantry-based alternative for coordinated promotions.",
        f"For comparison, the most frequent qualifying positive pair is {broad.antecedent} with {broad.consequent}: support {broad.support:.2%}, confidence {broad.confidence:.2%}, lift {broad.lift:.3f}. High lift is not the same as greatest reach; wider-reaching pairs can also merit tests.", "",
        "CORRESPONDING BUSINESS STRATEGIES"]
    for r in table.itertuples():
        report.append(f"- {r.product_A} + {r.product_B}: {r.recommendation}")
    report += ["", "IMPLEMENTATION AND MEASUREMENT",
        "Start with small, time-limited pilots for ground beef/spaghetti and herb & pepper/ground beef. Use recipe cards, nearby compatible displays or cross-aisle signs while preserving refrigeration requirements. Coordinate inventory so both items are available during promotions.",
        "Compare pilot stores or periods with a suitable control. Track paired-basket rate, incremental units, gross margin after discounts, stockouts and waste. Expand only when incremental margin supports the offer; association alone does not show that a promotion causes extra sales.",
        "These rules describe observed purchasing behavior. They do not prove that products are substitutes, complements or profitable bundles, and results can change with season, pricing or customer mix."]
    (OUT / "data_c_business_deliverable.txt").write_text("\n".join(report), encoding="utf-8")
    print(f"Validated {len(rules)} rules against {n} baskets; wrote business table and deliverable.")


if __name__ == "__main__":
    main()
