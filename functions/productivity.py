from utils.logging import Logger
from utils.connection import Connect
from datetime import datetime, timedelta

'''
    Набор метрик с эндпоинта производительность /production/productivity:
    1. productivity_kitchen - производительность кухни
    2. productivity_product - продуктов в час
    3. productivity_couriers - производительность курьеровntktuhfv
    4. quantity_work_hours - количество отработанных часов кухня
'''
class Productivity:
    def __init__(self):
        self.logger = Logger('PRODUCTIVITY')
        self.productivity_kitchen = 0
        self.productivity_product = 0
        self.quantity_work_hours = 0
        self.productivity_couriers = 0

    async def productivity_app(self, data, date_start, date_end):
        conn = Connect(data['partner'], data['rest_name'])
        date_end = datetime.strftime(date_end + timedelta(days=1), '%Y-%m-%dT00:00:00')
        response = await conn.dodo_api(f'https://api.dodois.{data["properties"]}/production/productivity',
                                       data["access"], units=data["units"], _from=date_start, to=date_end)
        try:
            productivity = response['productivityStatistics'][0]
            self.productivity_kitchen = productivity['salesPerLaborHour']
            self.productivity_product = productivity['productsPerLaborHour']
            self.productivity_couriers = productivity['ordersPerCourierLabourHour']
            self.quantity_work_hours = productivity['laborHours']
            self.logger.info(f'{data["partner"]} | {data["rest_name"]} | OK')
        except Exception as e:
            self.logger.error(f'{e} | {data["partner"]} | {data["rest_name"]}')
