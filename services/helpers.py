import os
from datetime import timedelta, datetime
from functools import lru_cache
from dotenv import load_dotenv
from aiogram.fsm.context import FSMContext
from typing import Optional

LIST_HALLS = [
    {
        "name": "Зал 120/Классика",
        "summary": "Зал 120 кв.м. Центр Альфа-Зет м. Достоевская",
        "alias": 'big120',
        "price": 4400
    },
    {
        "name": "Зал 90/Эзотерика",
        "summary": "Зал в эзотерическом стиле со статуей медитируюшего Будды и возможностью цветного освещения.",
        "alias": 'big90',
        "price": 3300
    },
    {
        "name": "Зал 60/Романтика",
        "summary": "Прямоугольный зал с фантазийными элементами в оформлении.",
        "alias": 'medium60',
        "price": 2200
    },
    {
        "name": "Малый зал 30/Практика",
        "summary": "Небольшой зал для мини-групп и индивидуальных сессий.",
        "alias": 'small30',
        "price": 1100
    },
    {
        "name": "Кабинет 16/Массаж",
        "summary": "С кушеткой и местом для беседы с клиентом.",
        "alias": 'small16',
        "price": 600
    }
]

# Кешируем результат чтобы не пересчитывать заново
@lru_cache(maxsize=256)
def generate_time_interval(time_start, time_end):
    slots = []
    interval = timedelta(minutes=30)
    
    while time_start <= time_end:
        slots.append(time_start.strftime('%H:%M'))
        time_start += interval
    return slots


FULL_TIME = generate_time_interval(datetime.strptime('10:00', '%H:%M'), datetime.strptime('22:00', '%H:%M'))

load_dotenv()
ADMIN_IDS = list(map(int, filter(None, (s.strip() for s in os.getenv("LIST_ADMINS", "").split(',')))))

async def get_state(state: FSMContext, key: Optional[str] = None):
    data = await state.get_data()
    return data.get(key) if key is not None else data
