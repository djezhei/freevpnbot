import os
from dotenv import load_dotenv


REFERAL_DISCOUNT=10

PANEL_PATH = '/8876'
API_LOGIN_PATH = f'{PANEL_PATH}/login'
API_INBOUNDS = f'{PANEL_PATH}/panel/api/inbounds/get'
API_ADD_CLIENT_PATH = f'{PANEL_PATH}/panel/inbound/addClient'
API_DELETE_CLI = PANEL_PATH + '/panel/inbound/{inbound_id}/delClient/{utid}'

load_dotenv()

YOO_TOKEN = os.environ.get('YOO_TOKEN')
YOO_RECEIVER = os.environ.get('YOO_RECEIVER')
YOO_SUCCESS_URL = os.environ.get('YOO_SUCCESS_URL')

TG_CHAT_ID = os.environ.get('TG_CHAT_ID')
TG_ADMIN_UTID = os.environ.get('TG_ADMIN_UTID')
TG_TOKEN = os.environ.get('TG_TOKEN')
TG_SERVICE_TOKEN = os.environ.get('TG_SERVICE_TOKEN')
TG_SEND_MESSAGE_URL = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage?parse_mode=HTML&disable_web_page_preview=true"
TG_SEND_SERVICE_MESSAGE_URL = f"https://api.telegram.org/bot{TG_SERVICE_TOKEN}/sendMessage?chat_id={TG_ADMIN_UTID}&parse_mode=HTML&disable_web_page_preview=true"
DB_LINK = (f'postgresql+psycopg2://{os.environ.get("DB_USER")}:{os.environ.get("DB_PASS")}'
           f'@{os.environ.get("DB_HOSTNAME")}:{os.environ.get("DB_PORT")}/{os.environ.get("DB_NAME")}')
API_LOGIN = os.environ.get('API_LOGIN')
API_PASS = os.environ.get('API_PASS')

donation_values = [50, 100, 200]

sub_types = {
    0: {
        'name': '30 мин',
        'seconds': 1800,
    },
    1: {
        'name': '1 месяц',
        'seconds': 2592000,
    },
    2: {
        'name': '3 месяца',
        'seconds': 7776000,
    },
    3: {
        'name': '6 месяцев',
        'seconds': 15552000,
    },
}
