from utils.logging import Logger
from utils.connection import Connect
from datetime import datetime


'''
    Набор метрик с эндпоинта список сотрудников /staff/members:
    1. quantity_couriers - количество курьеров
    2. quantity_kitchen - количество персонала кухни
    3. employed_couriers - количество принятых курьеров
    4. employed_kitchen - количество принятых на кухню
    5. dismissed_couriers - уволенные курьеры
    6. dismissed_kitchen - уволенные кухня
'''
class Staff:
    def __init__(self):
        self.quantity_couriers = 0
        self.quantity_kitchen = 0
        self.employed_couriers = 0
        self.employed_kitchen = 0
        self.dismissed_couriers = 0
        self.dismissed_kitchen = 0
        self.logger = Logger('STAFF')

    async def app(self, data, date_start, date_end):
        conn = Connect(data['partner_id'], data['name'])
        datetime_start = datetime.strptime(date_start, "%Y-%m-%dT%H:%M:%S")
        datetime_end = datetime.strptime(date_end, "%Y-%m-%dT%H:%M:%S")
        response = await conn.dodo_api(f'https://api.dodois.{data["properties"]}/staff/members',
                                       data['access'], units=data['uuid'], statuses='Active', take=900)
        try:
            for person in response['members']:
                if person['staffType'] == 'Courier':
                    self.quantity_couriers += 1
                else:
                    self.quantity_kitchen += 1
        except Exception as e:
            self.logger.error(f'{e} | {data["partner_id"]} | {data["name"]}')
        response_hired = await conn.dodo_api(f'https://api.dodois.{data["properties"]}/staff/members',
                                             data['access'], units=data['uuid'], hiredOn=date_start,
                                             hiredTo=date_end, take=900)
        try:
            for person_hired in response_hired['members']:
                if person_hired['positionName'] != 'Управляющий':
                    hired_date = datetime.strptime(person_hired["hiredOn"], "%Y-%m-%d")
                    if datetime_start < hired_date < datetime_end:
                        if person_hired['staffType'] == 'Courier':
                            self.employed_couriers += 1
                        else:
                            self.employed_kitchen += 1
        except Exception as e:
            self.logger.error(f'{e} | {data["partner_id"]} | {data["name"]}')
        response_dismissed = await conn.dodo_api(f'https://api.dodois.{data["properties"]}/staff/members',
                                                 data['access'], units=data['uuid'], dismissedFrom=date_start,
                                                 dismissedTo=date_end, statuses='Dismissed', take=900)
        try:
            for person_diss in response_dismissed['members']:
                if person_diss['positionName'] != 'Управляющий':
                    if person_diss['staffType'] == 'Courier':
                        self.dismissed_couriers += 1
                    else:
                        self.dismissed_kitchen += 1
        except Exception as e:
            self.logger.error(f'{e} | {data["partner_id"]} | {data["name"]}')
        self.logger.info(f'{data["partner_id"]} | {data["name"]} | OK')
