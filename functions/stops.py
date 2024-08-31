from utils.logging import Logger
from utils.connection import Connect
from datetime import datetime, timedelta
from utils.classes import BaseGroup


'''
    Набор метрик с эндпоинта стопов /production/stop-sales-channels, 
        /production/stop-sales-products, /production/stop-sales-ingredients,
        /delivery/stop-sales-sectors:
    1. duration_stops_channels - продолжительность стопов по каналам продаж
    2. cause_stops_channels - причины стопов по каналам
    3. list_products_stops - список продуктов поставленных в стоп
    4. quantity_products_stops - количество продуктов поставленных в стоп
    5. list_ingredients_stops - список ингредиентов поставленных в стоп
    6. quantity_ingredients_stops - количество ингредиентов поставленных в стоп
    7. duration_stops_sectors - длительность стопов по секторам
    8. quantity_stops_sectors - количество секторов в стопе
'''
class Stops(BaseGroup):
    def __init__(self):
        self.duration_stops_channels = timedelta(0)
        self.cause_stops_channels = ''
        self.list_products_stops = ''
        self.quantity_products_stops = 0
        self.list_ingredients_stops = ''
        self.quantity_ingredients_stops = 0
        self.duration_stops_sectors = timedelta(0)
        self.quantity_stops_sectors = 0
        self.logger = Logger('STOPS')

    async def app(self):
        time_stop = []
        cause_stop = []
        product_names = ''
        product_list = []
        ingredient_names = ''
        ingredient_list = []
        sectors_time_stop = []
        conn = Connect(self.data['partner_id'], self.data['name'])
        response = await conn.dodo_api(f'https://api.dodois.{self.data["properties"]}/production/stop-sales-channels',
                                       self.data['access'], units=self.data['uuid'],
                                       _from=self.date_start, to=self.date_end)
        try:
            for channel in response['stopSalesBySalesChannels']:
                if channel['startedAt'] in time_stop and channel['endedAt'] in time_stop:
                    continue
                else:
                    start_at = datetime.strptime(channel['startedAt'], '%Y-%m-%dT%H:%M:%S')
                    end_at = datetime.strptime(channel['endedAt'], '%Y-%m-%dT%H:%M:%S')
                    reason = channel['reason']
                    time_stop.append(channel['startedAt'])
                    time_stop.append(channel['endedAt'])
                    self.duration_stops_channels += end_at - start_at
                    if reason in cause_stop:
                        continue
                    else:
                        cause_stop.append(reason)
            self.cause_stops_channels = '\n'.join(cause_stop)
        except Exception as e:
            self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
        response_product = await conn.dodo_api(f'https://api.dodois.{self.data["properties"]}/'
                                               f'production/stop-sales-products', self.data["access"],
                                               units=self.data['uuid'], _from=self.date_start, to=self.date_end)
        try:
            for product in response_product['stopSalesByProducts']:
                if product_names != product['productName']:
                    product_names = product['productName']
                    self.quantity_products_stops += 1
                if product['productName'] in product_list:
                    continue
                else:
                    product_list.append(product['productName'])
            self.list_products_stops = '\n'.join(product_list)
        except Exception as e:
            self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
        response_ingredient = await conn.dodo_api(f'https://api.dodois.{self.data["properties"]}/'
                                                  f'production/stop-sales-ingredients', self.data['access'],
                                                  units=self.data['uuid'], _from=self.date_start, to=self.date_end)
        try:
            for ingredient in response_ingredient['stopSalesByIngredients']:
                if ingredient_names != ingredient['ingredientName']:
                    ingredient_names = ingredient['ingredientName']
                    self.quantity_ingredients_stops += 1
                if ingredient['ingredientName'] in ingredient_list:
                    continue
                else:
                    ingredient_list.append(ingredient['ingredientName'])
            self.list_ingredients_stops = '\n'.join(ingredient_list)
        except Exception as e:
            self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
        response_sector = await conn.dodo_api(f'https://api.dodois.{self.data["properties"]}/'
                                              f'delivery/stop-sales-sectors', self.data['access'],
                                              units=self.data['uuid'], _from=self.date_start, to=self.date_end)
        try:
            for sector in response_sector['stopSalesBySectors']:
                start_at_sector = datetime.strptime(sector['startedAt'], '%Y-%m-%dT%H:%M:%S')
                end_at_sector = datetime.strptime(sector['endedAt'], '%Y-%m-%dT%H:%M:%S')
                sectors_time_stop.append(sector['startedAt'])
                sectors_time_stop.append(sector['endedAt'])
                self.duration_stops_sectors += end_at_sector - start_at_sector
                self.quantity_stops_sectors += 1
        except Exception as e:
            self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
        self.logger.info(f'{self.data["partner_id"]} | {self.data["name"]} | OK')
