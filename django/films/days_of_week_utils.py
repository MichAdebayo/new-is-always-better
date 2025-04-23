from datetime import date, timedelta

def get_start_wednesday(current_date : date) -> date:
    start_wednesday = current_date

    day_of_week = current_date.weekday() # 0 = Lundi, 6 = Dimanche
    match day_of_week :
        case 0 : start_wednesday = current_date + timedelta(days=2)
        case 1 : start_wednesday = current_date + timedelta(days=1)
        case 2 : start_wednesday = current_date 
        case 3 : start_wednesday = current_date + timedelta(days=6)
        case 4 : start_wednesday = current_date + timedelta(days=5)
        case 5 : start_wednesday = current_date + timedelta(days=4)
        case 6 : start_wednesday = current_date + timedelta(days=3)

    return start_wednesday

def get_week_days(start_date : date) -> list[date]:
    days = [] 
    days.append(start_date)
    days.append(start_date + timedelta(days=1))
    days.append(start_date + timedelta(days=2))
    days.append(start_date + timedelta(days=3))
    days.append(start_date + timedelta(days=4))
    days.append(start_date + timedelta(days=5))
    days.append(start_date + timedelta(days=6))
    return days