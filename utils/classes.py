from dataclasses import dataclass

'''
    Класс с общими данными для всех групп
'''
@dataclass
class BaseGroup:
    data: dict
    date_start: str
    date_end: str

    @classmethod
    def set_data(cls, data: dict, date_start: str, date_end: str):
        cls.data = data
        cls.date_start = date_start
        cls.date_end = date_end
