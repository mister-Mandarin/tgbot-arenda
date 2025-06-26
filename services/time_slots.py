from datetime import timedelta, datetime

time_list = [(datetime.strptime('10:00', '%H:%M') + timedelta(minutes=30)*i).strftime('%H:%M') for i in range(((21-10)*60)//30 + 1)]


