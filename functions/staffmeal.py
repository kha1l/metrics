from utils.logging import Logger
from utils.connection import Connect
from datetime import timedelta, date

class StaffMeal:
    def __init__(self):
        self.logger = Logger('StaffMeal')
        self.amount_staff_lunches = 0
        self.percent_staff_lunches = 0

    async def staff_meal_app(self, revenue, data, date_start, date_end):
        skip = 0
        take = 0
        stock_items_dict = {}
        reach, reach_staff_meal = False, False
        start = f'{date.today() - timedelta(days=150)}T00:00:00'
        conn = Connect(data['partner'], data['rest_name'])
        while not reach:
            response = await conn.dodo_api(f'https://api.dodois.{data["properties"]}/accounting/incoming-stock-items',
                                           data["access"], units=data["units"], _from=start, to=date_end,
                                           skip=skip, take=take)
            skip += take
            try:
                for stock in response['incomingStockItems']:
                    stock_items_dict[stock['stockItemId']] = stock['pricePerMeasurementUnitWithVat']
            except Exception as e:
                self.logger.error(f'{e} | {data["partner"]} | {data["rest_name"]}')
            try:
                if response['isEndOfListReached']:
                    reach = True
            except Exception as e:
                reach = True
                self.logger.error(f'{e} | {data["partner"]} | {data["rest_name"]}')
        skip = 0
        take = 500
        while not reach_staff_meal:
            response = await conn.dodo_api(f'https://api.dodois.{data["properties"]}/'
                                           f'accounting/stock-consumptions-by-period',
                                           data["access"], units=data["units"], _from=date_start,
                                           to=date_end, skip=skip, take=take)
            skip += take
            try:
                for cons in response['consumptions']:
                    if cons['consumptionType'] == 'StaffMeal':
                        try:
                            price = stock_items_dict[cons['stockItemId']]
                            value = round(cons['quantity'] * price, 2)
                            self.amount_staff_lunches += value
                        except Exception as e:
                            self.logger.error(f'{e} | {data["partner"]} | {data["rest_name"]}')
            except Exception as e:
                self.logger.error(f'{e} | {data["partner"]} | {data["rest_name"]}')
            try:
                if response['isEndOfListReached']:
                    reach_staff_meal = True
            except Exception as e:
                reach_staff_meal = True
                self.logger.error(f'{e} | {data["partner"]} | {data["rest_name"]}')
            try:
                self.percent_staff_lunches = round(self.amount_staff_lunches / revenue * 100, 2)
            except ZeroDivisionError as e:
                self.percent_staff_lunches = 0
                self.logger.error(f'{e} | {data["partner"]} | {data["rest_name"]}')
        self.logger.info(f'{data["partner"]} | {data["rest_name"]} | OK')
