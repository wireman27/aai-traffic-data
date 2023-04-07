
"""
Post manual
- Check if something has been tagged as domestic (all the way) when it's actually international
- Create airports list
- Change column names
- Make everything integer

Everything here takes input from the manually updated Google Sheets and then does stuff with it.
*Rename all columns here, and not on Google Sheets*

- Also add code to re-run the gap assessment
"""

import pandas as pd

df = pd.read_csv("./aai-traffic-google-sheets.csv")
df.rename(columns = {'iata': 'airport_code', 'iata_code': 'iata'}, inplace=True)

# Create the airports dataset
airports = df[['name', 'airport_code']].drop_duplicates()
airports.to_csv('airports-from-aai.csv', index=False)

df.drop(columns=['index', 'atype_annex2', 'atype_annex3', 'atype_annex4', 'problematic', 'name', 'iata'], inplace=True)

for c in [
    'aircraftmov_intl', 
    'aircraftmov_domestic',
    'pax_intl',
    'pax_domestic',
    'freight_intl',
    'freight_domestic']:

    df[c].fillna(0, inplace=True)
    df[c] = df[c].astype(int)

df.to_csv('aai-traffic-only-airport-codes.csv', index=False)
