from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from datetime import datetime, date, timedelta
from ..models import Recette, Broadcast
from ..days_of_week_utils import get_start_wednesday, get_week_days

#______________________________________________________________________________
# 
# region recettes_view
#______________________________________________________________________________
def recettes_view(request):

    current_date = date.today()

    broadcast = get_or_create_broadcast(current_date)
    recettes = get_or_create_recettes(broadcast)
    
    for recette in recettes : 
        recette.day_name = recette.date.strftime("%A")
        recette.total = recette.ticket_price * recette.room_1_actual + recette.ticket_price * recette.room_2_actual + recette.consumptions
    
    context = {
        'recettes': recettes,
        'broadcast': broadcast
    }
    return render(request, 'films/recette.html', context)

#______________________________________________________________________________
# 
# region update_recettes
#______________________________________________________________________________
@require_POST
def update_recettes(request):
    recettes_data = request.POST.getlist('recettes')
    
    current_date = date.today()

    db_broadcast = get_or_create_broadcast(current_date)
    db_recettes = get_or_create_recettes(db_broadcast)

    index = 0
    while f'recettes[{index}][day]' in request.POST:
        day_str = request.POST.get(f'recettes[{index}][day]')
        db_recette = None
        for current_db_recette in db_recettes : 
            day_name = current_db_recette.date.strftime("%A")
            if day_str ==day_name :
                db_recette = current_db_recette
                break
        
        if not db_recette :
            continue

        # Mise à jour des champs
        db_recette.room_1_actual = int(request.POST.get(f'recettes[{index}][room_1_actual]', 0))
        db_recette.room_2_actual = int(request.POST.get(f'recettes[{index}][room_2_actual]', 0))
        db_recette.consumptions = float(request.POST.get(f'recettes[{index}][consumptions]', 0))
        db_recette.save()
        index += 1

    return redirect('recettes') 

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



