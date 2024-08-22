from utils.logging import Logger
from utils.connection import Connect
from datetime import datetime, timedelta

'''
    Набор метрик с глобал эндпоинта unitinfo/dailyrevenue/:
    1. revenue - общая выручка
    2. orders - общее количество заказов
    3. revenue_stationary - выручка ресторана
    4. revenue_delivery - выручка на доставку
    5. orders_stationary - количество заказов в ресторане
    6. orders_delivery - количество заказов на доставку
    7. orders_pickup - количество заказов самовывоз
    8. revenue_pickup - выручка самовывоз
    9. revenue_mobile_app - выручка из мобильного приложения
    10. orders_mobile_app - количество заказов из мобильного приложения
    11. percent_mobile_app - процент заказов из мобильного приложения
'''
class Revenue:
    def __init__(self):
        self.revenue = 0
        self.orders = 0
        self.revenue_stationary = 0
        self.revenue_delivery = 0
        self.orders_stationary = 0
        self.orders_delivery = 0
        self.orders_pickup = 0
        self.revenue_pickup = 0
        self.revenue_mobile_app = 0
        self.orders_mobile_app = 0
        self.percent_mobile_app = 0
        self.logger = Logger('REVENUE')

    async def app(self, data, date_start, date_end):
        conn = Connect(data['partner_id'], data['name'])
        properties = data["properties"].split('/')
        concept = properties[1]
        if concept == 'dodopizza':
            concept = ''
        else:
            concept += '.'
        date_start = datetime.strptime(date_start, '%Y-%m-%dT%H:%M:%S').date()
        date_end = datetime.strptime(date_end, '%Y-%m-%dT%H:%M:%S').date()
        while date_start != date_end + timedelta(days=1):
            link = f'https://publicapi.{concept}dodois.io/{properties[-1]}/api/v1/unitinfo/' \
                   f'{data["short_id"]}/dailyrevenue/{date_start.year}/{date_start.month}/{date_start.day}'
            response = await conn.public_dodo_api(link)
            try:
                rev = response['UnitRevenue'][0]
                self.revenue += int(rev['Value'])
                self.orders += int(rev['Count'])
                self.revenue_stationary += int(rev['StationaryRevenue'])
                self.revenue_delivery += int(rev['DeliveryRevenue'])
                self.revenue_pickup += int(rev['PickupRevenue'])
                self.orders_stationary += int(rev['StationaryCount'])
                self.orders_delivery += int(rev['DeliveryCount'])
                self.orders_pickup += int(rev['PickupCount'])
                self.revenue_mobile_app += int(rev['StationaryMobileRevenue'])
                self.orders_mobile_app += int(rev['StationaryMobileCount'])
            except Exception as e:
                self.logger.error(f'{e} | {data["partner_id"]} | {data["name"]}')
            date_start += timedelta(days=1)
        try:
            self.percent_mobile_app += round(self.orders_mobile_app / self.orders_stationary * 100, 2)
        except ZeroDivisionError as e:
            self.percent_mobile_app += 0
            self.logger.error(f'{e} | {data["partner_id"]} | {data["name"]}')
        self.logger.info(f'{data["partner_id"]} | {data["name"]} | OK')
