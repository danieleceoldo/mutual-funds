import pathlib
import yaml
import requests
import requests_html
import datetime
import time
import json
import logging
import logging.config



def get_html_table(code):
    try:
        return requests_html.HTMLSession().get(
            'https://www.morningstar.it/it/funds/snapshot'
            '/snapshot.aspx?id=' + code
            ).html.find('table')
    except Exception as excep_inst:
        logger.exception(excep_inst)
        return None



mutual_funds_fname = pathlib.Path('mutual_funds.database.yaml')
if mutual_funds_fname.is_file():
    mutual_funds = yaml.safe_load(mutual_funds_fname.read_text())
else:
    mutual_funds = {}

config = yaml.safe_load(pathlib.Path('config.yaml').read_text())

logger = logging.getLogger(__name__)
logging.config.dictConfig(
        {
            'version': 1,
            'formatters': {
                'minimal': {
                    'format': '{levelname:8} {message}',
                    'style': '{'
                    }
                },
            'handlers': {
                'console': {
                    'class': logging.StreamHandler,
                    'formatter': 'minimal'
                    },
                'file': {
                    'class': logging.FileHandler,
                    'formatter': 'minimal',
                    'filename': \
                            f'{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log',
                    'delay': True,
                    'mode': 'w'
                    }
                },
            'loggers': {
                __name__: {
                    'handlers': ['console', 'file'],
                    'level': logging.INFO
                    }
                }
        }
        )

while True:

    logger.info(f'Mutual funds check at {datetime.datetime.now()}')

    for code in [
        config['mutual_funds'][name]['code']
        for name in config['mutual_funds']
        ]:
        for html_table in [ get_html_table(code) ]:
            if html_table is None:
                continue
            try:
                name = html_table[0].text.splitlines()[0]
            except Exception as excep_inst:
                logger.exception(excep_inst)
                continue
            try:
                date = datetime.datetime.strptime(
                    html_table[3].text.splitlines()[2], '%d/%m/%Y'
                    ).date()
            except Exception as excep_inst:
                logger.exception(excep_inst)
                continue
            try:
                currency = html_table[3].text.splitlines()[3]\
                            .split(u'\xa0')[0]
            except Exception as excep_inst:
                logger.exception(excep_inst)
                continue
            try:
                nav = float(
                           html_table[3].text.splitlines()[3]\
                                   .split(u'\xa0')[1].replace(',', '.')
                           )
            except Exception as excep_inst:
                logger.exception(excep_inst)
                continue
            try:
                variation = float(
                    html_table[3].text.splitlines()[5][:-1].replace(',', '.')
                    )
            except Exception as excep_inst:
                logger.exception(excep_inst)
                continue
            try:
                code_check = config['mutual_funds']\
                        [html_table[0].text.splitlines()[0]]['code']
            except Exception as excep_inst:
                logger.exception(excep_inst)
                continue

            if not name in config['mutual_funds']:
                logger.error(
                        f'fund name from HTML: "{name}" '
                        'is not present in config file.'
                        )
                continue
            if not code == code_check:
                logger.error(
                        f'code read from HTML: {code_check} differs to '
                        f'code read from config file: {code} '
                        f'for fund name: "{name}".'
                        )
                continue

            if name in mutual_funds and date in mutual_funds[name]:
                continue

            mutual_fund_update = {
                    name : {
                        date: {
                            'currency': currency,
                            'NAV': nav,
                            'variation (%)': variation,
                            'code': code
                            }
                    }
                    }

            logger.info('')
            logger.info('-'*80)
            logger.info(f'Mutual funds update at {datetime.datetime.now()}:')
            logger.info('-'*80)
            logger.info('')
            for _ in yaml.safe_dump(mutual_fund_update).splitlines():
                logger.info(_)
            mutual_funds.update(mutual_fund_update)
            mutual_funds_fname.write_text(yaml.safe_dump(mutual_funds))

            alert_message = ''
            if (
                    nav_max := config['mutual_funds'][name]\
                            .get('NAV', {}).get('max')
                    ) and nav > nav_max:
                alert_message = \
                        f'{date} "{name}" NAV {nav} > {nav_max} ( MAX NAV )'
            if (
                    nav_min := config['mutual_funds'][name]\
                            .get('NAV', {}).get('min')
                    ) and nav < nav_min:
                alert_message = \
                        f'{date} "{name}" NAV {nav} > {nav_min} ( MIN NAV )'
            if (
                    max_abs_var := config['mutual_funds'][name]\
                            .get('max_abs_variation')
                    ) and abs(variation) > max_abs_var:
                alert_message = \
                        f'{date} "{name}" NAV Variation {variation} ' \
                        f'( MAX ABS VAR: {max_abs_var} )'

            if alert_message:
                logger.info('')
                logger.info('#'*80)
                logger.info(alert_message)
                logger.info('#'*80)
                logger.info('')

            logger.info('')
            logger.info('-'*80)
            logger.info('')

            time.sleep(60)


    time.sleep(3600)
