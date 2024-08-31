from utils.logging import Logger
from utils.connection import Connect
from utils.classes import BaseGroup

'''
Набор метрик с эндпоинта отзовы клиентов /customer-feedback/customer-ratings:
    1. customer_rating_stationary - средний рейтинг клиентов в ресторане
    2. customer_rating_delivery - средний рейтинг клиентов на доставку
    3. quantity_grade_stationary - количество оценок в ресторане
    4. quantity_grade_stationary - количество оценок на доставку
'''
class Rating(BaseGroup):
    def __init__(self):
        self.logger = Logger('RATING')
        self.customer_rating_stationary = 0
        self.customer_rating_delivery = 0
        self.quantity_grade_stationary = 0
        self.quantity_grade_delivery = 0

    async def app(self):
        conn = Connect(self.data['partner_id'], self.data['name'])
        properties = self.data["properties"].split('/')
        date_start_format = self.date_start.split('T')[0]
        date_end_format = self.date_end.split('T')[0]
        start_date_format = date_start_format.split('-')
        end_date_format = date_end_format.split('-')
        start_date = f'{start_date_format[2]}.{start_date_format[1]}.{start_date_format[0]}'
        end_date = f'{end_date_format[2]}.{end_date_format[1]}.{end_date_format[0]}'
        response = await conn.dodo_api(f'https://api.dodois.{properties[0]}/customer-feedback/customer-ratings',
                                       self.data["access"], units=self.data["uuid"],
                                       _from=start_date, to=end_date)
        try:
            rating = response['customerRatings'][0]
            self.customer_rating_stationary = rating['avgDineInOrderRate']
            self.customer_rating_delivery = rating['avgDeliveryOrderRate']
            self.quantity_grade_stationary = rating['dineInRateCount']
            self.quantity_grade_delivery = rating['deliveryRateCount']
        except Exception as e:
            self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
