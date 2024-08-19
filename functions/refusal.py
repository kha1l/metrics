from utils.logging import Logger
from utils.connection import Connect


class Refusal:
    def __init__(self):
        self.logger = Logger('REFUSAL')
        self.amount_refusal = 0
        self.percent_refusal = 0

    async def refusal_app(self, revenue, data, date_start, date_end):
        skip = 0
        take = 0
        reach = False
        conn = Connect(data['partner'], data['rest_name'])
        while not reach:
            response = await conn.dodo_api(f'https://api.dodois.{data["properties"]}/accounting/cancelled-sales',
                                           data["access"], units=data["units"], _from=date_start, to=date_end,
                                           skip=skip, take=take)
            skip += take
            try:
                for refusal in response['cancelledSales']:
                    self.amount_refusal += refusal['price']
            except Exception as e:
                self.logger.error(f'{e} | {data["partner"]} | {data["rest_name"]}')
            try:
                if response['isEndOfListReached']:
                    reach = True
            except Exception as e:
                reach = True
                self.logger.error(f'{e} | {data["partner"]} | {data["rest_name"]}')
        self.amount_refusal = round(self.amount_refusal, 0)
        try:
            self.percent_refusal = round(self.amount_refusal / revenue * 100, 2)
        except ZeroDivisionError:
            self.percent_refusal = 0
        self.logger.info(f'{data["partner"]} | {data["rest_name"]} | OK')
