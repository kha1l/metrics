from utils.logging import Logger
from utils.connection import Connect


class Salary:
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

    async def salary_app(self, revenue, revenue_delivery, orders, data, date_start, date_end):
        conn = Connect(data['partner'], data['rest_name'])
        response = await conn.dodo_api(f'https://api.dodois.{data["properties"]}/staff/incentives-by-members',
                                       data["access"], units=data["units"],
                                       _from=date_start, to=date_end)
        try:
            for salary in response['staffMembers']:
                person = await conn.dodo_api(f'https://api.dodois.{data["properties"]}/staff/'
                                             f'members/{salary["staffId"]}', data["access"])
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
            self.logger.error(f'{e} | {data["partner"]} | {data["rest_name"]}')
        try:
            self.kitchencost = round(self.salary_kitchen * data['tax'] / revenue * 100, 2)
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
            self.cost_one_delivery = round(self.salary_couriers / orders, 0)
        except ZeroDivisionError:
            self.cost_one_delivery = 0
        self.award_couriers = round(self.award_couriers, 0)
        self.award_kitchen = round(self.award_kitchen, 0)
        self.salary_trainee = round(self.salary_trainee, 0)
        self.logger.info(f'{data["partner"]} | {data["rest_name"]} | OK')
