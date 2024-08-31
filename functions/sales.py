from utils.logging import Logger
from utils.connection import Connect
from utils.classes import BaseGroup


'''
    Набор метрик с эндпоинта продажи /accounting/sales:
    1. general_discount - общий дисконт
    2. application_certificate_kitchen - применение сертификатов за опоздание кухни
    3. discount_personal - дисконт по скидке 50%
    4. discount_staff - дисконт по сотрудникам общий
    5. discount_couriers - дисконт по скидке 49%
    6. discount_lunch - дисконт по скидке 60%
    7. discount_combo - дисконт комбо наборов
    8. discount_certificates - дисконт по сертификатам за опоздания на доставку
    9. discount_cvm - дисконт CVM
    10. discount_pickup - дисконт самовывоз
    11. discount_stationary - дисконт продаж в ресторане
    12. discount_delivery - дисконт продаж на доставку
    13. application_certificate_courier - количество применений сертов на опоздания на доставку
    14. percent_sales_ingredient - процент проданых доп ингредиентов
    15. amount_sales_ingredients - сумма проданных ингредиентов
    16. amount_certificate_kitchen - упущенная выручка из за опозданий кухни
    17. kiosk_orders - количество заказов через киоск
    18. percent_kiosk_orders - процент заказов через киоск от общего числа заказов в рест
    19. amount_kiosk_sales - общая сумма заказов через киоск
'''
class Sales(BaseGroup):
    def __init__(self):
        self.general_discount = 0
        self.application_certificate_kitchen = 0
        self.discount_personal = 0
        self.discount_staff = 0
        self.discount_couriers = 0
        self.discount_lunch = 0
        self.discount_combo = 0
        self.discount_certificates = 0
        self.discount_pickup = 0
        self.discount_cvm = 0
        self.discount_stationary = 0
        self.discount_delivery = 0
        self.application_certificate_courier = 0
        self.percent_sales_ingredient = 0
        self.amount_sales_ingredients = 0
        self.amount_certificate_kitchen = 0
        self.kiosk_orders = 0
        self.percent_kiosk_orders = 0
        self.amount_kiosk_sales = 0
        self.logger = Logger('SALES')

    @staticmethod
    def app_percent(disc: float, price: float):
        try:
            percent = round(100 - (disc / price * 100), 2)
            return percent
        except ZeroDivisionError:
            return 0

    @staticmethod
    def append_discount(product, disc, price):
        disc += product['priceWithDiscount']
        price += product['price']
        return disc, price

    async def app(self, ):
        conn = Connect(self.data['partner_id'], self.data['name'])
        skip = 0
        take = 500
        count_orders_kiosk = 0
        count_orders_stationary = 0
        discount = 0
        price = 0
        discount_delivery = 0
        price_delivery = 0
        discount_stationary = 0
        price_stationary = 0
        discount_pickup = 0
        price_pickup = 0
        discount_certificates = 0
        price_certificates = 0
        discount_staff = 0
        price_staff = 0
        discount_cvm = 0
        price_cvm = 0
        without_discount_cvm = 0
        without_discount_certificates = 0
        without_discount_staff = 0
        discount_combo = 0
        price_combo = 0
        without_discount_combo = 0
        mobile_price = 0
        reach = False
        while not reach:
            response = await conn.dodo_api(f'https://api.dodois.{self.data["properties"]}/accounting/sales',
                                           self.data['access'], units=self.data['uuid'],
                                           _from=self.date_start, to=self.date_end,
                                           skip=skip, take=take)
            skip += take
            try:
                for sales in response['sales']:
                    products = sales['products']
                    channel = sales['salesChannel']
                    order = sales['orderSource']
                    if order == 'Kiosk':
                        # Количество заказов через киоск
                        count_orders_kiosk += 1
                    if channel != 'Delivery':
                        # Количество заказов в ресторане
                        count_orders_stationary += 1
                    for product in products:
                        discount_orders = product['discount']
                        combo = product['combo']
                        if order == 'Dine-in':
                            mobile_price += product['priceWithDiscount']
                            ingredients = product['addedIngredients']
                            if ingredients:
                                for ingredient in ingredients:
                                    self.amount_sales_ingredients += ingredient['price']
                        if order == 'Kiosk':
                            self.amount_kiosk_sales += product['priceWithDiscount']
                        discount, price = self.append_discount(product, discount, price)
                        if channel == 'Delivery':
                            discount_delivery, price_delivery = self.append_discount(product,
                                                                                     discount_delivery,
                                                                                     price_delivery)
                        elif channel == 'Dine-in':
                            discount_stationary, price_stationary = self.append_discount(product,
                                                                                         discount_stationary,
                                                                                         price_stationary)
                        elif channel == 'Takeaway':
                            discount_pickup, price_pickup = self.append_discount(product,
                                                                                 discount_pickup,
                                                                                 price_pickup)
                        if discount_orders is not None:
                            if discount['bonusActionName'] == 'Сертификат за опоздание курьера':
                                discount_certificates, price_certificates = self.append_discount(product,
                                                                                                 discount_certificates,
                                                                                                 price_certificates)
                                self.application_certificate_courier += 1
                            elif discount['bonusActionName'] == 'Скидка контрагентам 60%':
                                self.discount_lunch += product['priceWithDiscount']
                                discount_staff, price_staff = self.append_discount(product,
                                                                                   discount,
                                                                                   price_staff)
                            elif discount['bonusActionName'] == 'Скидка контрагентам 49%':
                                self.discount_couriers += product['priceWithDiscount']
                                discount_staff, price_staff = self.append_discount(product,
                                                                                   discount_staff,
                                                                                   price_staff)
                            elif discount['bonusActionName'] == 'Скидка сотрудникам 50%':
                                self.discount_personal += product['priceWithDiscount']
                                discount_staff, price_staff = self.append_discount(product,
                                                                                   discount_staff,
                                                                                   price_staff)
                            elif str(discount['bonusActionName']).startswith('CVM.'):
                                discount_cvm, price_cvm = self.append_discount(product,
                                                                               discount_cvm,
                                                                               price_cvm)
                            elif str(discount['bonusActionName']).startswith('Скидка 20% долгое ожидание в ресторане'):
                                self.application_certificate_kitchen += 1
                                self.amount_certificate_kitchen += product['price'] - product['priceWithDiscount']
                        else:
                            without_discount_cvm += product['price']
                            without_discount_certificates += product['price']
                            without_discount_staff += product['price']
                        if combo is not None:
                            discount_combo, price_combo = self.append_discount(product,
                                                                               discount_combo,
                                                                               price_combo)
                        else:
                            without_discount_combo += product['price']
            except Exception as e:
                self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
            try:
                if response['isEndOfListReached']:
                    reach = True
            except Exception as e:
                reach = True
                self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
        self.discount_cvm = self.app_percent(discount_cvm + without_discount_cvm,
                                             price_cvm + without_discount_cvm)
        self.discount_combo = self.app_percent(discount_combo + without_discount_combo,
                                               price_combo + without_discount_combo)
        self.general_discount = self.app_percent(discount, price)
        self.discount_delivery = self.app_percent(discount_delivery, price_delivery)
        self.discount_stationary = self.app_percent(discount_stationary, price_stationary)
        self.discount_pickup = self.app_percent(discount_pickup, price_pickup)
        self.discount_certificates = self.app_percent(discount_certificates + without_discount_certificates,
                                                      price_certificates + without_discount_certificates)
        self.discount_staff = self.app_percent(discount_staff + without_discount_staff,
                                               price_staff + without_discount_staff)
        try:
            self.kiosk_orders = round(count_orders_kiosk / count_orders_stationary * 100, 2)
        except ZeroDivisionError:
            self.kiosk_orders = 0

        try:
            self.percent_sales_ingredient = round(self.amount_sales_ingredients / mobile_price * 100, 2)
        except ZeroDivisionError:
            self.percent_sales_ingredient = 0
        self.logger.info(f'{self.data["partner_id"]} | {self.data["name"]} | OK')
