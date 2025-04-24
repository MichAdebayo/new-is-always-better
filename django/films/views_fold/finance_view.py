import os
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from ..models import Recette, Broadcast
from ..broadcast_utils import get_or_create_broadcast, get_or_create_recettes

import csv
import datetime as dt
from decimal import Decimal

ROOM_1_MAX_OCCUPATION = 120
ROOM_2_MAX_OCCUPATION = 100

#__________________________________________________________________________________________________
#
# region finance
#__________________________________________________________________________________________________
def finance(request):

    current_date = dt.date.today()
    previous_date = current_date - dt.timedelta(days=7)

    current_result = compute_finance_data(current_date)
    previous_result = compute_finance_data(previous_date)
    
    weekly_revenue = current_result["weekly_revenue"]
    weekly_costs = current_result["weekly_costs"]
    weekly_profit = current_result["weekly_profit"]
    occupation_rate = current_result["occupation_rate"]

    revenue_diff = get_percent_variation(float(current_result["weekly_revenue"]), float(previous_result["weekly_revenue"]))
    profit_diff =  get_percent_variation(float(current_result["weekly_profit"]), float(previous_result["weekly_profit"]))
    occupation_diff = current_result["occupation_rate"] - previous_result["occupation_rate"]
   
    metrics = {
        'weekly_revenue': weekly_revenue,
        'weekly_costs': weekly_costs,
        'weekly_profit': weekly_profit,
        'occupation_rate': occupation_rate,
        'revenue_diff' : revenue_diff,
        'profit_diff' : profit_diff,
        'occupation_diff' : occupation_diff
    }
    
    return render(request, 'films/financials.html', {
        'metrics': metrics,
        'active_tab': 'finance'
    })

def compute_finance_data(target_date : dt.date) -> dict :

    broadcast = get_or_create_broadcast(target_date)
    recettes = get_or_create_recettes(broadcast)

    total_recettes = Decimal(0.0)

    occupation = 0
    for recette in recettes : 
        occupation = occupation + recette.room_1_actual + recette.room_2_actual
        total_recettes = total_recettes + Decimal(recette.ticket_price * recette.room_1_actual) 
        total_recettes = total_recettes + Decimal(recette.ticket_price * recette.room_2_actual) 
        total_recettes = total_recettes + Decimal(recette.consumptions)
    
    occupation_rate = 100.0 * float(occupation) / float( 7 * (ROOM_1_MAX_OCCUPATION+ROOM_2_MAX_OCCUPATION))

    finance_data = {}
    finance_data["weekly_revenue"] = total_recettes
    finance_data["weekly_costs"]= Decimal(4900.0)
    finance_data["weekly_profit"] = finance_data["weekly_revenue"] - finance_data["weekly_costs"] 
    finance_data["occupation_rate"] = occupation_rate
    
    return finance_data

def get_percent_variation(current_value : float, previous_value: float) -> float:
    if previous_value == 0 :
        if current_value == 0 : return 0.0
        elif current_value > 0 : return 100.0
        else : return -100.0

    reference = abs(previous_value)
    difference = current_value - previous_value

    variation = 100.0 * (difference / reference)
    return variation