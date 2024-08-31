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
from functions.rating import Rating
from functions.couriersorders import CouriersOrders


"""
    Оснавная кофнигурация БД и сервера, берется из configuration/.env
"""
class Config:
    load_dotenv()
    dbase = os.getenv('DBASE')
    user = os.getenv('USER')
    password = os.getenv('PASSWORD')
    host = os.getenv('HOST')


'''
    Классы групп метрик словарь functions
'''
class Settings:
    groups = {
        1: Revenue(), 2: Schedule(), 3: Handover(),
        4: StaffMeal(), 5: Productivity(), 6: Rating(),
        7: Refusal(), 8: Delivery(), 9: Salary(),
        10: Sales(), 11: Shifts(), 12: Staff(),
        13: Stops(), 14: WriteOffs(), 15: CouriersOrders()
    }
