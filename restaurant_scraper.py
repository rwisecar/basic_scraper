"""Scrape King County's restaurant inspection DB."""

from bs4 import BeautifulSoup
import io
import sys
import requests

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


def get_inspection_page(**kwargs):
    """Make a request to KC's site, return content in bytes."""
    url = "{}/{}".format(INSPECTION_DOMAIN, INSPECTION_PATH)
    ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'
    headers = {"User-Agent": ua}
    params = INSPECTION_PARAMS.copy()
    for key, val in kwargs.items():
        if key in INSPECTION_PARAMS:
            params[key] = val
    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    return resp.content


def load_inspection_page(filename):
    """Read the data on the disk and return html."""
    f = io.open(filename, 'r+', encoding='utf-8')
    inspection_page = f.read()
    f.close()
    return inspection_page


def create_html_file(content):
    """Take response object's contents in bytes and write to html file."""
    with open('inspection_page.html', 'wb+') as f:
        f.write(content)
    return load_inspection_page('inspection_page.html')


def parse_source(html):
    # Parse the html using BeautifulSoup and html5lib
    parsed = BeautifulSoup(html, "html5lib")
    return parsed


if __name__ == "__main__":
    kwargs = {
        'Inspection_Start': '1/1/2016',
        'Inspection_End': '1/1/2017',
        'Zip_Code': '98115'
    }

    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        html = load_inspection_page('inspection_page.html')
    else:
        html = create_html_file(get_inspection_page(**kwargs))
    doc = parse_source(html)
    print(doc)
