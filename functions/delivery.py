from datetime import timedelta
from utils.connection import Connect
from utils.logging import Logger
from utils.classes import BaseGroup

'''
    Набор метрик с эндпоинта статистика по доставке /delivery/statistics/:
    1. average_delivery_speed - средняя скорость доставки
    2. couriers_workload - загруженность курьеров
    3. certificates - количество выданных сертификатов на доставку
    4. time_in_shelf - время заказов на тепловой полке
    5. percent_late_delivery - процент опозданий на доставку
'''
class Delivery(BaseGroup):
    def __init__(self):
        self.average_delivery_speed = timedelta(0)
        self.couriers_workload = 0
        self.certificates = 0
        self.time_in_shelf = timedelta(0)
        self.percent_late_delivery = 0
        self.logger = Logger('DELIVERY')

    async def app(self, orders_delivery):
        conn = Connect(self.data['partner_id'], self.data['name'])
        response = await conn.dodo_api(f'https://api.dodois.{self.data["properties"]}/delivery/statistics/',
                                       self.data['access'], units=self.data['uuid'],
                                       _from=self.date_start, to=self.date_end)
        try:
            delivery = response['unitsStatistics'][0]
            self.average_delivery_speed = timedelta(seconds=delivery['avgDeliveryOrderFulfillmentTime'])
            self.time_in_shelf = timedelta(seconds=delivery['avgHeatedShelfTime'])
            self.certificates = delivery['lateOrdersCount']
            try:
                self.couriers_workload = round((delivery['tripsDuration'] / delivery['couriersShiftsDuration']), 2)
                self.percent_late_delivery = round(delivery['lateOrdersCount'] / orders_delivery * 100, 2)
            except ZeroDivisionError as e:
                self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
            self.logger.info(f'{self.data["partner_id"]} | {self.data["name"]} | OK')
        except Exception as e:
            self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
