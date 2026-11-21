from pathlib import Path
import sys
sys.path.insert(0, r'C:\Users\anici\.codex\visualizations\2026\11\10\01a1c321-f5f5-79d3-bbcb-e9b36ed08351\pdfdeps')
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

OUT = Path('output/pdf/currency_crisis_source_summary.pdf')
OUT.parent.mkdir(parents=True, exist_ok=True)

navy = colors.HexColor('#17324D')
blue = colors.HexColor('#2E6F95')
gold = colors.HexColor('#C98B2E')
light = colors.HexColor('#EEF4F7')
dark = colors.HexColor('#24313A')
muted = colors.HexColor('#53636D')

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleX', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=20, leading=24, textColor=navy, alignment=TA_LEFT, spaceAfter=5))
styles.add(ParagraphStyle(name='SubX', parent=styles['Normal'], fontSize=9, leading=12, textColor=muted, spaceAfter=12))
styles.add(ParagraphStyle(name='H1X', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=13, leading=16, textColor=blue, spaceBefore=9, spaceAfter=5))
styles.add(ParagraphStyle(name='H2X', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=10.5, leading=13, textColor=navy, spaceBefore=6, spaceAfter=3))
styles.add(ParagraphStyle(name='BodyX', parent=styles['BodyText'], fontName='Helvetica', fontSize=8.7, leading=11.2, textColor=dark, spaceAfter=4))
styles.add(ParagraphStyle(name='SmallX', parent=styles['BodyText'], fontName='Helvetica', fontSize=7.5, leading=9.5, textColor=dark, spaceAfter=2))
styles.add(ParagraphStyle(name='CalloutX', parent=styles['BodyText'], fontName='Helvetica-Bold', fontSize=9, leading=12, textColor=navy))

def p(text, style='BodyX'):
    return Paragraph(text, styles[style])

doc = SimpleDocTemplate(str(OUT), pagesize=letter, rightMargin=.55*inch, leftMargin=.55*inch, topMargin=.5*inch, bottomMargin=.48*inch)
story = []
story.append(p('Currency Crisis Sources: Methods and Evidence', 'TitleX'))
story.append(p('A focused guide to the sources provided for an emerging-market currency-crisis project | prepared November 11, 2026', 'SubX'))

box = Table([[p('<b>Key correction for Step 3:</b> The Harvard Business School page is a landing page for the Excel download. The variable is inside the downloaded workbook, under the section or column labeled <b>Currency Crises: Year</b>. It is not necessarily visible in the web page list itself.', 'CalloutX')]], colWidths=[7.35*inch])
box.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),light),('BOX',(0,0),(-1,-1),.6,blue),('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
story.append(box)

story.append(p('1. What “currency_crisis” means in the HBS file', 'H1X'))
story.append(p('Open the Excel file from the HBS page and search the workbook for “Currency Crises”. The relevant field is the historical currency-crisis indicator by country and year. Create a binary outcome: 1 when the country-year is marked as a currency crisis, 0 when the dataset explicitly says no crisis, and missing when the source says no data available. Do not automatically convert “no data available” to 0.', 'BodyX'))
story.append(p('The IMF literature gives a useful benchmark: the Laeven-Valencia approach defines a currency crisis as a nominal depreciation against the U.S. dollar of at least 30 percent and at least 10 percentage points more than the previous year. This definition is a methodological reference; the HBS workbook is the practical source for your outcome variable.', 'BodyX'))

story.append(p('2. What “control” means', 'H1X'))
story.append(p('A control variable is an additional factor included in a model so that the relationship between your main predictors and currency crisis is less likely to be confused with another type of crisis. For example, a banking crisis may cause a currency crisis. If you include banking_crisis as a control, the model asks whether reserves, inflation, debt, and other predictors are associated with currency crises after accounting for whether a banking crisis was also occurring.', 'BodyX'))
story.append(p('A control is not automatically a cause, and adding a control does not prove causality. For your project, banking_crisis and sovereign_debt_crisis should be optional robustness controls, not required predictors in the first model.', 'BodyX'))

story.append(p('3. Source-by-source summary', 'H1X'))

data = [
    [p('<b>Source</b>', 'SmallX'), p('<b>What it is doing</b>', 'SmallX'), p('<b>Assumptions / thresholds</b>', 'SmallX'), p('<b>What it finds or provides</b>', 'SmallX')],
    [p('<b>Claessens and Kose (IMF WP/13/28, 2013)</b><br/>[IMF paper link]', 'SmallX'), p('This is a literature review, not a new predictive model. It organizes evidence on four crisis types: currency, sudden-stop, debt, and banking crises. It reviews theory, empirical identification, consequences, and early-warning prediction methods.', 'SmallX'), p('It assumes crises are multidimensional and that no single indicator captures all crises. It emphasizes that crisis definitions and dating rules affect results. It reports the Laeven-Valencia currency-crisis rule as at least 30% nominal depreciation and at least 10 percentage points above the prior year.', 'SmallX'), p('The authors conclude that crises are often preceded by credit and asset-price booms, but precise timing remains difficult. No single set of indicators reliably predicts every crisis type. They know recurring vulnerabilities; they do not know a universal causal mechanism or a consistently accurate warning rule.', 'SmallX')],
    [p('<b>HBS Global Crises Data by Country</b><br/>[HBS data page]', 'SmallX'), p('This is a compiled historical dataset, not a model. It records crisis years and related historical classifications for more than 70 countries, including currency crises, banking crises, debt defaults, inflation crises, and exchange-rate regimes.', 'SmallX'), p('The page itself does not present one unified statistical model. Definitions come from the historical crisis research assembled by Carmen Reinhart and collaborators. Coverage, definitions, and missingness vary across countries and periods.', 'SmallX'), p('It provides the practical dependent variable for your project: currency_crisis. It also provides possible robustness variables, but you should use only one crisis definition consistently in the main analysis.', 'SmallX')],
    [p('<b>Laeven and Valencia (IMF WP/26/94, 2026)</b><br/>[IMF PDF link]', 'SmallX'), p('This paper updates a systemic banking-crisis database through 2025. It uses textual screening of IMF reports to identify candidate episodes, then expert review and supporting evidence to confirm whether the banking-crisis definition is met.', 'SmallX'), p('A crisis requires significant banking-system distress plus significant policy intervention. Intervention is significant when at least three of six measures are used: deposit freezes or bank holidays, nationalization, restructuring costs, extensive liquidity support, significant guarantees, or significant asset purchases. Examples include liquidity support above 5% of deposits and nonresident liabilities, restructuring costs above 3% of GDP, and asset purchases above 5% of GDP. Crisis duration is truncated at five years.', 'SmallX'), p('It identifies 164 systemic banking crises, including borderline cases, during 1970-2025. It reports crisis dates, policy responses, fiscal costs, and output losses. It is useful for a banking_crisis control, but it is not the right primary source for your currency_crisis outcome.', 'SmallX')],
    [p('<b>ASIS World Bank emerging-market list</b><br/>[ASIS page]', 'SmallX'), p('This is a country-classification page, not a research model or economic dataset. It lists Level 1 and Level 2 emerging-market countries attributed to the World Bank.', 'SmallX'), p('The main assumption is that the listed classification is an acceptable operational definition of your sample. Classifications can change over time, so document the access date and keep the list fixed for your project.', 'SmallX'), p('It gives you the filter for the sample: keep only countries on the emerging-market list. It does not provide crisis outcomes or macroeconomic predictors.', 'SmallX')],
]
t = Table(data, colWidths=[1.55*inch, 1.95*inch, 2.1*inch, 1.75*inch], repeatRows=1)
t.setStyle(TableStyle([('GRID',(0,0),(-1,-1),.35,colors.HexColor('#B8C7CF')),('BACKGROUND',(0,0),(-1,0),light),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
story.append(t)

story.append(p('4. Data origins', 'H1X'))
story.append(p('HBS: the page says the data were collected over many years by Carmen Reinhart and coauthors, including Ken Rogoff, Christoph Trebesch, and Vincent Reinhart. The page provides the Excel download.', 'BodyX'))
story.append(p('IMF 2013: a review of published theory and empirical literature. It discusses crisis measures from several studies, including Laeven and Valencia, Reinhart and Rogoff, Kaminsky and Reinhart, and others. It is not a single newly collected panel dataset.', 'BodyX'))
story.append(p('IMF 2026: the authors screen IMF Article IV reports, technical-assistance reports, and financial-sector stability assessments, then supplement this with news articles, central-bank communications, and national technical reports. Fiscal costs are collected from official country publications, supranational agencies, and IMF staff reports.', 'BodyX'))
story.append(p('ASIS: the page reproduces an emerging-market country list attributed to the World Bank and links to World Bank classification information. It should be treated as a sample-selection source, not as evidence for the crisis mechanism.', 'BodyX'))

story.append(p('5. What the sources know and do not know', 'H1X'))
know = [
    [p('<b>They know</b>', 'SmallX'), p('Crisis episodes often coincide with credit booms, asset-price increases, external imbalances, banking stress, and policy intervention. Crisis types can overlap. Historical crisis datasets can identify recurring patterns and provide country-year labels.', 'SmallX')],
    [p('<b>They do not know</b>', 'SmallX'), p('A single universal predictor set, the exact causal trigger for every crisis, or a rule that can reliably predict the precise timing of all crises. Crisis dating is partly definition-dependent, and data coverage and measurement quality vary across countries.', 'SmallX')],
]
kt = Table(know, colWidths=[1.2*inch, 6.15*inch])
kt.setStyle(TableStyle([('GRID',(0,0),(-1,-1),.35,colors.HexColor('#B8C7CF')),('BACKGROUND',(0,0),(0,-1),light),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
story.append(kt)

story.append(p('6. Citation counts', 'H1X'))
story.append(p('Citation counts are database-specific and change over time. The counts below are reported conservatively from the public indexes located for this review, not as a universal Google Scholar total.', 'BodyX'))
cit = [
    [p('<b>Item</b>', 'SmallX'), p('<b>Count located</b>', 'SmallX'), p('<b>How to interpret it</b>', 'SmallX')],
    [p('Claessens and Kose, “Financial Crises: Explanations, Types, and Implications” (2013)', 'SmallX'), p('At least 4 citing works listed by RePEc/CitEc', 'SmallX'), p('This is a lower, index-specific count; other databases may show more.', 'SmallX')],
    [p('Laeven and Valencia, “Systemic Banking Crises Database: An Update” (2012/2013 publication lineage)', 'SmallX'), p('102 listed by OUCI; 140 shown on an SSRN author page for the item', 'SmallX'), p('Counts differ because indexes identify versions and citations differently.', 'SmallX')],
    [p('Laeven and Valencia, “Systemic Banking Crises Database: 1970-2025” (2026)', 'SmallX'), p('No reliable established count found; it is newly published', 'SmallX'), p('Treat the count as near zero or very low until citation indexes update.', 'SmallX')],
    [p('HBS dataset page and ASIS classification page', 'SmallX'), p('Not research papers; paper citation counts do not apply', 'SmallX'), p('Cite the pages as data/classification sources.', 'SmallX')],
]
ct = Table(cit, colWidths=[2.75*inch, 1.65*inch, 2.95*inch], repeatRows=1)
ct.setStyle(TableStyle([('GRID',(0,0),(-1,-1),.35,colors.HexColor('#B8C7CF')),('BACKGROUND',(0,0),(-1,0),light),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
story.append(ct)

story.append(p('7. How this applies to your project', 'H1X'))
story.append(p('Use HBS Currency Crises: Year as the main outcome, ASIS/World Bank as the sample filter, and World Bank macroeconomic indicators as predictors. Use IMF 2013 to justify your definitions and variable choices. Add IMF 2026 banking_crisis only as an optional control or robustness check.', 'BodyX'))
story.append(p('<b>Recommended model statement:</b> “Using emerging-market country-year data, I estimate whether lagged macroeconomic indicators predict the probability of a currency crisis. I include banking-crisis status as an optional control to distinguish currency-crisis risk from broader financial-system distress.”', 'CalloutX'))

story.append(p('Sources', 'H1X'))
sources = [
    'Claessens, Stijn, and M. Ayhan Kose. 2013. Financial Crises: Explanations, Types, and Implications. IMF Working Paper 13/28. https://www.imf.org/-/media/websites/imf/imported-full-text-pdf/external/pubs/ft/wp/2013/_wp1328.pdf',
    'Harvard Business School. Global Crises Data by Country. https://www.hbs.edu/behavioral-finance-and-financial-stability/data/Pages/global.aspx',
    'Laeven, Luc, and Fabian Valencia. 2026. Systemic Banking Crises Database: 1970-2025. IMF Working Paper 26/94. https://www.imf.org/-/media/files/publications/wp/2026/english/wpiea2026094-source-pdf.pdf',
    'ASIS International. Emerging Markets by the World Bank. https://www.asisonline.org/membership/join/emerging-markets/',
]
for s in sources:
    story.append(p(s, 'SmallX'))

def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(gold)
    canvas.setLineWidth(1.1)
    canvas.line(doc.leftMargin, .32*inch, letter[0]-doc.rightMargin, .32*inch)
    canvas.setFont('Helvetica', 7.2)
    canvas.setFillColor(muted)
    canvas.drawString(doc.leftMargin, .18*inch, 'Currency crisis source summary')
    canvas.drawRightString(letter[0]-doc.rightMargin, .18*inch, f'{doc.page}')
    canvas.restoreState()

doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUT.resolve())
