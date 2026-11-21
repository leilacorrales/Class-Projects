from pathlib import Path
import sys
import re
import requests
import pandas as pd

# sys.path.insert(0, r'C:\Users\anici\.codex\visualizations\2026\11\10\01a1c321-f5f5-79d3-bbcb-e9b36ed08351\xlsxdeps')

ROOT = Path(__file__).parent
RAW = ROOT / 'raw_data'
OUT = ROOT / 'output' / 'data'
RAW.mkdir(exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

HBS_URL = 'https://www.hbs.edu/behavioral-finance-and-financial-stability/Documents/ChartData/MapCharts/20160923_global_crisis_data.xlsx'
HBS_PATH = RAW / 'hbs_crises.xlsx'
if not HBS_PATH.exists():
    response = requests.get(HBS_URL, timeout=120)
    response.raise_for_status()
    HBS_PATH.write_bytes(response.content)

def norm(value):
    text = '' if pd.isna(value) else str(value).strip().lower()
    text = text.replace('&', 'and')
    return re.sub(r'[^a-z0-9]+', ' ', text).strip()

advanced = {
    'andorra','australia','austria','belgium','canada','croatia','cyprus','czech republic',
    'denmark','estonia','finland','france','germany','greece','hong kong sar','iceland',
    'ireland','israel','italy','japan','korea','latvia','lithuania','luxembourg','macao sar',
    'malta','the netherlands','new zealand','norway','portugal','puerto rico','san marino',
    'singapore','slovak republic','slovenia','spain','sweden','switzerland','taiwan province of china','taiwan',
    'united kingdom','united states'}

hbs = pd.read_excel(HBS_PATH)
hbs.columns = [str(c).strip() for c in hbs.columns]
hbs = hbs.rename(columns={'Currency Crises': 'currency_crisis_raw'})
hbs['Country'] = hbs['Country'].astype('string').str.strip()
hbs['year'] = pd.to_numeric(hbs['Year'], errors='coerce')
hbs['currency_crisis_raw'] = pd.to_numeric(hbs['currency_crisis_raw'], errors='coerce')
hbs = hbs[hbs['Country'].notna() & hbs['year'].notna()].copy()
hbs['country_name'] = hbs['Country'].astype(str).str.strip()
hbs['country_norm'] = hbs['country_name'].map(norm)
hbs['year'] = hbs['year'].astype(int)
hbs['currency_crisis'] = hbs['currency_crisis_raw'].apply(lambda x: 1 if x in (1, 2) else (0 if x == 0 else pd.NA)).astype('Int64')
hbs_out = hbs[['country_name','country_norm','year','currency_crisis','currency_crisis_raw']].drop_duplicates(['country_name','year'])
hbs_out.to_csv(RAW / 'hbs_currency_crisis_clean.csv', index=False)

country_rows = []
page = 1
while True:
    payload = requests.get(f'https://api.worldbank.org/v2/country?format=json&per_page=400&page={page}', timeout=120).json()
    if len(payload) < 2 or not payload[1]:
        break
    country_rows.extend(payload[1])
    if page >= int(payload[0].get('pages', page)):
        break
    page += 1
country_map = pd.DataFrame(country_rows)
country_map['country_norm'] = country_map['name'].map(norm)
country_map = country_map[['id','name','country_norm']].drop_duplicates('country_norm')
hbs_out = hbs_out.merge(country_map, on='country_norm', how='left').rename(columns={'id':'country_code','name':'wb_country_name'})

name_overrides = {
    'bolivia': 'BO', 'brunei': 'BN', 'cape verde': 'CV', 'congo democratic republic of the': 'CD',
    'congo republic of the': 'CG', 'iran': 'IR', 'laos': 'LA', 'micronesia': 'FM',
    'myanmar': 'MM', 'russia': 'RU', 'syria': 'SY', 'taiwan': 'TW', 'tanzania': 'TZ',
    'turkey': 'TR', 'venezuela': 'VE', 'vietnam': 'VN', 'yemen': 'YE',
    "cote d ivoire": 'CI', "coted ivoire": 'CI', "coted'ivoire": 'CI', 'egypt': 'EG'}

hbs_out['country_code'] = hbs_out.apply(lambda r: name_overrides.get(r['country_norm'], r['country_code']), axis=1)
hbs_out['imf_advanced'] = hbs_out['country_norm'].isin(advanced)
hbs_out['emerging_developing'] = (~hbs_out['imf_advanced']).astype(int)

indicators = {
    'inflation': 'FP.CPI.TOTL.ZG',
    'GDP_growth': 'NY.GDP.MKTP.KD.ZG',
    'reserves': 'FI.RES.TOTL.CD',
    'external_debt': 'DT.DOD.DECT.GN.ZS',
    'current_account': 'BN.CAB.XOKA.GD.ZS',
    'export_growth': 'NE.EXP.GNFS.KD.ZG',
    'exchange_rate': 'PA.NUS.FCRF',}

def get_wdi(code):
    rows = []
    page = 1
    while True:
        url = f'https://api.worldbank.org/v2/country/all/indicator/{code}?date=1970:2025&format=json&per_page=20000&page={page}'
        payload = requests.get(url, timeout=120).json()
        if len(payload) < 2 or not payload[1]:
            break
        rows.extend(payload[1])
        if page >= int(payload[0].get('pages', page)):
            break
        page += 1
    result = pd.DataFrame(rows)
    result = result.rename(columns={'countryiso3code':'country_code','date':'year','value':code})
    result['year'] = pd.to_numeric(result['year'], errors='coerce').astype('Int64')
    return result[['country_code','year',code]]

macro = None
for variable, code in indicators.items():
    current = get_wdi(code).rename(columns={code: variable})
    macro = current if macro is None else macro.merge(current, on=['country_code','year'], how='outer')
    current.to_csv(RAW / f'wdi_{variable}.csv', index=False)

macro['year'] = macro['year'].astype(int)
panel = hbs_out.merge(macro, on=['country_code','year'], how='left')
panel = panel[(panel['emerging_developing'] == 1) & panel['year'].between(1970, 2016)].copy()
panel = panel.sort_values(['country_code','year'])
panel['exchange_rate_change'] = panel.groupby('country_code')['exchange_rate'].pct_change() * 100

predictors = ['inflation','GDP_growth','reserves','external_debt','current_account','export_growth','exchange_rate_change']
final_cols = ['country_code','country_name','year','currency_crisis','currency_crisis_raw','emerging_developing'] + predictors
panel[final_cols].to_csv(OUT / 'currency_crisis_emerging_markets_panel.csv', index=False)

dictionary = pd.DataFrame([
    ['country_code','Identifier','ISO-3 country code','World Bank country metadata','Merge key'],
    ['year','Identifier','Calendar year','HBS and World Bank','Merge key; study period 1970-2016'],
    ['currency_crisis','Outcome','1 if HBS raw code is 1 or 2; 0 if raw code is 0','HBS Global Crises Data','Main dependent variable'],
    ['inflation','Predictor','Consumer-price inflation, annual percent','World Bank WDI FP.CPI.TOTL.ZG','Observed year-level value; no lag applied'],
    ['GDP_growth','Predictor','GDP growth, annual percent','World Bank WDI NY.GDP.MKTP.KD.ZG','Observed year-level value; no lag applied'],
    ['reserves','Predictor','Total reserves including gold, current US dollars','World Bank WDI FI.RES.TOTL.CD','Observed year-level value; no lag applied'],
    ['external_debt','Predictor','External debt stocks, percent of GNI','World Bank WDI DT.DOD.DECT.GN.ZS','Observed year-level value; no lag applied'],
    ['current_account','Predictor','Current-account balance, percent of GDP','World Bank WDI BN.CAB.XOKA.GD.ZS','Observed year-level value; no lag applied'],
    ['export_growth','Predictor','Export growth, annual percent','World Bank WDI NE.EXP.GNFS.KD.ZG','Observed year-level value; no lag applied'],
    ['exchange_rate','Predictor','Local currency units per US dollar','World Bank WDI PA.NUS.FCRF','Used to calculate depreciation'],
    ['exchange_rate_change','Predictor','Annual percent change in local currency per US dollar','Calculated from exchange_rate','Observed year-level value; no lag applied'],
    ['emerging_developing','Sample flag','1 for HBS country not in IMF WEO advanced-economy list','IMF WEO Groups and Aggregates','Sample filter'],
], columns=['variable','role','definition','source','use'])
dictionary.to_csv(OUT / 'currency_crisis_data_dictionary.csv', index=False)

readme = OUT / 'README.txt'
readme.write_text('''Currency Crisis Emerging-Market Panel\n\nStudy period: 1970-2016. The HBS source file ends in 2016, so later years are not available from this outcome source.\n\nOutcome: HBS Global Crises Data, Currency Crises field. Raw codes are retained in currency_crisis_raw; codes 1 and 2 are coded as currency_crisis=1, code 0 as 0.\n\nSample: HBS countries not in the IMF WEO advanced-economy list. IMF WEO Groups and Aggregates: https://data.imf.org/en/Datasets/WEO/Groups-and-Aggregates-October-2024\n\nPredictors: World Bank WDI API indicators. Source: https://data.worldbank.org/\n\nImportant limitation: the IMF WEO download endpoint was blocked during this run, so the country sample was implemented as the complement of the IMF advanced-economy list using the official IMF Groups and Aggregates page. Review country names and codes before modeling.\n\nNo lagged variables are included.\n''', encoding='utf-8')

print('Rows:', len(panel))
print('Countries:', panel['country_code'].nunique())
print('Crisis rows:', int(panel['currency_crisis'].fillna(0).sum()))
print('Output:', OUT / 'currency_crisis_emerging_markets_panel.csv')
