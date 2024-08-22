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
        self.quantity_grade_delivery = 0

    async def app(self, data, date_start, date_end):
        conn = Connect(data['partner_id'], data['name'])
        properties = data["properties"].split('/')
        date_start_format = date_start.split('T')[0]
        date_end_format = date_end.split('T')[0]
        start_date_format = date_start_format.split('-')
        end_date_format = date_end_format.split('-')
        start_date = f'{start_date_format[2]}.{start_date_format[1]}.{start_date_format[0]}'
        end_date = f'{end_date_format[2]}.{end_date_format[1]}.{end_date_format[0]}'
        response = await conn.dodo_api(f'https://api.dodois.{properties[0]}/customer-feedback/customer-ratings',
                                       data["access"], units=data["uuid"],
                                       _from=start_date, to=end_date)
        try:
            rating = response['customerRatings'][0]
            self.customer_rating_stationary = rating['avgDineInOrderRate']
            self.customer_rating_delivery = rating['avgDeliveryOrderRate']
            self.quantity_grade_stationary = rating['dineInRateCount']
            self.quantity_grade_delivery = rating['deliveryRateCount']
        except Exception as e:
            self.logger.error(f'{e} | {data["partner_id"]} | {data["name"]}')
