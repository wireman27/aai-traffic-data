
"""
This snippet downloads all the files required
and renames them accordingly. It also logs the files
that failed and need to be downloaded manually and then
renamed accordingly.
"""

import json
import re

import requests
from lxml import html

months = {
    'jan': 1,
    'feb': 2,
    'mar': 3,
    'apr': 4,
    'may': 5,
    'june': 6,
    'jun': 6,
    'jul': 7,
    'july': 7,
    'aug': 8,
    'sep': 9,
    'oct': 10,
    'nov': 11,
    'dec': 12
}

for y in range(2014, 2024):
    year = str(y)

    with open(f'./html/{year}.html.json', 'r') as f:
        data = json.loads(f.read())

    h = html.fromstring(data[2]['data'])
    l = h.xpath("//a/@href")
    for link in l:
        d = re.search(r'(.*)2k(\d{2})[Aa]nnex(\d{1})', link.split('/')[-1], re.IGNORECASE)
        try:
            month = d.group(1).lower()
            year = str(int(d.group(2)) + 2000)
            annex = d.group(3)
        except:
            if 'TR' in link or 'Traffic' in link:
                continue
            else:
                print('Error with the following file. Please download manually: ', link)
                continue

        month_digit = months[month]

        filename = f'{month_digit}-{year}-annexure-{annex}.pdf'

        data = 0
        while data == 0:
            page = requests.get(link)
            if len(page.content) < 100:
                print('Failed download, retrying for ', link)
                data = 0
            data = 1

        with open(f'data-raw/{filename}', 'wb') as f:
            f.write(page.content)
        print(f'Completed downloading {filename}')
