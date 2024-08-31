from utils.logging import Logger
from utils.connection import Connect
from datetime import datetime, timedelta
from utils.classes import BaseGroup

'''
    Набор метрик с эндпоинта производительность /production/productivity:
    1. productivity_kitchen - производительность кухни
    2. productivity_product - продуктов в час
    3. productivity_couriers - производительность курьеров
    4. quantity_work_hours - количество отработанных часов кухня
'''
class Productivity(BaseGroup):
    def __init__(self):
        self.productivity_kitchen = 0
        self.productivity_product = 0
        self.quantity_work_hours = 0
        self.productivity_couriers = 0
        self.logger = Logger('PRODUCTIVITY')

    async def app(self):
        conn = Connect(self.data['partner_id'], self.data['name'])
        datetime_date_end = datetime.strptime(self.date_end, '%Y-%m-%dT00:00:00')
        date_end = datetime.strftime(datetime_date_end + timedelta(days=1), '%Y-%m-%dT00:00:00')
        response = await conn.dodo_api(f'https://api.dodois.{self.data["properties"]}/production/productivity',
                                       self.data["access"], units=self.data["uuid"],
                                       _from=self.date_start, to=self.date_end)
        try:
            productivity = response['productivityStatistics'][0]
            self.productivity_kitchen = productivity['salesPerLaborHour']
            self.productivity_product = productivity['productsPerLaborHour']
            self.productivity_couriers = productivity['ordersPerCourierLabourHour']
            self.quantity_work_hours = productivity['laborHours']
            self.logger.info(f'{self.data["partner_id"]} | {self.data["name"]} | OK')
        except Exception as e:
            self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
