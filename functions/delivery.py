from datetime import timedelta
from utils.connection import Connect
from utils.logging import Logger

'''
    Набор метрик с эндпоинта статистика по доставке /delivery/statistics/:
    1. average_delivery_speed - средняя скорость доставки
    2. couriers_workload - загруженность курьеров
    3. certificates - количество выданных сертификатов на доставку
    4. time_in_shelf - время заказов на тепловой полке
    5. percent_late_delivery - процент опозданий на доставку
'''
class Delivery:
    def __init__(self):
        self.average_delivery_speed = timedelta(0)
        self.couriers_workload = 0
        self.certificates = 0
        self.time_in_shelf = timedelta(0)
        self.percent_late_delivery = 0
        self.logger = Logger('DELIVERY')

    async def delivery_app(self, orders, data, dt_start, dt_end):
        conn = Connect(data['partner'], data['rest_name'])
        response = await conn.dodo_api(f'https://api.dodois.{data["domain"]}/dodopizza/'
                                       f'{data["country_code"]}/delivery/statistics/',
                                       data['access'], units=data['units'], _from=dt_start, to=dt_end)
        try:
            delivery = response['unitsStatistics'][0]
            self.average_delivery_speed = timedelta(seconds=delivery['avgDeliveryOrderFulfillmentTime'])
            self.time_in_shelf = timedelta(seconds=delivery['avgHeatedShelfTime'])
            self.certificates = delivery['lateOrdersCount']
            try:
                self.couriers_workload = round((delivery['tripsDuration'] / delivery['couriersShiftsDuration']), 2)
                self.percent_late_delivery = round(delivery['lateOrdersCount'] / orders * 100, 2)
            except ZeroDivisionError as e:
                self.logger.error(f'{e} | {data["partner"]} | {data["rest_name"]}')
            self.logger.info(f'{data["partner"]} | {data["rest_name"]} | OK')
        except Exception as e:
            self.logger.error(f'{e} | {data["partner"]} | {data["rest_name"]}')
