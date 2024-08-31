from utils.logging import Logger
from utils.connection import Connect
from datetime import datetime, timedelta
from utils.classes import BaseGroup


'''
    Набор метрик с эндпоинта часы по графику /staff/schedules:
    1. schedule_work_hours - планируемые часы по графику
'''
class Schedule(BaseGroup):
    def __init__(self):
        self.schedule_work_hours = 0
        self.logger = Logger('SCHEDULE')

    async def app(self):
        total_hours = timedelta(0)
        skip = 0
        take = 500
        conn = Connect(self.data['partner_id'], self.data['name'])
        reach = False
        while not reach:
            response = await conn.dodo_api(f'https://api.dodois.{self.data["properties"]}/staff/schedules',
                                           self.data["access"], units=self.data["uuid"],
                                           beginFrom=self.date_start, beginTo=self.date_end, skip=skip, take=take)
            skip += take
            try:
                for schedule in response['schedules']:
                    if schedule['staffTypeName'] != 'Courier' and \
                            schedule['staffTypeName'] != 'Operator':
                        scheduled_start_at = schedule['scheduledShiftStartAtLocal']
                        scheduled_end_at = schedule['scheduledShiftEndAtLocal']
                        scheduled_start_format = datetime.strptime(scheduled_start_at, '%Y-%m-%dT%H:%M:%S')
                        scheduled_end_format = datetime.strptime(scheduled_end_at, '%Y-%m-%dT%H:%M:%S')
                        total_hours += scheduled_end_format - scheduled_start_format
            except Exception as e:
                self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
            try:
                if response['isEndOfListReached']:
                    reach = True
            except Exception as e:
                reach = True
                self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
        self.schedule_work_hours = total_hours.days * 24 + total_hours.seconds / 3600
        self.logger.info(f'{self.data["partner_id"]} | {self.data["name"]} | OK')
