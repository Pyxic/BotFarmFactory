from telethon.tl.types import InputBotAppShortName

from bots.base.base import BaseFarmer
from bots.hrum.strings import URL_AUTH, URL_INIT
from bots.iceberg.strings import HEADERS


class BotFarmer(BaseFarmer):
    name = "hrummebot"
    extra_code = "ref326124961"  # в случае если рефка вида https://t.me/bot_username?start=ref_code
    app_extra = "ref326124961"  # в случае если рефка вида https://t.me/bot_username?action?param=ref_code (Тут пока не разобрался увы)
    initialization_data = {}  # данные для передачи в инициатор, отличаются в зависимости от типа кнопки входа в бота
    refreshable_token = False  # обновлять ли токен в боте
    codes_to_refresh = (401,)  # при получении этих статусов будет автоматически обновляться токен
    auth_data = None

    initialization_data = dict(peer=name, bot=name, url=URL_INIT, start_param=extra_code)

    def set_headers(self, *args, **kwargs):
        """ Установка заголовков """
        self.headers = HEADERS.copy()

    def authenticate(self, *args, **kwargs):
        """ Аутентифифкация, получения токена, выставление заголовков, заполнение шаблона запроса и тд... """
        init_data = self.initiator.get_auth_data(**self.initialization_data)
        print(init_data)
        result = self.post(URL_AUTH, json={"data": {"initData": init_data["authData"], "platform": "android"}})
        if result.status_code == 200:
            print(result.json())
            return
        self.is_alive = False
        raise KeyError

    def refresh_token(self):
        """ Метод вызывается для обновления токена, при условии что self.refreshable_token == True """
        raise NotImplementedError

    def set_start_time(self):
        """ 
        Метод выставляет время следующего захода фармера. 
        Например время когда закончится фарминг или накопятся тапы 
        """
        raise NotImplementedError

    def farm(self):
        """
        Основной метод, описывающий логику модуля. 
        Покупки, прокачки. Все здесь 
        """
        raise NotImplementedError
