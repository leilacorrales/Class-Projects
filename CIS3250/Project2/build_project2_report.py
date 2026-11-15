"""Format the saved Project 2 results in the supplied report-template structure.
Uses the existing results; does not refit models or change their settings.
"""
from pathlib import Path
from html import escape
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.utils import ImageReader

BASE = Path(__file__).resolve().parent
OUT = BASE / "output" / "pdf"
OUT.mkdir(parents=True, exist_ok=True)
A, B, C = [BASE / f"project2_data_{x}_outputs" for x in "abc"]
metrics = pd.read_csv(A / "data_a_model_summary.csv").iloc[0]
coeff = pd.read_csv(A / "data_a_all_coefficients.csv").set_index("predictor")
importance = pd.read_csv(A / "data_a_feature_importance.csv")
evaluation = pd.read_csv(B / "data_b_cluster_evaluation.csv")
profiles = pd.read_csv(B / "data_b_cluster_profiles.csv").set_index("cluster")
pairs = pd.read_csv(C / "data_c_business_associations.csv")
rules = pd.read_csv(C / "data_c_all_association_rules.csv")
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="BodyReport", fontName="Times-Roman", fontSize=11, leading=14.3, spaceAfter=8))
styles.add(ParagraphStyle(name="TitleReport", fontName="Times-Bold", fontSize=13, leading=16, spaceAfter=12))
styles.add(ParagraphStyle(name="HeadReport", fontName="Times-Bold", fontSize=11.5, leading=14, spaceBefore=5, spaceAfter=8, keepWithNext=True))
styles.add(ParagraphStyle(name="CellReport", fontName="Times-Roman", fontSize=9, leading=11))
styles.add(ParagraphStyle(name="SmallReport", fontName="Times-Roman", fontSize=9, leading=11.5, spaceAfter=7))
story = []


def p(text, style="BodyReport"):
    story.append(Paragraph(text, styles[style]))


def h(text):
    p(text, "HeadReport")


def title(text):
    p(text, "TitleReport")


def bullet(text):
    story.append(Paragraph("&#8226; " + text, styles["BodyReport"]))


def table(headers, rows, widths):
    data = [[Paragraph("<b>" + escape(str(x)) + "</b>", styles["CellReport"]) for x in headers]]
    data += [[Paragraph(escape(str(x)), styles["CellReport"]) for x in row] for row in rows]
    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "TOP"), ("LINEABOVE", (0,0), (-1,0), .7, colors.black),
        ("LINEBELOW", (0,0), (-1,0), .5, colors.black), ("LINEBELOW", (0,-1), (-1,-1), .6, colors.black),
        ("LEFTPADDING", (0,0), (-1,-1), 4), ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4)]))
    story.extend([t, Spacer(1,10)])


def picture(path, width, maxheight):
    iw, ih = ImageReader(str(path)).getSize()
    scale = min(width/iw, maxheight/ih)
    story.append(Image(str(path), width=iw*scale, height=ih*scale, hAlign="CENTER"))
    story.append(Spacer(1,8))


def page():
    story.append(PageBreak())


def pf(value):
    return "<0.001" if value < .001 else f"{value:.4f}"


title("Data A: Linear Regression")
h("Results:")
p(f"A multiple linear regression analysis examined <b>Global_Sales</b> using <b>NA_Sales, Year, Publisher, Genre, and Platform</b> in one model. After removing 307 records with missing required values, {int(metrics.n_cleaned):,} games remained. A random 80/20 split assigned {int(metrics.n_train):,} games to training and {int(metrics.n_test):,} to testing (seed 42). Publisher, Genre, and Platform were dummy-coded using training categories only.")
table(["Model statistic", "Result"], [
    ["R-squared (training)",f"{metrics.R_squared_training:.6f}"],
    ["Adjusted R-squared (training)",f"{metrics.Adjusted_R_squared_training:.6f}"],
    ["Overall regression F-statistic",f"F({int(metrics.F_df_numerator)}, {int(metrics.F_df_denominator):,}) = {metrics.F_statistic:.3f}"],
    ["F-test p-value", "<0.001"], ["R-squared (testing)",f"{metrics.Test_R_squared:.6f}"],
    ["Test RMSE / MAE",f"{metrics.Test_RMSE:.6f} / {metrics.Test_MAE:.6f}"]], [280,224])
p(f"The model explains approximately <b>{100*metrics.R_squared_training:.2f}%</b> of training variation in global sales and <b>{100*metrics.Test_R_squared:.2f}%</b> of test variation. Adjusted R-squared accounts for the 570 encoded predictors. The F-test indicates that the predictors are jointly associated with Global_Sales. F denotes the regression statistic, rather than a classification F1 score.")
h("Regression Coefficients")
selected = ["NA_Sales", "Year", "Publisher=Nintendo", "Publisher=Enix Corporation", "Genre=Role-Playing", "Platform=PS3", "Platform=PS4"]
table(["Predictor", "B (unstandardized)", "Beta (standardized)", "p-value"],
    [[name.replace("=", ": "), f"{coeff.loc[name].B_unstandardized:.6f}", f"{coeff.loc[name].Beta_standardized:.6f}", pf(coeff.loc[name].p_value)] for name in selected], [196,112,112,84])
p("The table shows both numeric predictors and selected category coefficients with large absolute standardized effects within their variable. Reference categories are <b>Electronic Arts</b> (Publisher), <b>Action</b> (Genre), and <b>DS</b> (Platform). The full table, including every encoded coefficient and the intercept, is supplied in <b>data_a_all_coefficients.csv</b>.", "SmallReport")

page()
title("Data A: Interpretation and Business Recommendations")
h("Interpretation of the Regression Results")
na, year = coeff.loc["NA_Sales"], coeff.loc["Year"]
bullet(f"<b>NA_Sales (B = {na.B_unstandardized:.4f}; Beta = {na.Beta_standardized:.4f}; p &lt; 0.001).</b> Holding the other variables constant, a one-unit increase in North American sales is associated with an estimated {na.B_unstandardized:.4f}-unit increase in global sales. NA_Sales has the largest standardized coefficient.")
bullet(f"<b>Year (B = {year.B_unstandardized:.4f}; Beta = {year.Beta_standardized:.4f}; p = {year.p_value:.4f}).</b> A one-year increase is associated with a small positive difference in global sales, conditional on the other included predictors.")
bullet("<b>Category differences.</b> Nintendo's estimated B of 0.4532 is relative to Electronic Arts. Role-Playing's B of 0.1037 is relative to Action. PS3's B of 0.1622 and PS4's B of 0.2714 are relative to DS. These conditional differences do not establish causal advantages of a publisher, genre, or platform.")
h("Feature Importance in Numbers")
table(["Feature", "Mean decrease in test R-squared", "SD across permutations"],
    [[r.feature,f"{r.test_R2_decrease_mean:.6f}",f"{r.test_R2_decrease_sd:.6f}"] for r in importance.itertuples()], [150,188,166])
p("Importance is the mean loss of test R-squared across 20 permutations of each original feature. All dummy columns for a category move together. Larger values indicate greater predictive reliance. Values are not percentages and can exceed one if shuffling makes predictions worse than the mean-only benchmark.", "SmallReport")
h("Business Insights and Recommendations for Publishers")
p("<b>1. Use North American sales as a monitoring signal.</b> Its dominant importance supports using observed North American performance when estimating worldwide totals and adjusting distribution or campaign plans. Because NA_Sales is a component of Global_Sales, this finding does not demonstrate pre-release forecasting ability.")
p("<b>2. Treat publisher and platform differences as follow-up evidence.</b> Publisher and Platform contribute more permutation importance than Genre or Year. Review the larger category differences alongside development costs, audience fit, and market conditions before making portfolio choices.")
p("<b>3. Avoid broad claims from small effects.</b> Year and Genre have modest incremental importance. Category p-values are unadjusted across many tests and should be treated as exploratory. Standard OLS inference assumes correctly specified, independent, homoskedastic errors. Fifty-two test records had unseen publishers and were coded as the reference category.")

page()
title("Data B: Customer Segmentation Analysis - K-Means Clustering")
h("1. Feature Selection and Business Logic")
p("The bank wants to understand customer usage patterns and design targeted marketing. Three numeric variables were selected using business reasoning:")
bullet("<b>PURCHASES:</b> captures the amount of purchase activity.")
bullet("<b>CASH_ADVANCE:</b> distinguishes customers who use the card for cash access.")
bullet("<b>BALANCE:</b> describes outstanding balances and separates low-balance from higher-balance usage.")
p("All 8,950 unique customers were retained. The selected variables had no missing or invalid values requiring imputation; the script supports median imputation if these occur. Customer IDs were excluded. Variables were transformed with log(1 + x) to reduce monetary skew, then standardized to equalize their scale. No categorical encoding was needed.")
h("2. Optimal Number of Clusters")
p("K-means models were evaluated for K = 2 through 10 using 20 initializations and seed 42. The highest silhouette score was the primary selection criterion; the elbow curve and Davies-Bouldin index provided cross-checks.")
table(["K", "Inertia", "Silhouette", "Davies-Bouldin"],
    [[int(r.k),f"{r.inertia:,.2f}",f"{r.silhouette_sample_2500:.4f}",f"{r.Davies_Bouldin_index:.4f}"] for r in evaluation.itertuples()], [60,148,148,148])
p("The selected solution is <b>K = 4</b>. It has the highest silhouette score (<b>0.5295</b>) and lowest Davies-Bouldin index (<b>0.6803</b>) among the evaluated models. The endpoint-chord elbow heuristic also selects four clusters. Silhouette uses the same random sample of 2,500 customers for each K; inertia and Davies-Bouldin use all customers.")

page()
title("Data B: Emerging Customer Segments")
p("The four clusters describe distinct patterns of spending, cash access, and balances. Labels are arbitrary; the names below interpret observed behavior. Amounts are medians in the original dataset's monetary units.")
table(["Cluster", "Customers", "Share", "Purchases", "Cash advance", "Balance"],
    [[int(i),f"{int(r.customers):,}",f"{r.percent:.2f}%",f"{r.PURCHASES_median:,.2f}",f"{r.CASH_ADVANCE_median:,.2f}",f"{r.BALANCE_median:,.2f}"] for i,r in profiles.iterrows()], [46,76,65,105,106,106])
segments = [
    ("Cluster 0 - Mixed Purchases and Cash Advances", "This group includes 2,163 customers (24.17%). Median purchases are 619.60, cash advances 1,213.39, and balance 1,852.65. Customers combine purchasing with cash access and have the highest median balance of the four groups.", "Test retention messages and purchase rewards, supported by clear cash-access cost information and optional payment-management tools. Measure incremental purchases, retention, and campaign costs."),
    ("Cluster 1 - Cash-Advance-Focused Customers", "This group includes 2,020 customers (22.57%). Median purchases are zero, cash advances 1,272.31, and balance 1,498.24. These customers primarily use the card for cash access, with minimal purchasing activity.", "Provide clear cost information and optional budgeting or payment reminders. Test a modest purchase-activation offer for interested customers; measure activation, engagement, and retention."),
    ("Cluster 2 - Low-Balance Purchasers", "This group includes 2,033 customers (22.72%). Median purchases are 295.00, cash advances zero, and balance 30.40. Customers make purchases while maintaining low observed balances and little cash-advance usage.", "Test low-cost everyday-purchase rewards and engagement messages. Track active usage, incremental purchases, and incentive cost. Low balances alone do not prove full repayment every period."),
    ("Cluster 3 - Purchase-Focused Customers with Balances", "This group includes 2,734 customers (30.55%). Median purchases are 1,185.47, cash advances zero, and balance 827.53. It is the largest group and has the highest median purchases.", "Test merchant offers or purchase-category rewards, paired with spending summaries and optional reminders. Measure redemption, retention, and net campaign contribution.")]
for name, interpretation, action in segments:
    h(name)
    p("<b>Behavioral characteristics and interpretation:</b> " + interpretation)
    p("<b>Business strategy:</b> " + action)

page()
title("Data B: Cluster Visualization and Implementation")
h("3. Visualization of the Customer Types")
picture(B / "data_b_customer_segments_3d.png", 485, 365)
p("Figure 1. All customers are plotted using the three standardized log-transformed inputs used by K-means. Colors and labels identify the four clusters; black X markers show centroids.", "SmallReport")
p("The figure separates customers with meaningful cash-advance usage (Clusters 0 and 1) from customers with little cash-advance usage (Clusters 2 and 3). Purchase activity differentiates the two cash-advance groups, while balance and purchasing levels distinguish the two groups with little cash usage.")
h("4. Business Recommendations for the Bank")
p("Use the segments to tailor the content and cost of marketing pilots. Compare treated customers with suitable controls and track incremental purchases, offer uptake, retention, and campaign contribution after rewards and communication costs. Expand successful offers and revise those that increase cost without improving outcomes.")
p("These clusters describe behavior; they do not establish income, profitability, creditworthiness, or repayment capacity. Evaluate credit decisions using appropriate separate evidence. Refresh the profiles when customer behavior or product conditions change.")

page()
title("Data C: Market-Basket Analysis")
h("1. Overview of Analysis")
p("The retailer wants to identify valuable product combinations for promotions and store layout. The existing Apriori analysis used <b>7,501 shopping baskets</b>, retaining the first spreadsheet row as a transaction and counting each item once per basket.")
bullet("<b>Minimum support:</b> 1% (at least 76 baskets).")
bullet("<b>Minimum confidence:</b> 20%.")
bullet("<b>Results:</b> 257 frequent itemsets and 162 directional association rules.")
p("All 162 saved rules were checked against the original baskets. Rules were evaluated using support, confidence, and lift. Lift above one indicates a positive association. The thresholds identify useful observed patterns; no statistical significance tests were performed.")
h("2. Most Valuable Product Combinations")
p("The table lists the ten strongest distinct two-product combinations by lift among qualifying positive rules. Reverse directions are combined to avoid duplicate pairs. Confidence is directional; A -&gt; B means the proportion of A baskets that also contain B.")
table(["Antecedent (A)", "Consequent (B)", "Support", "Confidence", "Lift"],
    [[r.product_A,r.product_B,f"{r.support_percent:.2f}%",f"{r.confidence_A_to_B_percent:.2f}%",f"{r.lift:.3f}"] for r in pairs.itertuples()], [122,142,76,90,74])
h("Key Insight")
p("<b>Herb &amp; pepper with ground beef</b> is the strongest association (lift 3.292), while <b>ground beef with spaghetti</b> offers greater observed reach (294 baskets; support 3.92%) and a lift of 2.291. <b>Olive oil with spaghetti</b> provides another practical meal-promotion candidate (172 baskets; support 2.29%).")
p("These are priorities for controlled tests. Prices, margins, and promotion costs were not supplied, so association strength cannot establish which bundle is most profitable.")

page()
title("Data C: Interpretation of Support, Confidence, and Lift")
h("3. Rule Evaluation")
p("<b>Support</b> measures the share of all baskets containing both products. <b>Confidence</b> measures how often B appears among baskets containing A. <b>Lift</b> compares that confidence with B's overall purchase frequency. The same pair has equal lift in both directions but can have very different confidence.")
bullet("<b>Herb &amp; pepper -&gt; ground beef:</b> support 1.60% (120 baskets), confidence 32.35%, lift 3.292. Ground beef appears about 3.29 times as frequently in herb &amp; pepper baskets as it does overall. This is a strong but relatively narrow-reach association.")
bullet("<b>Spaghetti and ground beef:</b> support 3.92% (294 baskets), lift 2.291. Confidence is 22.51% from spaghetti to ground beef and 39.89% in the reverse direction. This pair combines higher reach with strong association.")
bullet("<b>Olive oil -&gt; spaghetti:</b> support 2.29% (172 baskets), confidence 34.82%, lift approximately 2.000. This supports testing pantry-based meal promotions.")
picture(C / "data_c_support_confidence_lift.png", 450, 266)
p("Figure 2. Support versus confidence for all 162 saved rules; color indicates lift. Labels identify the original top ten directional two-item rules. The graph also includes rules involving more than two items.", "SmallReport")
p("For broader reach, spaghetti and mineral water occur together in 5.97% of baskets, with 34.30% confidence from spaghetti to mineral water and lift 1.439. The most frequent pair is therefore different from the highest-lift pair. Association does not prove intent or a causal response to promotion.")

page()
title("Data C: Business Recommendations for the Grocery Store")
h("4. Business Recommendations")
h("A. Cross-Merchandising: Pasta Meal Promotions")
p("Prioritize a <b>spaghetti and ground beef</b> pilot because the pair combines 3.92% support with lift 2.291. Use recipe cards, cross-aisle signs, or coordinated offers. Test olive oil with spaghetti as a pantry alternative (2.29% support; lift about 2.000). Preserve the individual pair evidence rather than assuming that a larger multi-product bundle is equally strong.")
h("B. Targeted Add-On Offers: Seasonings and Beef")
p("Test <b>herb &amp; pepper with ground beef</b> through recipe signage and optional seasoning add-ons. It has the highest lift, but its 120 observed paired baskets indicate smaller reach than the pasta-and-beef combination. Grated cheese with ground beef and olive oil with ground beef are additional meal-oriented tests, with lifts of 2.201 and 2.184 respectively.")
h("C. Meal Ideas Across Produce, Frozen Foods, and Dairy")
p("Test <b>tomatoes with frozen vegetables</b> (lift 2.474) and <b>shrimp with frozen vegetables</b> (lift 2.447) through vegetable-meal and stir-fry messaging. For <b>soup with milk</b> (lift 2.321), use recipe-based cross-aisle reminders. Test olive oil with milk through cooking ideas before offering discounts; the observed association alone does not establish why the products co-occur.")
h("D. Broader-Reach and Occasion-Based Promotions")
p("Use <b>spaghetti with mineral water</b> as a broader-reach meal-and-beverage pilot. Its lift of 1.439 is weaker than the top pairs, but 5.97% support gives it greater observed reach. Red wine with spaghetti (lift 2.096) is an occasion-based option where store policy permits. Avoid inferring shopper income or lifestyle from these baskets.")
h("E. Store Layout and Evaluation")
p("Use nearby compatible displays, shelf signs, or digital recommendations to connect related products while preserving refrigeration and product-handling requirements. Coordinate inventory so both products remain available. Pilot layout changes before making major permanent moves.")
p("Compare pilot stores or periods with suitable controls. Track paired-basket rates, incremental units, gross margin after discounts, stockouts, and waste. Expand only when incremental contribution supports the offer. Refresh the analysis for seasonality and changing prices. The rules describe co-purchasing and do not guarantee that a discount or placement change will increase sales.")
p("<b>Results sources:</b> Saved Data A regression outputs, Data B K-means outputs, and Data C association-rule outputs in the Project2 folder. The supplied template guided report structure; all statistics and conclusions above reflect the current project results.", "SmallReport")


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Times-Roman", 9)
    canvas.drawString(54, 30, "CIS3250 | Project 2 Results")
    canvas.drawRightString(558, 30, str(doc.page))
    canvas.restoreState()


target = OUT / "CIS3250_Project2_Results.pdf"
doc = SimpleDocTemplate(str(target), pagesize=(612,792), rightMargin=54, leftMargin=54,
    topMargin=48, bottomMargin=48, title="CIS3250 Project 2 Results", author="")
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(target)
