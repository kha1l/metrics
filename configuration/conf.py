import os
from dotenv import load_dotenv
from functions.delivery import Delivery
from functions.handover import Handover
from functions.productivity import Productivity
from functions.staffmeal import StaffMeal
from functions.refusal import Refusal
from functions.revenue import Revenue


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
        1: Delivery(), 3: Handover(),
        4: StaffMeal(), 5: Productivity(),
        7: Refusal(), 8: Revenue()
    }
