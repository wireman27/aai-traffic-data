import glob
import json
import logging
import re
import traceback

import pandas as pd
import tabula
from tqdm import tqdm

logging.basicConfig(
    level=logging.ERROR,
    filename='app.log',
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    force=True
)

"""
Issues:
    - Cell borders missing in some cases (
        11-2020-annexure-3.pdf,
        6-2020-annexure-3.pdf)
    - Nagpur, Nagparu issue in 9-2022-annexure-3.pdf
    - Really spooky issue with AGR in 7-2015-annexure-3.pdf
"""

"""
What we can do here is for each airport, get a list of 3 values.
We know that:
    - the first value is international freight/pax
    - the second value is domestic freight/pax
    - the final value is total freight/pax
"""

"""
There will be 3 massive tables for each data type.
Once these 3 massive tables are ready, they will be merged on 
airport+month+year
"""


def construct_airport_mappings(f):

    """
    A tab-delimited file with first element in each line being the IATA code
    and the rest being the aliases

    The mappings file will have the following format:
        {
            aai_1: iata_1,
            aai_2: iata_1,
            aai_3: iata_1
        }
    """

    with open(f, 'r') as f:
        data = json.loads(f.read())

    return data


airport_mappings = construct_airport_mappings('./airport_mappings_condensed-open-ai.json')

mapping = {
    '2': 'aircraftmov',
    '3': 'pax',
    '4': 'freight'
}


def get_iata(row):

    """
    Given an airport name as given by AAI,
    map the correct IATA code
    """

    aai = row['aai']
    aai = re.sub(r'[^\x00-\x7f]', r'', aai)
    aai = aai.replace('(', '').replace(')', '').lower().strip()

    try:
        iata = airport_mappings[aai]
    except:
        if aai == 'airport' or aai == 'for the  month' or aai == 'for themonth':
            pass
        else:
            logging.error(f'Airport resolution problem with {aai}')
        return None

    return iata


def create_sub_table(pdf_file):

    """
    Given a singular PDF file which contains data for a given month
    in a given year for a given data type (freight/passengers/aircraft movements),
    create a table with the following columns:
        - airport
        - month
        - year
        - <data_type>_intl
        - <data_type>_domestic
        
    Filename convention:
        - <datatype>-<month>-<year>.pdf
    """

    el = pdf_file.split('-')
    data_type = mapping[el[3].split('.')[0]]
    month = el[0]
    year = el[1]

    tables = []

    pdf = tabula.read_pdf(
        f'./data-raw/{pdf_file}',
        pages='all',
        lattice=True,
        pandas_options={'header': None}
    )

    for df in pdf:

        # Remove all columns which are useless
        t = df.dropna(axis=1, how='all')

        # To deal with 8-2017-annexure-3.pdf
        if t.shape[1] < 7 and t.shape[0] < 5:
            # If there are less than 7 columns
            # and less than 5 rows
            # right at the outset, we know it's a crap table to begin with
            continue

        # To deal with the special case in 9-2022-annexure-3.pdf
        for x in t.columns:
            bad_rt = pd.isna(t[[x]]).value_counts(normalize=True)
            try:
                bad_ratio = bad_rt[True]
            except:
                bad_ratio = 0
#             if pd.isna(t[[x]].loc[5:]).all().all() == True:
#                 t.drop(columns=x, inplace=True)
            if bad_ratio > 0.5:
                t.drop(columns=x, inplace=True)

        if t.shape[1] < 3:
            logging.error(f"A table in {pdf_file} was not added")
            continue

        # Keep only the first 3 columns
        t = t.iloc[:, :3]
        t.columns = ['sl_no', 'aai', 'value']

        tables.append(t)

    final = pd.concat(tables)
    final = final[pd.notna(final['aai'])]
    final = final[~final['aai'].astype(str).str.contains('\d+', regex=True)]

    final['iata'] = final.apply(lambda row: get_iata(row), axis=1)

    airports = set(final['iata'])

    data = []

    for a in airports:

        s = final[final['iata']==a]

        # Placeholder for examining airports
        values = s['value'].tolist()
        if len(values) == 2:
            atype = 'dom'
            data.append({
                'iata': a,
                f'{data_type}_domestic': values[0],
                f'{data_type}_intl': None,
                'month': str(month),
                'year': str(year),
                'aai': s['aai'].iloc[0],
                'atype': atype
            })

        elif len(values) == 3:
            atype = 'intl+dom'
            data.append({
                'iata': a,
                f'{data_type}_domestic': values[1],
                f'{data_type}_intl': values[0],
                'month': str(month),
                'year': str(year),
                'aai': s['aai'].iloc[0],
                'atype': atype
            })
        elif len(values) == 1:
            logging.error(f'All values of airport {a} not picked up in file {pdf_file}')

    return pd.DataFrame(data)


def do():

    """
    When logging things, we need to know:
        - Which files failed
        - Which 'airports' didn't have an appropriate IATA code
    """

    # Let's do just aircraft pax first
    for annex in ['2', '3', '4']:
        df_all = []
        datatype = mapping[annex]
        files = glob.glob(f'./data-raw/*-annexure-{annex}.pdf')
        for f in tqdm(files, position=0, leave=True):
            filename = f.split('/')[-1]
            try:
                df = create_sub_table(filename)
                df_all.append(df)
            except Exception as e:
                traceback.print_exc()
                logging.error(f'Something totally amiss with file {filename}')
        f = pd.concat(df_all)
        f.to_csv(f'./{datatype}.csv', index=False)

do()
