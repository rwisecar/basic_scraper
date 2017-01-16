"""Scrape King County's restaurant inspection DB."""

from bs4 import BeautifulSoup
import io
import re
import requests
import sys

"""Constant Global Variables for setting up query."""

INSPECTION_DOMAIN = 'http://info.kingcounty.gov'
INSPECTION_PATH = '/health/ehs/foodsafety/inspections/Results.aspx'
INSPECTION_PARAMS = {
    'Output': 'W',
    'Business_Name': '',
    'Longitude': '',
    'Latitude': '',
    'City': '',
    'Zip_Code': '',
    'Inspection_Type': 'All',
    'Inspection_Start': '',
    'Inspection_End': '',
    'Inspection_Closed_Business': 'A',
    'Violation_Points': '',
    'Violation_Red_Points': '',
    'Violation_Descr': '',
    'Fuzzy_Search': 'N',
    'Sort': 'H',
}


UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'
HEADERS = {"User-Agent": UA}


def get_inspection_page(**kwargs):
    """Make a request to KC's site, return content in bytes."""
    url = INSPECTION_DOMAIN + INSPECTION_PATH
    params = INSPECTION_PARAMS.copy()
    for key, val in kwargs.items():
        if key in INSPECTION_PARAMS:
            params[key] = val
    resp = requests.get(url, params=params, headers=HEADERS, stream=True)
    resp.raise_for_status()
    return resp.content, resp.encoding


def load_inspection_page():
    """Read the data on the disk and return html."""
    f = io.open('inspection_page.html', 'r+')
    content = f.read()
    encoding = 'utf-8'
    f.close()
    return content, encoding


def create_html_file(content):
    """Take response object's contents and write to html file."""
    with open('inspection_page.html', 'w') as f:
        f.write(content)


def parse_source(html, encoding='utf-8'):
    """Parse the html using BeautifulSoup and html5lib"""
    soup = BeautifulSoup(html, "html5lib")
    return soup


def extract_data_listings(html):
    """Parse through listings by divs with a particular id."""
    id_finder = re.compile(r'PR[\d]+~')
    return html.find_all('div', id=id_finder)


def has_two_tds(element):
    """Return True if the element is both a <tr> and has two <td>s."""
    is_true = element.name == 'tr'
    td_children = element.find_all('td', recursive=False)
    has_two = len(td_children) == 2
    return is_true and has_two


def clean_data(td):
    """Clean extra characters off the string we want."""
    data = td.string
    try:
        return data.strip(" \n:-")
    except AttributeError:
        return u""


def extract_restaurant_metadata(element):
    """Store cleaned metadata as a dictionary."""
    metadata_rows = element.find('tbody').findall(
        has_two_tds, recursive=False
    )
    rdata = {}
    current_label = ''
    for row in metadata_rows:
        key_cell, val_cell = row.find_all('td', recursive=False)
        new_label = clean_data(key_cell)
        current_label = new_label if new_label else current_label
        rdata.setdefault(current_label, []).append(clean_data(val_cell))
    return rdata


def is_inspection_row(element):
    """Filter for rows that contain keyword 'inspection'."""
    is_true = element.name == 'tr'
    if not is_true:
        return False
    td_children = element.find_all('td', recursive=False)
    has_four = len(td_children) == 4
    this_text = clean_data(td_children[0]).lower()
    contains_word = 'inspection' in this_text
    does_not_start = not this_text.startswith('inspection')
    return is_true and has_four and contains_word and does_not_start


def extract_score_data(element):
    """Take in a restaurant listing, apply filter to find inspection data."""
    inspection_rows = element.find_all(is_inspection_row)
    samples = len(inspection_rows)
    total = high_score = average = 0
    for row in inspection_rows:
        strval = clean_data(row.find_all('td')[2])
        try:
            intval = int(strval)
        except (ValueError, TypeError):
            samples -= 1
        else:
            total += intval
            high_score = intval if intval > high_score else high_score
    if samples:
        average = total/float(samples)
    data = {
        u'Average Score': average,
        u'High Score': high_score,
        u'Total Inspections': samples
    }
    return data


if __name__ == "__main__":
    kwargs = {
        'Inspection_Start': '1/1/2016',
        'Inspection_End': '1/1/2017',
        'Zip_Code': '98115'
    }
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        html, encoding = load_inspection_page()
    else:
        html, encoding = get_inspection_page(**kwargs)
    doc = parse_source(html, encoding)
    listings = extract_data_listings(doc)
    for listing in listings:
        metadata = extract_restaurant_metadata(listing)
        inspection_row = listing.find_all(is_inspection_row)
        score_data = extract_score_data(listing)
        metadata.update(score_data)
        for key, value in metadata.items():
            print(key, value)
