import pathlib
import yaml
import requests_html
import datetime
import time



mutual_funds_fname = pathlib.Path('mutual_funds.database.yaml')
if mutual_funds_fname.is_file():
    mutual_funds = yaml.safe_load(mutual_funds_fname.read_text())
else:
    mutual_funds = {}


while True:

    print()
    print('--------------------------------------------------')
    print(f'Mutual funds update at {datetime.datetime.now()}:')
    print('--------------------------------------------------')
    print()

    mutual_funds_update = {
            html_table[0].text.splitlines()[0]: {
                datetime.datetime.strptime(
                    html_table[3].text.splitlines()[2],
                    '%d/%m/%Y'
                    ).date(): {
                    'currency': html_table[3].text.splitlines()[3].split(u'\xa0')[0],
                    'NAV': html_table[3].text.splitlines()[3].split(u'\xa0')[1],
                    'variation': html_table[3].text.splitlines()[5]
                    }
            }
            for html_table in [
                requests_html.HTMLSession().get(
                    'https://www.morningstar.it/it/funds/snapshot/snapshot.aspx?id='
                    + fund_code
                    ).html.find('table')
                for fund_code in [
                    '0P0000VHLM',
                    '0P0000VHMS',
                    '0P0000VHO3',
                    '0P0000VHO7',
                    '0P0000VHOM',
                    'F0GBR05VWX',
                    'F0GBR064XS',
                    '0P0000MWCO',
                    'F0000026XE'
                    ]
                ]
            }

    print(yaml.safe_dump(mutual_funds_update), end='')
    print()
    print('--------------------------------------------------')
    print()

    for _ in mutual_funds_update:
        mutual_fund = mutual_funds.get(_, {})
        mutual_fund.update(mutual_funds_update[_])
        mutual_funds.update({_: mutual_fund})
    mutual_funds_fname.write_text(yaml.safe_dump(mutual_funds))

    time.sleep(5)
