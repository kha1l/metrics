from utils.logging import Logger
from utils.connection import Connect
from datetime import timedelta, date
from utils.classes import BaseGroup


'''
    Набор метрик с эндпоинтов /accounting/incoming-stock-items и /accounting/stock-consumptions-by-period:
    1. amount_staff_lunches - сумма обедов сотрудников
    2. percent_staff_lunches - процент обедов сотрудников от выручки
'''
class StaffMeal(BaseGroup):
    def __init__(self):
        self.amount_staff_lunches = 0
        self.percent_staff_lunches = 0
        self.logger = Logger('StaffMeal')

    async def app(self, revenue):
        skip = 0
        take = 0
        stock_items_dict = {}
        reach, reach_staff_meal = False, False
        start = f'{date.today() - timedelta(days=150)}T00:00:00'
        conn = Connect(self.data['partner_id'], self.data['name'])
        while not reach:
            response = await conn.dodo_api(f'https://api.dodois.{self.data["properties"]}/'
                                           f'accounting/incoming-stock-items',
                                           self.data["access"], units=self.data["uuid"],
                                           _from=start, to=self.date_end,
                                           skip=skip, take=take)
            skip += take
            try:
                for stock in response['incomingStockItems']:
                    stock_items_dict[stock['stockItemId']] = stock['pricePerMeasurementUnitWithVat']
            except Exception as e:
                self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
            try:
                if response['isEndOfListReached']:
                    reach = True
            except Exception as e:
                reach = True
                self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
        skip = 0
        take = 500
        while not reach_staff_meal:
            response = await conn.dodo_api(f'https://api.dodois.{self.data["properties"]}/'
                                           f'accounting/stock-consumptions-by-period',
                                           self.data["access"], units=self.data["uuid"], _from=self.date_start,
                                           to=self.date_end, skip=skip, take=take)
            skip += take
            try:
                for cons in response['consumptions']:
                    if cons['consumptionType'] == 'StaffMeal':
                        try:
                            price = stock_items_dict[cons['stockItemId']]
                            value = round(cons['quantity'] * price, 2)
                            self.amount_staff_lunches += value
                        except Exception:
                            pass
            except Exception as e:
                self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
            try:
                if response['isEndOfListReached']:
                    reach_staff_meal = True
            except Exception as e:
                reach_staff_meal = True
                self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
            try:
                self.percent_staff_lunches = round(self.amount_staff_lunches / revenue * 100, 2)
            except ZeroDivisionError as e:
                self.percent_staff_lunches = 0
                self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
        self.logger.info(f'{self.data["partner_id"]} | {self.data["name"]} | OK')
