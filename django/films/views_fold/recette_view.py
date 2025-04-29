from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from datetime import datetime, date, timedelta
from ..models import Recette, Broadcast, PredictionHistory
from ..business.broadcast_utils import get_start_wednesday, get_or_create_broadcast, get_or_create_recettes

from django.conf import settings
DATEPICKER_FORMAT_STRING = getattr(settings, "DATEPICKER_FORMAT_STRING", "%Y-%m-%d")

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
            prediction_1_per_day = float(prediction_1.first_week_predicted_entries_france) / float(14000)

    prediction_2_per_day = 0.0
    if broadcast.room_2 :
        prediction_2 = PredictionHistory.objects.filter(movie_id = broadcast.room_1).first()
        if prediction_2 :
            prediction_2_per_day = float(prediction_2.first_week_predicted_entries_france) / float(14000)   
    
    for recette in recettes : 
        recette.room_1_predicted = prediction_1_per_day
        recette.room_2_predicted = prediction_2_per_day
        recette.save() 

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
        db_recette.room_1_actual = int(request.POST.get(f'recettes[{index}][room_1_actual]', 0))
        db_recette.room_2_actual = int(request.POST.get(f'recettes[{index}][room_2_actual]', 0))
        db_recette.consumptions = float(request.POST.get(f'recettes[{index}][consumptions]', 0))
        db_recette.save()
        index += 1

    current_wednesday = get_start_wednesday(current_date)
    context = {
        'selected_day' : datetime.combine(current_wednesday, selected_day.time()),
        'recettes': db_recettes,
        'broadcast': db_broadcast,
        'active_tab': 'recettes'
    }
    return render(request, 'films/recette.html', context)





