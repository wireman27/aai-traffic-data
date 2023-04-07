
"""
Final cleaning
    - Keep only the required columns
    - Correct data types everywhere

For the final checks:
    - For each airport, are all years and months available?
    - Randomly check values of random airports
    - Check if the intl+dom tag is the same everywhere
    - Add the common name of the airport
    
Observations:
    - There are times where dom+intl is not the same for all; I will relegate this to bad parsing,
        like the AGR example in 7-2015-annexure-3.pdf
        like the BLR example in 1-2015-annexure-2.pdf

To Do:
    - [DONE]: Do the final checks - if an airport is intl, it has to be intl everywhere; if domestic, domestic everywhere
    - [DONE]: Check if there are any *gaps* in the data
    - [DONE]: Do a outer join in the 3-table join
    - Go entirely through gaps.csv and make necessary additions
    - Add the manual missing values (these are indicated 'Problematic')
    - Final QC
"""

import functools as ft
import pandas as pd

df1 = pd.read_csv("aircraftmov.csv")
df2 = pd.read_csv("pax.csv")
df3 = pd.read_csv("freight.csv")

dfs = [df1, df2, df3]

df_final = ft.reduce(lambda left, right: pd.merge(left, right, how='outer', on=['iata', 'month', 'year']), dfs)
df_final.to_csv('aai-traffic.csv', index=False)

df = pd.read_csv("./aai-traffic.csv")
df = df[[
    'iata',
    'aircraftmov_intl',
    'aircraftmov_domestic',
    'pax_intl',
    'pax_domestic',
    'freight_intl',
    'freight_domestic',
    'atype_x',
    'atype_y',
    'atype',
    'month',
    'year'
]]

df.rename(columns={
    'atype_x': 'atype_annex2',
    'atype_y': 'atype_annex3',
    'atype': 'atype_annex4'}, inplace=True)

for c in [
    'aircraftmov_intl',
    'aircraftmov_domestic',
    'pax_intl',
    'pax_domestic',
    'freight_intl',
    'freight_domestic']:

    df[c] = df[c].astype(str)\
                 .str.replace(',', '')\
                 .str.replace(')', '')\
                 .str.extract('(\d+)', expand=False)\
                 .astype(float).astype('Int64')

def problematic(row):

    """
    Problematic if types are not the same
    """

    if len(set([row['atype_annex2'], row['atype_annex3'], row['atype_annex4']])) > 1:
        return True
    return False

# Let's identify gaps in the data
gaps = []

for a in df['iata'].unique():
    t = df[df['iata']==a]
    t['msc'] = t['month'] + 12 * t['year']
    mx = t['msc'].max()
    mn = t['msc'].min()
    span = mx - mn
    rows = t.shape[0]
    if span + 1 != rows:
        for v in range(mn, mx):
            if v not in t['msc'].tolist():
                gaps.append({
                    'iata': a,
                    'month': 12 if v % 12 == 0 else v % 12,
                    'year': int(v / 12)
                })

gaps = pd.DataFrame(gaps)
gaps.to_csv('gaps.csv', index=False)


df['problematic'] = df.apply(lambda row: problematic(row), axis=1)
df.to_csv('aai-traffic-for-final-manual.csv', index=False)