from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from datetime import datetime, date, timedelta
from ..models import Recette, Broadcast, PredictionHistory, NB_MAX_ROOM1, NB_MAX_ROOM2
from ..business.broadcast_utils import get_start_wednesday, get_or_create_broadcast, get_or_create_recettes

from django.conf import settings
DATEPICKER_FORMAT_STRING = getattr(settings, "DATEPICKER_FORMAT_STRING", "%Y-%m-%d")

from decimal import Decimal

#______________________________________________________________________________
# 
# region recettes_view
#______________________________________________________________________________
def recettes_view(request):

    selected_day = datetime.now() # par défaut
    if request.method == "POST":
        # Récupérer la date envoyée par le formulaire
        selected_date_str = str(request.POST.get('selected_day'))
        selected_date_str = selected_date_str.split('T')[0]
        if selected_date_str:
            selected_day = datetime.strptime(selected_date_str, DATEPICKER_FORMAT_STRING)

    current_date = datetime.date(selected_day)
    current_wednesday = get_start_wednesday(current_date)

    broadcast = get_or_create_broadcast(current_wednesday)
    recettes = get_or_create_recettes(broadcast)

    prediction_1_per_day = 0.0
    if broadcast.room_1 :
        prediction_1 = PredictionHistory.objects.filter(movie_id = broadcast.room_1).first()
        if prediction_1 :
            #prediction_1_per_day = float(prediction_1.first_week_predicted_entries_france) / float(14000)
            prediction_1_per_day = float(prediction_1.first_week_predicted_entries_france) / float(7)

    prediction_2_per_day = 0.0
    if broadcast.room_2 :
        prediction_2 = PredictionHistory.objects.filter(movie_id = broadcast.room_1).first()
        if prediction_2 :
            #prediction_2_per_day = float(prediction_2.first_week_predicted_entries_france) / float(14000)   
            prediction_2_per_day = float(prediction_2.first_week_predicted_entries_france) / float(7)   
    
    for recette in recettes : 
        recette.room_1_predicted = prediction_1_per_day
        recette.room_2_predicted = prediction_2_per_day
        recette = update_recette_fields(recette, recette.room_1_actual, recette.room_2_actual, recette.consumptions)
        recette.save() 

    # for display only
    for recette in recettes : 
        recette.room_1_predicted = int(recette.room_1_predicted)
        recette.room_2_predicted = int(recette.room_2_predicted)
        recette.day_name = recette.date.strftime("%A")
        recette.total = recette.ticket_price * recette.room_1_actual + recette.ticket_price * recette.room_2_actual + recette.consumptions
    
    context = {
        'selected_day' : datetime.combine(current_wednesday, selected_day.time()),
        'recettes': recettes,
        'broadcast': broadcast,
        'active_tab': 'recettes'
    }
    return render(request, 'films/recette.html', context)

#______________________________________________________________________________
# 
# region update_recettes
#______________________________________________________________________________
@require_POST
def update_recettes(request):

    recettes_data = request.POST.getlist('recettes')

    selected_day = datetime.now() 
    # Récupérer la date envoyée par le formulaire
    selected_date_str = str(request.POST.get('other_form_current_date'))
    selected_date_str = selected_date_str.split('T')[0]
    if selected_date_str:
        selected_day = datetime.strptime(selected_date_str, DATEPICKER_FORMAT_STRING)

    current_date = selected_day.date()

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
        room_1_entries = int(request.POST.get(f'recettes[{index}][room_1_actual]', 0))  
        room_2_entries = int(request.POST.get(f'recettes[{index}][room_2_actual]', 0))
        consumptions = Decimal(request.POST.get(f'recettes[{index}][consumptions]', 0))

        db_recette = update_recette_fields(db_recette, room_1_entries, room_2_entries, consumptions)
        db_recette.save()
        index += 1
    
    # for display only
    for db_recette in db_recettes : 
        db_recette.room_1_predicted = int(db_recette.room_1_predicted) # redefinition of room_1_predicted
        db_recette.room_2_predicted = int(db_recette.room_2_predicted)  # redefinition of room_2_predicted
        db_recette.day_name = db_recette.date.strftime("%A")
        db_recette.total = db_recette.ticket_price * db_recette.room_1_actual + db_recette.ticket_price * db_recette.room_2_actual + db_recette.consumptions
    

    current_wednesday = get_start_wednesday(current_date)
    context = {
        'selected_day' : datetime.combine(current_wednesday, selected_day.time()),
        'recettes': db_recettes,
        'broadcast': db_broadcast,
        'active_tab': 'recettes'
    }
    return render(request, 'films/recette.html', context)


# added to do the same thing every times this is needed
def update_recette_fields(db_object : Recette, entries1 : int, entries2:int, consumptions: Decimal ) -> Recette :
    if entries1 > NB_MAX_ROOM1 :
        entries1 = NB_MAX_ROOM1
    elif entries1 <0 : 
        entries1 = 0

    db_object.room_1_actual =  entries1 
    db_object.room_1_amount =  db_object.ticket_price * db_object.room_1_actual

    if entries2 > NB_MAX_ROOM2 :
        entries2 = NB_MAX_ROOM2
    elif entries2 <0 : 
        entries2 = 0

    db_object.room_2_actual =  entries2   
    db_object.room_2_amount =  db_object.ticket_price * db_object.room_2_actual
    db_object.consumptions = consumptions
    return db_object