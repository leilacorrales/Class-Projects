from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether

OUT = Path('output/pdf/currency_crisis_project_structure.pdf')
OUT.parent.mkdir(parents=True, exist_ok=True)

navy = colors.HexColor('#17324D')
blue = colors.HexColor('#2E6F95')
light = colors.HexColor('#EEF4F7')
gold = colors.HexColor('#C98B2E')
dark = colors.HexColor('#24313A')

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleCustom', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=21, leading=25, textColor=navy, alignment=TA_LEFT, spaceAfter=5))
styles.add(ParagraphStyle(name='Subtitle', parent=styles['Normal'], fontName='Helvetica', fontSize=9.5, leading=13, textColor=colors.HexColor('#53636D'), spaceAfter=12))
styles.add(ParagraphStyle(name='Section', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=11.5, leading=14, textColor=blue, spaceBefore=7, spaceAfter=4))
styles.add(ParagraphStyle(name='BodyCustom', parent=styles['BodyText'], fontName='Helvetica', fontSize=8.8, leading=11.5, textColor=dark, spaceAfter=3))
styles.add(ParagraphStyle(name='Small', parent=styles['BodyText'], fontName='Helvetica', fontSize=7.8, leading=10, textColor=dark))
styles.add(ParagraphStyle(name='Callout', parent=styles['BodyText'], fontName='Helvetica-Bold', fontSize=9.2, leading=12, textColor=navy))

def p(text, style='BodyCustom'):
    return Paragraph(text, styles[style])

doc = SimpleDocTemplate(str(OUT), pagesize=letter, rightMargin=.55*inch, leftMargin=.55*inch, topMargin=.48*inch, bottomMargin=.45*inch)
story = []
story.append(p('Currency Crisis Prediction: Project Structure', 'TitleCustom'))
story.append(p('A concise four-week data science plan for emerging markets', 'Subtitle'))

question = Table([[p('<b>Research question</b><br/>Can macroeconomic and financial indicators predict currency crises in emerging markets, and do decision trees or random forests improve on a logistic-regression baseline?', 'Callout')]], colWidths=[7.35*inch])
question.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),light),('BOX',(0,0),(-1,-1),.6,blue),('LEFTPADDING',(0,0),(-1,-1),10),('RIGHTPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8)]))
story.append(question)

story.append(p('Project structure', 'Section'))
structure = [
    [p('<b>1. Literature review</b><br/>Summarize traditional early-warning models, logit/probit methods, signal extraction, and recent machine-learning approaches.', 'Small'), p('<b>2. Data and outcome</b><br/>Define a binary crisis label, select 6-10 lagged predictors, and document source, unit, period, and missingness.', 'Small')],
    [p('<b>3. Data preparation</b><br/>Merge the country-time panel, clean missing values and outliers, engineer lags and rates of change, and prevent leakage.', 'Small'), p('<b>4. Modeling</b><br/>Compare a majority-class baseline, logistic regression, one decision tree, and one random forest.', 'Small')],
    [p('<b>5. Evaluation</b><br/>Use a chronological train/validation/test split. Report recall, precision, F1, ROC-AUC, precision-recall AUC, and calibration.', 'Small'), p('<b>6. Interpretation</b><br/>Explain coefficients, tree splits, and random-forest feature importance. Treat importance as predictive, not causal.', 'Small')],
]
t = Table(structure, colWidths=[3.62*inch, 3.62*inch], rowHeights=[.62*inch, .62*inch, .62*inch])
t.setStyle(TableStyle([('GRID',(0,0),(-1,-1),.35,colors.HexColor('#B8C7CF')),('BACKGROUND',(0,0),(-1,-1),colors.white),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
story.append(t)

story.append(p('Four-week schedule', 'Section'))
schedule = [
    [p('<b>Week 1</b>', 'Small'), p('Finalize research question and crisis definition; build literature matrix; choose variables; acquire data; create data dictionary.', 'Small'), p('Question, literature matrix, raw data, variable plan', 'Small')],
    [p('<b>Week 2</b>', 'Small'), p('Clean and merge data; construct lags; inspect missingness, outliers, class imbalance, and crisis frequency; make exploratory plots.', 'Small'), p('Analysis-ready dataset and EDA', 'Small')],
    [p('<b>Week 3</b>', 'Small'), p('Train baseline, logistic regression, decision tree, and random forest; tune modestly; evaluate with rare-event metrics; interpret features.', 'Small'), p('Results tables, plots, model interpretation', 'Small')],
    [p('<b>Week 4</b>', 'Small'), p('Run robustness checks; write the report; prepare slides; practice; rerun the full notebook from start to finish.', 'Small'), p('Final report, code, figures, presentation', 'Small')],
]
st = Table(schedule, colWidths=[.8*inch, 4.55*inch, 2.0*inch])
st.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.white),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#B8C7CF')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),6),('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
story.append(st)

story.append(p('Recommended starting scope', 'Section'))
story.append(p('Use country-time panel data and lag every predictor so only pre-crisis information is used. Begin with reserves, inflation, GDP growth, external debt, current account, export growth, exchange-rate change, and interest-rate differential. Keep the model comparison small and interpretable.', 'BodyCustom'))

story.append(p('Immediate next steps', 'Section'))
story.append(p('1. Write the one-sentence research question.  2. Choose the crisis definition.  3. Create the literature matrix.  4. List candidate variables and sources.  5. Email your professor with this scope and ask for feedback before finalizing the data.', 'BodyCustom'))

story.append(Spacer(1, 6))
story.append(p('Core caution: accuracy alone is misleading when crises are rare. Also, predictive importance does not establish economic causation.', 'Small'))

def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(gold)
    canvas.setLineWidth(1.2)
    canvas.line(doc.leftMargin, .32*inch, letter[0]-doc.rightMargin, .32*inch)
    canvas.setFont('Helvetica', 7.5)
    canvas.setFillColor(colors.HexColor('#6B7880'))
    canvas.drawString(doc.leftMargin, .18*inch, 'Currency crisis prediction project')
    canvas.drawRightString(letter[0]-doc.rightMargin, .18*inch, f'{doc.page}')
    canvas.restoreState()

doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUT.resolve())
