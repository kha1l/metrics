import os
from dotenv import load_dotenv
from functions.delivery import Delivery
from functions.handover import Handover
from functions.productivity import Productivity
from functions.staffmeal import StaffMeal
from functions.refusal import Refusal
from functions.revenue import Revenue
from functions.schedule import Schedule
from functions.sales import Sales
from functions.salary import Salary
from functions.shifts import Shifts
from functions.staff import Staff
from functions.stops import Stops
from functions.writeoffs import WriteOffs


"""
    Оснавная кофнигурация БД и сервера, берется из configuration/.env
"""
class Config:
    load_dotenv()
    dbase = os.getenv('DATA_BASE')
    user = os.getenv('USER_NAME')
    password = os.getenv('PASSWORD')
    host = os.getenv('IP')

class Settings:
    functions = {
        1: Delivery(), 2: Sales(), 3: Handover(),
        4: StaffMeal(), 5: Productivity(), 6: '',
        7: Refusal(), 8: Revenue(), 9: Salary(),
        10: Schedule(), 11: Shifts(), 12: Staff(),
        13: Stops(), 14: WriteOffs()
    }
