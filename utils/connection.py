from utils.logging import Logger
import aiohttp
from aiohttp.client_exceptions import ContentTypeError
import asyncio


"""
    Класс Connect осуществляет получения данных из api
"""
class Connect:
    def __init__(self, partner, stationary):
        self.logger = Logger('CONNECT DODO_API')
        self.partner = partner
        self.stationary = stationary

    """
        Получение данных из закрытого dodo api с передачей в нее аргументов:
        1. url - адрес необходимого эндпоинта
        2. access - bearer токен доступа партнера
    """
    async def dodo_api(self, url, access, **kwargs) -> dict:
        data = {}
        retry_limit = 5
        retry_delay = 60
        for key, value in kwargs.items():
            if key == '_from':
                data['from'] = value
            else:
                data[key] = value
        headers = {
            "user-agent": 'DodoVkus',
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Bearer {access}"
        }
        async with aiohttp.ClientSession(trust_env=True) as session:
            for i in range(retry_limit):
                async with session.get(url, headers=headers, params=data) as response:
                    try:
                        if response.status == 200:
                            response = await response.json()
                            return response
                        elif response.status == 429:
                            await asyncio.sleep(retry_delay)
                        else:
                            self.logger.error(f'{response.status}|{self.partner}|{self.stationary}|'
                                              f'{url}|{response.content}')
                            return {}
                    except ContentTypeError as e:
                        self.logger.error(f'{e}|{self.partner}|{self.stationary}|{url}')
                        return {}

    """
        Получение данных из глобального dodo api, в качестве аргумента передать эндпоинт
    """
    async def public_dodo_api(self, url) -> dict:
        async with aiohttp.ClientSession(trust_env=True) as session:
            async with session.get(url) as response:
                try:
                    response = await response.json()
                    return response
                except ContentTypeError as e:
                    self.logger.error(f'{e}|{url}|{self.partner}|{self.stationary}')
                    return {}
