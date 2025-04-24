from datetime import date, timedelta
from .models import Broadcast, Recette

def get_or_create_broadcast(current_date : date) -> Broadcast:
    broadcast = Broadcast.objects.filter(
        start_date__lte=current_date, 
        end_date__gte=current_date
    ).first()

    if broadcast :
        return broadcast

    start_wednesday = get_start_wednesday(current_date)
    week_days = get_week_days(start_wednesday)
    broadcast = Broadcast(
        start_date = week_days[0],
        end_date = week_days[6]
    )
    broadcast.save()
    return broadcast

def get_or_create_recettes(broadcast : Broadcast ) -> list[Recette]:
    results = Recette.objects.filter(broadcast_id=broadcast.id)
    if results.count() ==7 :
        return list(results)

    ticket_price = 10.0
    week_days = get_week_days(broadcast.start_date)

    recette_list = []
    for day_date in week_days :
        recette = Recette(
            broadcast_id = broadcast.id,
            date = day_date, 
            ticket_price=ticket_price)  
        recette.save()   
        recette_list.append(recette) 

    return recette_list

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