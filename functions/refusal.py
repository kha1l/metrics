from utils.logging import Logger
from utils.connection import Connect
from utils.classes import BaseGroup

'''
    Набор метрик с эндпоинта отказы /accounting/cancelled-sales:
    1. amount_refusal - сумма заказов
    2. percent_refusal - процент отказов от выручки
'''
class Refusal(BaseGroup):
    def __init__(self):
        self.amount_refusal = 0
        self.percent_refusal = 0
        self.logger = Logger('REFUSAL')

    async def app(self, revenue):
        skip = 0
        take = 0
        reach = False
        conn = Connect(self.data['partner_id'], self.data['name'])
        while not reach:
            response = await conn.dodo_api(f'https://api.dodois.{self.data["properties"]}/accounting/cancelled-sales',
                                           self.data["access"], units=self.data["uuid"],
                                           _from=self.date_start, to=self.date_end,
                                           skip=skip, take=take)
            skip += take
            try:
                for refusal in response['cancelledSales']:
                    self.amount_refusal += refusal['price']
            except Exception as e:
                self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
            try:
                if response['isEndOfListReached']:
                    reach = True
            except Exception as e:
                reach = True
                self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
        self.amount_refusal = round(self.amount_refusal, 0)
        try:
            self.percent_refusal = round(self.amount_refusal / revenue * 100, 2)
        except ZeroDivisionError:
            self.percent_refusal = 0
        self.logger.info(f'{self.data["partner_id"]} | {self.data["name"]} | OK')
