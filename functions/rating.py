from utils.logging import Logger
from utils.connection import Connect
from datetime import datetime, timedelta

'''
Набор метрик с эндпоинта отзовы клиентов /customer-feedback/customer-ratings:
    1. customer_rating_stationary - средний рейтинг клиентов в ресторане
    2. customer_rating_delivery - средний рейтинг клиентов на доставку
    3. quantity_grade_stationary - количество оценок в ресторане
    4. quantity_grade_stationary - количество оценок на доставку
'''
class Rating:
    def __init__(self):
        self.logger = Logger('RATING')
        self.customer_rating_stationary = 0
        self.customer_rating_delivery = 0
        self.quantity_grade_stationary = 0
        self.quantity_grade_stationary = 0

    async def rating_app(self, data, date_start, date_end):
        conn = Connect(data['partner'], data['rest_name'])
        properties = data["properties"]
        date_start_format = datetime.strftime(date_start, '%Y-%m-%d')
        date_end_format = datetime.strftime(date_end, '%Y-%m-%d')
        response = await conn.dodo_api(f'https://api.dodois.{properties}/customer-feedback/customer-ratings',
                                       data["access"], units=data["units"],
                                       _from=date_start_format, to=date_end_format)
        try:
            rating = response['customerRatings'][0]
            self.customer_rating_stationary = rating['avgDineInOrderRate']
            self.customer_rating_delivery = rating['avgDeliveryOrderRate']
            self.quantity_grade_stationary = rating['dineInRateCount']
            self.quantity_grade_delivery = rating['deliveryRateCount']
        except Exception as e:
            self.logger.error(f'{e} | {data["partner"]} | {data["rest_name"]}')
