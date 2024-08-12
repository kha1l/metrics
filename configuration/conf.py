import os
from dotenv import load_dotenv


"""
    Оснавная кофнигурация БД и сервера, берется из configuration/.env
"""
class Config:
    load_dotenv()
    dbase = os.getenv('DATA_BASE')
    user = os.getenv('USER_NAME')
    password = os.getenv('PASSWORD')
    host = os.getenv('IP')
