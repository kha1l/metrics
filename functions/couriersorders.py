from utils.logging import Logger
from utils.connection import Connect


'''
Набор метрик с эндпоинта поездки курьеров /delivery/couriers-orders:
    1. percent_long_orders_delivery - процент долгих заказов на доставку
    2. percent_long_orders_stationary - процент долгих заказов в ресторан
    3. percent_one_delivery - процент поездок с одним заказом
    4. percent_two_delivery - процент поездок с двумя заказами
    5. percent_three_more_delivery - процент поездок с тремя и более заказами
'''
class CouriersOrders:
    def __init__(self):
        self.percent_long_orders_delivery = 0
        self.percent_long_orders_stationary = 0
        self.percent_one_delivery = 0
        self.percent_two_delivery = 0
        self.percent_three_more_delivery = 0
        self.logger = Logger('COURIERSORDERS')

    async def app(self, delivery_orders, stationary_orders, data, date_start, date_end):
        skip = 0
        take = 500
        count_delivery_later = 0
        count_one_delivery = 0
        count_two_delivery = 0
        count_stationary_later = 0
        handover_orders = {}
        conn = Connect(data['partner_id'], data['name'])
        reach = False
        response_handover = await conn.dodo_api(f'https://api.dodois.{data["properties"]}'
                                                f'/production/orders-handover-time', data['access'],
                                                units=data['uuid'], _from=date_start, to=date_end)
        try:
            for times in response_handover['ordersHandoverTime']:
                if times['salesChannel'] == 'Delivery':
                    handover_orders[times['orderId']] = times['trackingPendingTime'] + times['cookingTime'] \
                                                 + times['heatedShelfTime']
                if times['salesChannel'] == 'Dine-in':
                    time_stationary = times['trackingPendingTime'] + times['cookingTime']
                    if time_stationary > 900:
                        count_stationary_later += 1
        except Exception as e:
            self.logger.error(f'{e} | {data["partner_id"]} | {data["name"]}')
        while not reach:
            response_orders = await conn.dodo_api(f'https://api.dodois.{data["properties"]}'
                                                  f'/delivery/couriers-orders', data['access'],
                                                  units=data['uuid'], _from=date_start, to=date_end,
                                                  skip=skip, take=take)

            skip += take
            try:
                for order in response_orders['couriersOrders']:
                    if order['tripOrdersCount'] == 1:
                        count_one_delivery += 1
                    elif order['tripOrdersCount'] == 2:
                        count_two_delivery += 1
                    try:
                        values = order['deliveryTime'] + handover_orders.get(order['orderId'])
                    except Exception:
                        values = 0
                    if values > 2400:
                        count_delivery_later += 1
            except Exception as e:
                reach = True
                self.logger.error(f'{e} | {data["partner_id"]} | {data["name"]}')
            try:
                if response_orders['isEndOfListReached']:
                    reach = True
            except Exception as e:
                self.logger.error(f'{e} | {data["partner_id"]} | {data["name"]}')
                reach = True
        try:
            self.percent_long_orders_delivery = round(count_delivery_later / delivery_orders * 100, 2)
        except ZeroDivisionError:
            self.percent_long_orders_delivery = 0

        try:
            self.percent_long_orders_stationary = round(count_stationary_later / stationary_orders * 100, 2)
        except ZeroDivisionError:
            self.percent_long_orders_stationary = 0
        try:
            self.percent_one_delivery = round(count_one_delivery / delivery_orders * 100, 2)
        except ZeroDivisionError:
            self.percent_one_delivery = 0
        try:
            self.percent_two_delivery = round(count_two_delivery / 2 / delivery_orders * 100, 2)
        except ZeroDivisionError:
            self.percent_two_delivery = 0
        try:
            self.percent_three_more_delivery = 1 - self.percent_two_delivery - self.percent_one_delivery
        except ZeroDivisionError:
            self.percent_three_more_delivery = 0
        self.logger.info(f'{data["partner_id"]} | {data["name"]} | OK')
