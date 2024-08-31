from utils.logging import Logger
from utils.connection import Connect
from datetime import timedelta, date
from utils.classes import BaseGroup


'''
    Набор метрик с эндпоинта списания /accounting/write-offs/stock-items:
    1. write_offs - списания
    2. scrap - брак
    3. write_offs_showcase - списания с витрины
'''
class WriteOffs(BaseGroup):

    def __init__(self):
        self.write_offs = 0
        self.scrap = 0
        self.write_offs_showcase = 0
        self.logger = Logger('WRITE_OFFS')

    async def app(self):
        reason_prepare = ['Expired', 'Marketing', 'ExpiredShowcaseTime']
        reason_scrap = ['Defected', 'DamagedPackaging', 'HumanElement', 'ShowcaseWriteOff']
        reason_showcase = ['ExpiredShowcaseTime', 'ShowcaseWriteOff']
        dict_stock = {}
        conn = Connect(self.data['partner_id'], self.data['name'])
        reach = False
        skip = 0
        take = 500
        start_period = f'{date.today() - timedelta(days=150)}T00:00:00'
        while not reach:
            response = await conn.dodo_api(f'https://api.dodois.{self.data["properties"]}/'
                                           f'accounting/incoming-stock-items', self.data['access'],
                                           units=self.data['uuid'], _from=start_period,
                                           to=self.date_end, skip=skip, take=take)
            skip += take
            try:
                for stock in response['incomingStockItems']:
                    dict_stock[stock['stockItemId']] = stock['pricePerMeasurementUnitWithVat']
            except Exception as e:
                self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
            try:
                if response['isEndOfListReached']:
                    reach = True
            except Exception as e:
                reach = True
                self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
        reach_write = False
        skip_write = 0
        take_write = 500
        while not reach_write:
            response = await conn.dodo_api(f'https://api.dodois.{self.data["properties"]}/'
                                           f'accounting/write-offs/stock-items', self.data['access'],
                                           units=self.data['uuid'], _from=self.date_start, to=self.date_end,
                                           skip=skip_write, take=take_write)
            skip_write += take_write
            try:
                for write_off in response['writeOffs']:
                    try:
                        price = dict_stock[write_off['stockItemId']]
                        value = round(write_off['quantity'] * price, 2)
                        if write_off['reason'] in reason_prepare:
                            self.write_offs += value
                        if write_off['reason'] in reason_scrap:
                            self.scrap += value
                        if write_off['reason'] in reason_showcase:
                            self.write_offs_showcase += value
                    except Exception as e:
                        self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
            except Exception as e:
                self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
            try:
                if response['isEndOfListReached']:
                    reach_write = True
            except Exception as e:
                reach_write = True
                self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
        reach_product = False
        skip_product = 0
        take_product = 500
        while not reach_product:
            response = await conn.dodo_api(f'https://api.dodois.{self.data["properties"]}/'
                                           f'accounting/write-offs/products', self.data['access'],
                                           units=self.data['uuid'], _from=self.date_start, to=self.date_end,
                                           skip=skip_product, take=take_product)
            skip_product += take_product
            try:
                for write_product in response['writeOffs']:
                    try:
                        stock_items = write_product['stockItems']
                        reason = write_product['reason']
                        for items in stock_items:
                            price = dict_stock[items['id']]
                            value = round(items['quantity'] * price, 2)
                            if reason in reason_prepare:
                                self.write_offs += value
                            if reason in reason_scrap:
                                self.scrap += value
                            if reason in reason_showcase:
                                self.write_offs_showcase += value
                    except Exception as e:
                        self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
            except Exception as e:
                self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
            try:
                if response['isEndOfListReached']:
                    reach_product = True
            except Exception as e:
                reach_product = True
                self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
