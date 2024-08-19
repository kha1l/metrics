from utils.logging import Logger
from utils.connection import Connect


class Sales:
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

    async def sales_app(self, data, date_start, date_end):
        conn = Connect(data['partner'], data['rest_name'])
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
            response = await conn.dodo_api(f'https://api.dodois.{data["properties"]}/accounting/sales',
                                           data['access'], units=data['units'],
                                           _from=date_start, to=date_end,
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
                self.logger.error(f'{e} | {data["partner"]} | {data["rest_name"]}')
            try:
                if response['isEndOfListReached']:
                    reach = True
            except Exception as e:
                reach = True
                self.logger.error(f'{e} | {data["partner"]} | {data["rest_name"]}')
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
        self.logger.info(f'{data["partner"]} | {data["rest_name"]} | OK')