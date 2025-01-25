import pathlib
import yaml
import requests_html

mutual_funds_update = {
        html_table[0].text.splitlines()[0]:
        {
            'date': html_table[3].text.splitlines()[2],
            'currency': html_table[3].text.splitlines()[3].split(u'\xa0')[0],
            'NAV': html_table[3].text.splitlines()[3].split(u'\xa0')[1],
            'variation': html_table[3].text.splitlines()[5]
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

if pathlib.Path('mutual_funds.yaml').is_file():
    mutual_funds = yaml.safe_load(pathlib.Path('mutual_funds.yaml').read_text())
else:
    mutual_funds = []
mutual_funds += [mutual_funds_update]
pathlib.Path('mutual_funds.yaml').write_text(yaml.safe_dump(mutual_funds))
