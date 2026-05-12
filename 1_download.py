import logging
logging.basicConfig(
    level=logging.DEBUG, format='%(levelname)s - %(funcName)s :: %(lineno)d - %(message)s')
DEBUG = logging.debug
INFO = logging.info
GOOGLE_EXCEL_EXPORT_LINK = (
    'https://docs.google.com/spreadsheets/d/'
    '1aLeaaSirWj7e6NgasEnpVeqK--IIt88o8J9jhzfJag0/'
    'export?exportFormat=xlsx&format=xlsx')
SHEET_TABS = (
    'DIS_25059',
    'eu_aiact',
)
DOCS_FOLDER = '.'

from urllib import request

def download_document() -> None:
    url = GOOGLE_EXCEL_EXPORT_LINK
    # INFO(url)
    try:
        request.urlretrieve(url, f'{DOCS_FOLDER}/spreadsheet.xlsx')
        INFO(f'Downloaded spreadhseet.xlsx')
    except Exception as E:
        logging.error(f'ERROR :: {E}')


def _extract_CSVs():
    import subprocess
    for sheet_name in SHEET_TABS:
        with open(f'{DOCS_FOLDER}/{sheet_name}.csv', 'w') as outfile:
            subprocess.run(["xlsx2csv", f"{DOCS_FOLDER}/spreadsheet.xlsx", "-i", "-n", f"{sheet_name}"], stdout=outfile)
        INFO(f'Wrote {sheet_name}.csv')

INFO('-'*25)
download_document()
_extract_CSVs()
INFO('-'*25)
