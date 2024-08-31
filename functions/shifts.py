from utils.logging import Logger
from utils.connection import Connect
import operator
from utils.classes import BaseGroup


'''
    Набор метрик с эндпоинта смены сотрудников /staff/shifts:
    1. extra_time_work - количество экстра часов кухни
    2. workload_manager - загруженность менеджера
    3. maximum_workload_manager - максимальная загруженность менеджера
    4. workload_kitchen - загруженность кухни
    5. productivity_auto_couriers - производительность авто курьера
    6. productivity_bike_couriers - производительность вело(пешего) курьера
'''
class Shifts(BaseGroup):
    def __init__(self):
        self.extra_time_work = 0
        self.workload_manager = 0
        self.maximum_workload_manager = ''
        self.workload_kitchen = 0
        self.productivity_auto_couriers = 0
        self.productivity_bike_couriers = 0
        self.logger = Logger('SHIFTS')

    async def app(self, hours):
        conn = Connect(self.data['partner_id'], self.data['name'])
        kitchen = ['Стажер-менеджер', 'Инструктор', 'Универсал',
                   'Пиццамейкер', 'Кандидат-пиццамейкер', 'Кассир',
                   'Кандидат-кассир']
        skip = 0
        take = 500
        managers_worked_list = set()
        managers_worked_hours = 0
        manager_worked_dict = {}
        kitchen_list = set()
        kitchen_hours = 0
        couriers_auto_hours = 0
        couriers_auto_orders = 0
        couriers_bike_hours = 0
        couriers_bike_orders = 0
        worked_hours = 0
        reach = False
        while not reach:
            response = await conn.dodo_api(f'https://api.dodois.{self.data["properties"]}/staff/shifts',
                                           self.data['access'], units=self.data['uuid'], clockInFrom=self.date_start,
                                           clockInTo=self.date_end, skip=skip, take=take)
            skip += take
            try:
                if response['isEndOfListReached']:
                    reach = True
            except Exception as e:
                reach = True
                self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
            try:
                for shift in response['shifts']:
                    staff_type = shift['staffTypeName']
                    position = shift['staffPositionName']
                    staff_id = shift['staffId']
                    work_time = shift['dayShiftMinutes'] + shift['nightShiftMinutes']
                    if staff_type != 'Courier':
                        worked_hours += work_time / 60
                        if position == 'Менеджер' or position == 'Заместитель управляющего':
                            managers_worked_list.add(staff_id)
                            managers_worked_hours += work_time / 60
                            if staff_id in manager_worked_dict:
                                manager_worked_dict[staff_id] += work_time / 60
                            else:
                                manager_worked_dict[staff_id] = work_time / 60
                        else:
                            if position in kitchen:
                                kitchen_hours += work_time / 60
                                kitchen_list.add(staff_id)
                    else:
                        if position == 'Автомобильный':
                            couriers_auto_hours += work_time / 60
                            couriers_auto_orders += shift['deliveredOrdersCount']
                        else:
                            couriers_bike_hours += work_time
                            couriers_bike_orders += shift['deliveredOrdersCount']
                person = max(manager_worked_dict.items(), key=operator.itemgetter(1))
                last_name = await conn.dodo_api(f'https://api.dodois.{self.data["properties"]}/staff/'
                                                f'members/{person[0]}', self.data["access"])
                str_person = str(round(person[1], 2)).replace('.', ',')
                self.maximum_workload_manager = f'{str_person}-{last_name["lastName"]}'
                delta_hours = worked_hours - hours
                if delta_hours <= 0:
                    self.extra_time_work = 0
                else:
                    self.extra_time_work = delta_hours
                try:
                    self.workload_kitchen = round(kitchen_hours / len(kitchen_list), 2)
                except ZeroDivisionError as e:
                    self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
                try:
                    self.workload_manager = round(managers_worked_hours / len(managers_worked_list), 2)
                except ZeroDivisionError as e:
                    self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
                try:
                    self.productivity_auto_couriers = round(couriers_auto_orders / couriers_auto_hours, 2)
                except ZeroDivisionError as e:
                    self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
                try:
                    self.productivity_bike_couriers = round(couriers_bike_orders / couriers_bike_hours, 2)
                except ZeroDivisionError as e:
                    self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
            except Exception as e:
                self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
        self.logger.info(f'{self.data["partner_id"]} | {self.data["name"]} | OK')
