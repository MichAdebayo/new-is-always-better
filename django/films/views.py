import io
import os
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from typing import Optional

import requests

from .models import Movie, PredictionHistory, INITIAL_DATE_FORMAT_STRING
from .business.broadcast_utils import get_start_wednesday, get_or_create_broadcast
from .business.movie_list_utils import get_week_movies

from .data_importer import DataImporter
from .utils import process_movies_dataframe

import csv
import datetime as dt
import logging

model_version = 0

logger = logging.getLogger(__name__)  # Utilise le logger Django pour detecter les erreurs
#__________________________________________________________________________________________________
#
# region top_ten_list
#__________________________________________________________________________________________________
def top_ten_list(request):

    today = dt.datetime.now()

    start_wednesday = get_start_wednesday(today)
    end_wednesday = start_wednesday + dt.timedelta(days=7)

    next_week_movies = get_week_movies(start_wednesday, end_wednesday)
    broadcast = get_or_create_broadcast(end_wednesday)   

    from first_predictor import FirstPredictor
    predictor = FirstPredictor(model_version)

    for movie in next_week_movies :
        if broadcast.room_1 == movie.id :
            movie.room1_checked = True
        else : 
            movie.room1_checked = False

        if broadcast.room_2 == movie.id :
            movie.room2_checked = True
        else : 
            movie.room2_checked = False

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
# region update_top_ten_list
#__________________________________________________________________________________________________
@require_POST
def update_top_ten_list(request):
    room_1_checks = []
    room_2_checks = []
    for key, value in request.POST.items():
        if key.startswith('room1_'):
            movie_room_id = key.split('_')[1]
            if value : 
                try :
                    checked_id = int(movie_room_id)
                    room_1_checks.append(checked_id)
                except: 
                    pass
            
        elif key.startswith('room2_'):
            movie_room_id = key.split('_')[1]
            if value : 
                try :
                    checked_id = int(movie_room_id)
                    room_2_checks.append(checked_id)
                except: 
                    pass
    
    next_week = dt.datetime.now() + dt.timedelta(days=7)
    broadcast = get_or_create_broadcast(next_week)

    broadcast.room_1 = assign_room(room_1_checks, broadcast.room_1)
    broadcast.room_2 = assign_room(room_2_checks, broadcast.room_2)
    broadcast.save()

    return redirect('top_ten_list')  

def assign_room(room_checks : list[int], room_id : Optional[int]) -> Optional[int]: 
    num_checked = len(room_checks)
    if num_checked == 1 :
        return room_checks[0] # the only one
    elif num_checked > 1 :
        if room_id : 
            other_id = next((x for x in room_checks if x != room_id), None) 
            return other_id # the new one
        else : 
            return room_checks[0] # the first one is ok 
    else :
        return None


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

#__________________________________________________________________________________________________
#
# region setings / update_data
#__________________________________________________________________________________________________
from azure_blob_getter import AzureBlobStorageGetter
def update_data(request):
    """
    Mise à jour des films depuis Azure Blob et prédiction via API pour les films importés uniquement.
    """
    if request.method == 'POST':
        try:
            azure_blob_getter = AzureBlobStorageGetter()
            dataframe = azure_blob_getter.get_storage_content()

            if dataframe is None or dataframe.empty:
                messages.error(request, '❌ Le fichier récupéré est vide ou non lisible.')
                logger.warning("DataFrame vide ou None après lecture du blob Azure.")
                return render(request, 'films/settings.html', {
                    'active_tab': 'settings'
                })

            # Importation dans la base et récupération des films importés
            logs, created_movies = process_movies_dataframe(dataframe)

            success_count = sum(1 for log in logs if log.startswith("✅"))
            error_count = len(logs) - success_count

            for log_entry in logs:
                logger.info(log_entry)

            # On récupère les films importés, supposant qu'ils sont dans le DataFrame
            #imported_movies = Movie.objects.filter(title__in=[log.split("✅")[1].strip() for log in logs if log.startswith("✅")])

            # Lancement des prédictions pour les films importés uniquement
            for movie in created_movies:
                try:
                    # Création du payload avec les données du film
                    payload = {
                        "film_title": movie.title,
                        "release_date": movie.release_date.isoformat() if movie.release_date else "",
                        "duration": movie.duration,
                        "age_classification": movie.age_classification,
                        "producers": movie.producers,
                        "director": movie.director,
                        "top_stars": movie.top_stars,
                        "languages": movie.languages,
                        "distributor": movie.distributor,
                        "year_of_production": movie.year_of_production,
                        "film_nationality": movie.film_nationality,
                        "filming_secrets": movie.filming_secrets,
                        "awards": movie.awards,
                        "associated_genres": movie.associated_genres,
                        "broadcast_category": movie.broadcast_category,
                        "trailer_views": movie.trailer_views,
                        "synopsis": movie.synopsis
                    }

                    # Envoi de la requête POST vers l'API de prédiction
                    response = requests.post(
                        f"{settings.FASTAPI_URL}/predict", 
                        json=payload,  # Envoi du payload au format JSON
                        timeout=10
                    )
                    response.raise_for_status()  # Soulever une exception si la réponse est une erreur HTTP
                    prediction_data = response.json()

                    # Sauvegarde de la prédiction dans la base de données
                    PredictionHistory.objects.create(
                        movie=movie,
                        first_week_predicted_entries_france=prediction_data.get("prediction", 0),
                        prediction_error=prediction_data.get("error", 0),
                        model_version=prediction_data.get("version", 1),
                        date=dt.datetime.now().date()
                    )
                    logger.info(f"✅ Prédiction enregistrée pour {movie.title}")

                except Exception as prediction_error:
                    logger.warning(f"❌ Échec de la prédiction pour {movie.title}: {prediction_error}")

            messages.success(request, f"{success_count} films importés, {error_count} erreurs. Prédictions générées pour les films importés.")

        except Exception as e:
            messages.error(request, f"Erreur globale : {str(e)}")
            logger.exception("❌ Erreur critique lors de l'importation ou de la prédiction.")

    return render(request, 'films/settings.html', {
        'active_tab': 'settings'
    })