from django.shortcuts import render
from .models import Recette, BroadCast
from datetime import date, timedelta
from days_of_week_utils import get_start_wednesday, get_week_days

def recettes_view(request):

    start_date = end_date = date.today()
    recettes = Recette.objects.order_by('date')
    
    if recettes.exists():
        start_date = recettes.first().date
        end_date = recettes.last().date
    else:
        create_current_week(date.today())
        start_date = end_date = date.today()

    context = {
        'recettes': recettes,
        'broadcast': {
            'start_date': start_date,
            'end_date': end_date,
            'room_1': recettes.first().room_1_movie.title if recettes else '',
            'room_2': recettes.first().room_2_movie.title if recettes else ''
        }
    }
    return render(request, 'recettes/liste_recettes.html', context)

def create_current_week(current_date : date):
    start_wednesday = get_start_wednesday(current_date)
    week_days = get_week_days(start_wednesday)