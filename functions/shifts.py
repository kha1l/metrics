from utils.logging import Logger
from utils.connection import Connect
import operator


class Shifts:
    def __init__(self):
        self.extra_time_work = 0
        self.workload_manager = 0
        self.maximum_workload_manager = ''
        self.workload_kitchen = 0
        self.productivity_auto_couriers = 0
        self.productivity_bike_couriers = 0
        self.logger = Logger('SHIFTS')

    async def shifts_app(self, hours, data, date_start, date_end):
        conn = Connect(data['partner'], data['rest_name'])
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
            response = await conn.dodo_api(f'https://api.dodois.{data["properties"]}/staff/shifts',
                                           data['access'], units=data['units'], clockInFrom=date_start,
                                           clockInTo=date_end, skip=skip, take=take)
            skip += take
            try:
                if response['isEndOfListReached']:
                    reach = True
            except Exception as e:
                reach = True
                self.logger.error(f'{e} | {data["partner"]} | {data["rest_name"]}')
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
                last_name = await conn.dodo_api(f'https://api.dodois.{data["properties"]}/staff/'
                                                f'members/{person[0]}', data["access"])
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
                    self.logger.error(f'{e} | {data["partner"]} | {data["rest_name"]}')
                try:
                    self.workload_manager = round(managers_worked_hours / len(managers_worked_list), 2)
                except ZeroDivisionError as e:
                    self.logger.error(f'{e} | {data["partner"]} | {data["rest_name"]}')
                try:
                    self.productivity_auto_couriers = round(couriers_auto_orders / couriers_auto_hours, 2)
                except ZeroDivisionError as e:
                    self.logger.error(f'{e} | {data["partner"]} | {data["rest_name"]}')
                try:
                    self.productivity_bike_couriers = round(couriers_bike_orders / couriers_bike_hours, 2)
                except ZeroDivisionError as e:
                    self.logger.error(f'{e} | {data["partner"]} | {data["rest_name"]}')
            except Exception as e:
                self.logger.error(f'{e} | {data["partner"]} | {data["rest_name"]}')
        self.logger.info(f'{data["partner"]} | {data["rest_name"]} | OK')
