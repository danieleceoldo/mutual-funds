import pathlib
import yaml
import requests
import requests_html
import datetime
import time
import json



mutual_funds_fname = pathlib.Path('mutual_funds.database.yaml')
if mutual_funds_fname.is_file():
    mutual_funds = yaml.safe_load(mutual_funds_fname.read_text())
else:
    mutual_funds = {}

config = yaml.safe_load(pathlib.Path('config.yaml').read_text())


while True:

    print()
    print('--------------------------------------------------')
    print(f'Mutual funds update at {datetime.datetime.now()}:')
    print('--------------------------------------------------')
    print()

    # TODO check for errors
    mutual_funds_update = {
            html_table[0].text.splitlines()[0]: {
                datetime.datetime.strptime(
                    html_table[3].text.splitlines()[2],
                    '%d/%m/%Y'
                    ).date(): {
                    'currency': html_table[3].text.splitlines()[3]\
                            .split(u'\xa0')[0],
                    'NAV': float(
                               html_table[3].text.splitlines()[3]\
                                       .split(u'\xa0')[1].replace(',', '.')
                               ),
                    'variation (%)': float(
                        html_table[3].text.splitlines()[5][:-1]\
                                .replace(',', '.')
                        ),
                    'code': config['mutual_funds']\
                            [html_table[0].text.splitlines()[0]]['code']
                    }
            }
            for html_table in [
                requests_html.HTMLSession().get(
                    'https://www.morningstar.it/it/funds/snapshot'
                    '/snapshot.aspx?id=' + fund_code
                    ).html.find('table')
                for fund_code in [
                    config['mutual_funds'][fund_name]['code']
                    for fund_name in config['mutual_funds']
                    ]
                ]
            }

    print(yaml.safe_dump(mutual_funds_update), end='')
    print()
    print('--------------------------------------------------')
    print()

    for fund_name in mutual_funds_update:
        mutual_fund = mutual_funds.get(fund_name, {})
        mutual_fund.update(mutual_funds_update[fund_name])
        date, data = mutual_funds_update[fund_name].popitem()
        #threshold_value = 3
        #if data['NAV'] < threshold_value:
        #    url = 'https://api.telegram.org/bot' \
        #            + config['telegram']['token'] \
        #            + '/sendMessage?chat_id=' \
        #            + config['telegram']['chat_id'] \
        #            + '&text=' \
        #            + f'Mutual Fund "{fund_name}" NAV down {threshold_value} ' \
        #            + data['currency']
        #    print(json.dumps(requests.get(url).json(), indent=4))
        mutual_funds.update({fund_name: mutual_fund})
    # TODO DEBUG
    mutual_funds_fname.write_text(yaml.safe_dump(mutual_funds))

    time.sleep(3600)
