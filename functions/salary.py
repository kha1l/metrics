from utils.logging import Logger
from utils.connection import Connect
from utils.classes import BaseGroup


'''
    Набор метрик с эндпоинта вознаграждения /staff/incentives-by-members:
    1. salary_kitchen - зарплата кухни
    2. salary_couriers - зарплата курьера
    3. salary_trainee - зарплата стажеров
    4. award_kitchen - премии кухни
    5. award_couriers - премии курьеров
    6. kitchencost - процент зарплаты кухни от выручки
    7. deliverycost - процент зарплаты курьеров от выручки доставки
    8. laborcost - процент зарплаты курьеров и кухни от выручки
    9. cost_one_delivery - стоимость одной доставки
    10. salary_staff - зарплата курьеров и кухни
'''
class Salary(BaseGroup):
    def __init__(self):
        self.salary_kitchen = 0
        self.salary_couriers = 0
        self.salary_trainee = 0
        self.award_kitchen = 0
        self.award_couriers = 0
        self.kitchencost = 0
        self.deliverycost = 0
        self.laborcost = 0
        self.cost_one_delivery = 0
        self.salary_staff = 0
        self.logger = Logger('SALARY')

    async def app(self, revenue, revenue_delivery, orders_delivery):
        conn = Connect(self.data['partner_id'], self.data['name'])
        response = await conn.dodo_api(f'https://api.dodois.{self.data["properties"]}/staff/incentives-by-members',
                                       self.data["access"], units=self.data["uuid"],
                                       _from=self.date_start, to=self.date_end)
        try:
            for salary in response['staffMembers']:
                person = await conn.dodo_api(f'https://api.dodois.{self.data["properties"]}/staff/'
                                             f'members/{salary["staffId"]}', self.data["access"])
                staff, position = person['staffType'], person['positionName']
                for shift in salary['shiftsDetailing']:
                    staff = shift['staffType']
                    position = shift['positionName']
                    if staff == 'Courier':
                        self.salary_couriers += shift['totalWage']
                        self.award_couriers += shift['shiftPremiums'] + shift['seniorityBonus']
                    else:
                        self.salary_kitchen += shift['totalWage']
                        self.award_kitchen += shift['shiftPremiums'] + shift['seniorityBonus']
                        if position.startswith('Стажер-') and position != 'Стажер-менеджер':
                            self.salary_trainee += shift['totalWage']
                for prem in salary['premiums']:
                    if staff == 'Courier':
                        self.salary_couriers += prem['amount']
                        self.award_couriers += prem['amount']
                    else:
                        self.award_kitchen += prem['amount']
                        self.salary_kitchen += prem['amount']
                        if position.startswith('Стажер-') and position != 'Стажер-менеджер':
                            self.salary_trainee += prem['amount']
        except Exception as e:
            self.logger.error(f'{e} | {self.data["partner_id"]} | {self.data["name"]}')
        try:
            self.kitchencost = round(self.salary_kitchen * self.data['tax'] / revenue * 100, 2)
        except ZeroDivisionError:
            self.kitchencost = 0
        try:
            self.deliverycost = round(self.salary_couriers / revenue_delivery * 100, 2)
        except ZeroDivisionError:
            self.deliverycost = 0
        self.salary_couriers = round(self.salary_couriers, 0)
        self.salary_kitchen = round(self.salary_kitchen, 0)
        self.salary_staff = self.salary_couriers + self.salary_kitchen
        try:
            self.laborcost = round(self.salary_staff / revenue * 100, 2)
        except ZeroDivisionError:
            self.laborcost = 0
        try:
            self.cost_one_delivery = round(self.salary_couriers / orders_delivery, 0)
        except ZeroDivisionError:
            self.cost_one_delivery = 0
        self.award_couriers = round(self.award_couriers, 0)
        self.award_kitchen = round(self.award_kitchen, 0)
        self.salary_trainee = round(self.salary_trainee, 0)
        self.logger.info(f'{self.data["partner_id"]} | {self.data["name"]} | OK')
