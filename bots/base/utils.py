import logging
from .strings import URL_CHECK_IP, MSG_BAD_RESPONSE, MSG_PROXY_CHECK_ERROR, MSG_PROXY_CONNECTION_ERROR, \
    MSG_PROXY_IP, MSG_SESSION_ERROR
from time import sleep
from requests import get as requests_get
from dateutil import tz, parser

log_format = "%(asctime)s %(levelname)s %(message)s"
logging.basicConfig(level=logging.INFO, format=log_format)

file_handler = logging.FileHandler('debug.log')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(log_format)
debug_logger = logging.getLogger("debug_logger")
for handler in debug_logger.handlers:
    handler.setFormatter(formatter)
debug_logger.setLevel(logging.DEBUG)
debug_logger.addHandler(file_handler)


def check_proxy(proxies):
    try:
        response = requests_get(URL_CHECK_IP, proxies=proxies)
        if response.status_code == 200:
            ip = response.json()['origin']
            logging.info(MSG_PROXY_IP.format(ip=ip))
            return ip
        else:
            logging.error(MSG_PROXY_CHECK_ERROR.format(status_code=response.status_code))
    except Exception as error:
        logging.error(MSG_PROXY_CONNECTION_ERROR.format(error=error))


def retry(func):
    def wrapper(*args, **kwargs):
        self = args[0]
        while True:
            try:
                result = func(*args, **kwargs)
                if result.status_code not in (200, 201, 202):
                    if result.status_code == 429:
                        self.log(MSG_BAD_RESPONSE.format(status=result.status_code, text=result.text))
                        sleep(10)
                        continue
                    elif result.status_code in (401, 403):
                        if result.status_code == 401 and self.refreshable_token:
                            self.refresh_token()
                            continue
                        self.log(MSG_BAD_RESPONSE.format(status=result.status_code, text=result.text))
                        raise Exception(f"code: {result.status_code} {result.text}")
                return result
            except Exception as error:
                self.log(MSG_SESSION_ERROR.format(error=error))
                sleep(3)
    return wrapper


def to_localtz_timestamp(zulutime: str):
    return parser.parse(zulutime).astimezone(tz.tzlocal()).timestamp()


def api_response(func):
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs)
        if response.status_code == 200:
            return response.json() if response.text else {"ok": True} # Костыль, если вернуло 200 и пустое тело
        else:
            return {}
    return wrapper

