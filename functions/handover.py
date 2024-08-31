from utils.logging import Logger
from datetime import timedelta
from utils.connection import Connect
from utils.classes import BaseGroup


'''
    Набор метрик с эндпоинта время выдачи заказа /production/orders-handover-time:
    1. late_stationary - опоздание в ресторане
    2. percent_late_stationary - процент опозданий в ресторане от общего числа заказов
    3. cooking_time_stationary - время приготовления в ресторан
    4. cooking_time_delivery - время приготовления на доставку
    5. assembly_time_stationary - время сборки в ресторане
    6. percent_long_orders_stationary - процент долгих заказов в ресторане
    7. percent_long_orders_delivery - процент долгих заказов на доставку
'''
class Handover(BaseGroup):
    def __init__(self):
        self.logger = Logger('HANDOVER')
        self.late_stationary = 0
        self.percent_late_stationary = 0
        self.cooking_time_stationary = timedelta(0)
        self.cooking_time_delivery = timedelta(0)
        self.assembly_time_stationary = timedelta(0)
        self.percent_long_orders_stationary = 0
        self.percent_long_orders_delivery = 0

    async def app(self, orders_stationary):
        conn = Connect(self.data['partner_id'], self.data['name'])
        count_orders_stationary, count_orders_delivery = 0, 0
        amount_meet_stationary, amount_meet_delivery = 0, 0
        amount_assembly_stationary = 0
        response = await conn.dodo_api(f'https://api.dodois.{self.data["properties"]}/production/orders-handover-time',
                                       self.data["access"], units=self.data["uuid"],
                                       _from=self.date_start, to=self.date_end)
        try:
            for order in response['ordersHandoverTime']:
                if order['salesChannel'] == 'Dine-in':
                    count_orders_stationary += 1
                    products_in_order = int(order['orderNumber'].split('-')[-1])
                    time_meet = order['trackingPendingTime'] + order['cookingTime']
                    amount_meet_stationary += time_meet
                    amount_assembly_stationary += order['assemblyTime']
                    if products_in_order == 0:
                        if time_meet > 300:
                            self.late_stationary += 1
                    if 0 < products_in_order < 9:
                        if time_meet > 900:
                            self.late_stationary += 1
                    if products_in_order >= 9:
                        if time_meet > 1500:
                            self.late_stationary += 1
                elif order['salesChannel'] == 'Delivery':
                    count_orders_delivery += 1
                    time_meet = order['trackingPendingTime'] + order['cookingTime']
                    amount_meet_delivery += time_meet
            try:
                self.percent_late_stationary = round(self.late_stationary / orders_stationary * 100, 2)
            except ZeroDivisionError as e:
                self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
            try:
                self.cooking_time_stationary = timedelta(seconds=round(amount_meet_stationary /
                                                                       count_orders_stationary, 0))
            except ZeroDivisionError as e:
                self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
            try:
                self.cooking_time_delivery = timedelta(seconds=round(amount_meet_delivery /
                                                                     count_orders_delivery, 0))
            except ZeroDivisionError as e:
                self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
            try:
                self.assembly_time_stationary = timedelta(seconds=round(amount_assembly_stationary /
                                                                        count_orders_stationary, 0))
            except ZeroDivisionError as e:
                self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
            self.logger.info(f'{self.data["partner_id"]} | {self.data["name"]} | OK')
        except Exception as e:
            self.logger.error(f'{e}|{self.data["partner_id"]}|{self.data["name"]}')
