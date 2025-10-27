from datetime import timedelta, datetime
from db.halls import get_halls_time
from services.helpers import FULL_TIME, generate_time_interval

def generate_buzy_time(alias, date):
    time_start = []
    clear_buzy_time = []
    buzy_time = get_halls_time(alias, date)

    for row in buzy_time:
        start = datetime.fromisoformat(row[1]) - timedelta(minutes=30)
        end = datetime.fromisoformat(row[2]) - timedelta(minutes=30)
        time_start += generate_time_interval(start, end)

    for i in buzy_time:
        start = datetime.fromisoformat(i[1]).strftime('%H:%M')
        end = datetime.fromisoformat(i[2]).strftime('%H:%M')
        clear_buzy_time += (start, end)

    return time_start, clear_buzy_time

def generate_free_time_start(alias, date):
    buzy, clear_buzy_time = generate_buzy_time(alias, date)
    free = []

    for element in FULL_TIME:
        if element not in buzy and element != '21:30' and element != '22:00':
            free.append(element)
    return free, clear_buzy_time

def generate_free_time_end(time_start: str, clear_buzy_time: list[str]) -> list[str]:
    slots = []
    interval = timedelta(minutes=30)
    # Начинаем минимум через 1 час
    current_time = datetime.strptime(time_start, '%H:%M') + 2 * interval

    while True:
        time_str = current_time.strftime('%H:%M')
        slots.append(time_str)
        if time_str in clear_buzy_time or time_str == '22:00':
            break
        current_time += interval

    return slots



clear_buzy = ['13:00', '14:00', '16:00', '20:00']
free_time = ['10:00', '10:30', '11:00', '11:30', '12:00', '14:00', '14:30', '15:00','20:00', '20:30', '21:00']
time = '19:30'

if __name__ == '__main__':
    print(generate_free_time_end(time, clear_buzy))
    #generate_free_time_start(alias, date)

"""
ДО. Исходные данные даты начала с пересечениями
Свободно: ['10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00', '21:30', '22:00']
Занято:                                                         ['13:00', '13:30', '14:00',                            '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00']
Результат:['10:00', '10:30', '11:00', '11:30', '12:00', '12:30',                            '14:30', '15:00', '15:30',                                                                                  '20:30', '21:00', '21:30', '22:00']

ПОСЛЕ. Результат с условием минимальной аренды 1 час.
Свободно: ['10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00', '21:30', '22:00']
Занято:                                                ['12:30', '13:00', '13:30',                            '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30']
Результат:['10:00', '10:30', '11:00', '11:30', '12:00',                            '14:00', '14:30', '15:00',                                                                                  '20:00', '20:30', '21:00']
В результате убираем 2 последних значения 21:30, 22:00 так как они не подходят под ограничения
"""

