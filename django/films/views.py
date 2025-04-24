import os
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from .models import Movie, PredictionHistory, INITIAL_DATE_FORMAT_STRING

from .data_importer import DataImporter

import csv
import datetime as dt

model_version = 0

#__________________________________________________________________________________________________
#
# region top_ten_list
#__________________________________________________________________________________________________
def top_ten_list(request):

    today = dt.datetime.now()
    start_wednesday = today

    day_of_week = today.weekday() # 0 = Lundi, 6 = Dimanche
    match day_of_week :
        case 0 : start_wednesday = today + dt.timedelta(days=2)
        case 1 : start_wednesday = today + dt.timedelta(days=1)
        case 2 : start_wednesday = today 
        case 3 : start_wednesday = today + dt.timedelta(days=6)
        case 4 : start_wednesday = today + dt.timedelta(days=5)
        case 5 : start_wednesday = today + dt.timedelta(days=4)
        case 6 : start_wednesday = today + dt.timedelta(days=3)

    end_wednesday = start_wednesday + dt.timedelta(days=7)

    # debug only : { 
    start_wednesday = start_wednesday - dt.timedelta(days=14)
    # } debug only 
    
    limit_date = today - dt.timedelta(days=21)
    top_movies = Movie.objects.filter(  
            release_date_fr__gt = limit_date
        ).order_by(
            '-release_date_fr'
        ).prefetch_related('predictions').all()

    next_week_movies = []
    for movie in top_movies :
        release_datetime = dt.datetime.combine(movie.release_date_fr, today.time())
        if release_datetime < start_wednesday :
            continue
    
        if release_datetime >= end_wednesday :
            continue

        next_week_movies.append(movie)

    from first_predictor import FirstPredictor
    predictor = FirstPredictor(model_version)

    for movie in next_week_movies :
        predictions = movie.predictions.all()
        if len(predictions) == 0 :
            (prediction, error) = predictor.predict(movie.title, "")
            if (prediction, error) != (0,0) :
                new_entry = PredictionHistory(
                    movie_id = movie.id, 
                    first_week_predicted_entries_france = prediction, 
                    prediction_error = error,
                    model_version = predictor.model_version,
                    date = today
                )
                new_entry.save()
                movie.last_prediction = prediction
            else : 
                movie.last_prediction = 0
        else :
            movie.last_prediction = predictions.last().first_week_predicted_entries_france

    top_movies = sorted(next_week_movies, key=lambda x: x.last_prediction, reverse=True)

    return render(request, 'films/top_ten_list.html', {
        'movies': top_movies[:10],  
        'active_tab': 'top-ten'
    })


#__________________________________________________________________________________________________
#
# region history
#__________________________________________________________________________________________________
def history(request):
    prediction_history = PredictionHistory.objects.all().order_by('date')
    return render(request, 'films/history.html', {
        'prediction_history': prediction_history,
        'active_tab': 'history'
    })


#__________________________________________________________________________________________________
#
# region settings / import_csv
#__________________________________________________________________________________________________
def settings(request):
    return render(request, 'films/settings.html', {
        'active_tab': 'settings'
    })

def import_csv(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        try:
            # Récupérer le fichier CSV téléchargé
            csv_file = request.FILES['csv_file']
            if not csv_file.name.endswith('.csv'):
                messages.error(request, "Invalid file type. Please upload a CSV file.")
                return render(request, 'films/settings.html',  {
                    'active_tab': 'settings'
                })

            # Stocker temporairement le fichier CSV
            fs = FileSystemStorage()
            filename = fs.save(csv_file.name, csv_file)
            file_path = fs.path(filename)
            print(f"File path: {file_path}")  # Affiche le chemin du fichier

            # Vérification si le fichier existe
            if not os.path.exists(file_path):
                messages.error(request, "File not found.")
                return render(request, 'films/settings.html',  {
                    'active_tab': 'settings'
                })

            # Lire le fichier CSV et remplir la base de données
            with open(file_path, newline='', encoding='utf-8') as file:

                sample = file.read(1024)
                file.seek(0)
                sniffed_dialect = csv.Sniffer().sniff(sample)
                
                reader = csv.DictReader(file, dialect =sniffed_dialect)

                csv_importer = DataImporter()
                csv_importer.set_column_names(reader.fieldnames)

                movie_count = 0
                for row in reader:
                    if csv_importer.try_import_row(row) :
                        movie_count+=1

            # Afficher un message de succès
            messages.success(request, f"{movie_count} movies successfully imported.")
            return render(request, 'films/settings.html',  {
                'active_tab': 'settings'
            })

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return render(request, 'films/settings.html',  {
                'active_tab': 'settings'
            })

        finally:
            # Supprimer le fichier temporaire s'il existe
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                print(f"Temporary file deleted: {file_path}")

    return render(request, 'films/settings.html',  {
        'active_tab': 'settings'
    })


from azure_blob_getter import AzureBlobStorageGetter
def update_data(request):
    """
        don't forget : pip install azure-storage-blob 
    """
    if request.method == 'POST':
        
        azure_blob_getter = AzureBlobStorageGetter()
        dataframe = azure_blob_getter.get_storage_content()
        messages.success(request, 'Bonne nouvelle')
        

    return render(request, 'films/settings.html',  {
        'active_tab': 'settings'
    })

   