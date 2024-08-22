from utils.logging import Logger
from utils.connection import Connect
from datetime import timedelta, date


'''
    Набор метрик с эндпоинтов /accounting/incoming-stock-items и /accounting/stock-consumptions-by-period:
    1. amount_staff_lunches - сумма обедов сотрудников
    2. percent_staff_lunches - процент обедов сотрудников от выручки
'''
class StaffMeal:
    def __init__(self):
        self.amount_staff_lunches = 0
        self.percent_staff_lunches = 0
        self.logger = Logger('StaffMeal')

    async def app(self, revenue, data, date_start, date_end):
        skip = 0
        take = 0
        stock_items_dict = {}
        reach, reach_staff_meal = False, False
        start = f'{date.today() - timedelta(days=150)}T00:00:00'
        conn = Connect(data['partner_id'], data['name'])
        while not reach:
            response = await conn.dodo_api(f'https://api.dodois.{data["properties"]}/accounting/incoming-stock-items',
                                           data["access"], units=data["uuid"], _from=start, to=date_end,
                                           skip=skip, take=take)
            skip += take
            try:
                for stock in response['incomingStockItems']:
                    stock_items_dict[stock['stockItemId']] = stock['pricePerMeasurementUnitWithVat']
            except Exception as e:
                self.logger.error(f'{e} | {data["partner_id"]} | {data["name"]}')
            try:
                if response['isEndOfListReached']:
                    reach = True
            except Exception as e:
                reach = True
                self.logger.error(f'{e} | {data["partner_id"]} | {data["name"]}')
        skip = 0
        take = 500
        while not reach_staff_meal:
            response = await conn.dodo_api(f'https://api.dodois.{data["properties"]}/'
                                           f'accounting/stock-consumptions-by-period',
                                           data["access"], units=data["uuid"], _from=date_start,
                                           to=date_end, skip=skip, take=take)
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
                self.logger.error(f'{e} | {data["partner_id"]} | {data["name"]}')
            try:
                if response['isEndOfListReached']:
                    reach_staff_meal = True
            except Exception as e:
                reach_staff_meal = True
                self.logger.error(f'{e} | {data["partner_id"]} | {data["name"]}')
            try:
                self.percent_staff_lunches = round(self.amount_staff_lunches / revenue * 100, 2)
            except ZeroDivisionError as e:
                self.percent_staff_lunches = 0
                self.logger.error(f'{e} | {data["partner_id"]} | {data["name"]}')
        self.logger.info(f'{data["partner_id"]} | {data["name"]} | OK')
