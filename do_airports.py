
"""
This snippet is for creating the list of airports and aliases
"""

import glob
import json
from collections import Counter

import pandas as pd
import tabula
from tqdm import tqdm


def do_airports():

    tables = []
    files = glob.glob('./data-raw/*.pdf')

    for f in tqdm(files, position=0, leave=True):
        pdf = tabula.read_pdf(
                f,
                pages='all',
                lattice=True,
                pandas_options={'header': None}
            )
        try:
            for df in pdf:
                t = df.dropna(axis=1, how='all')

                # Keep only the first 3 columns
                t = t.iloc[:, :2]
                t.columns = ['sl_no', 'airport']
                tables.append(t)
        except:
            print("Issue with ", f)
            continue

    final = pd.concat(tables)

    final = final[pd.notna(final['airport'])]
    final = final[~final['airport'].astype(str).str.contains('\d+', regex=True)]

    airports = final['airport'].tolist()

    with open('airports.json', 'w') as f:
        json.dump(Counter(airports), f)


do_airports()


