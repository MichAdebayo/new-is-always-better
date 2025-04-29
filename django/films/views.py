import io
import os
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.conf import settings

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

DATEPICKER_FORMAT_STRING = getattr(settings, "DATEPICKER_FORMAT_STRING", "%Y-%m-%d")

model_version = 0

logger = logging.getLogger(__name__)  # Utilise le logger Django pour detecter les erreurs
#__________________________________________________________________________________________________
#
# region top_ten_list
#__________________________________________________________________________________________________
def top_ten_list(request):

    selected_day = dt.datetime.now() + dt.timedelta(days=7) # par défaut
    if request.method == "POST":
        # Récupérer la date envoyée par le formulaire
        selected_date_str = str(request.POST.get('selected_day'))
        selected_date_str = selected_date_str.split('T')[0]
        if selected_date_str:
            selected_day = dt.datetime.strptime(selected_date_str, DATEPICKER_FORMAT_STRING)

    start_wednesday = get_start_wednesday(selected_day)
    end_wednesday = start_wednesday + dt.timedelta(days=7)

    next_week_movies = get_week_movies(start_wednesday, end_wednesday)
    broadcast = get_or_create_broadcast(start_wednesday) # the broadcast if for the next week  

    # from first_predictor import FirstPredictor #unused : the prediction are allredy present in database
    # predictor = FirstPredictor(model_version) #unused : the prediction are allredy present in database

    for movie in next_week_movies :
        if broadcast.room_1 == movie.id :
            movie.room1_checked = True
        else : 
            movie.room1_checked = False

        if broadcast.room_2 == movie.id :
            movie.room2_checked = True
        else : 
            movie.room2_checked = False

        prediction_history = PredictionHistory.objects.filter(movie_id=movie.id).first()
        if not prediction_history :
            # (prediction, error) = predictor.predict(movie.title, movie.release_date_fr) #unused : the prediction are allredy present in database
            # if (prediction, error) != (0,0) : #unused : the prediction are allredy present in database
            #     prediction_history = create_or_update_prediction(movie.id, prediction, error, predictor.model_version, date = selected_day) #unused : the prediction are allredy present in database
            #     movie.last_prediction = prediction #unused : the prediction are allredy present in database
            # else :  #unused : the prediction are allredy present in database
            movie.last_prediction = 0
        else :
            movie.last_prediction = prediction_history.first_week_predicted_entries_france

    top_movies = sorted(next_week_movies, key=lambda x: x.last_prediction, reverse=True)

    return render(request, 'films/top_ten_list.html', {
        'selected_day' : start_wednesday,
        'movies': top_movies[:10],  
        'active_tab': 'top-ten'
    })

#__________________________________________________________________________________________________
#
# region update_top_ten_list
#__________________________________________________________________________________________________
@require_POST
def update_top_ten_list(request):

    selected_day = dt.datetime.now() + dt.timedelta(days=7) # page target week is next week
    # Récupérer la date envoyée par le formulaire
    selected_date_str = str(request.POST.get('other_form_current_date'))
    selected_date_str = selected_date_str.split('T')[0]
    if selected_date_str:
        selected_day = dt.datetime.strptime(selected_date_str, DATEPICKER_FORMAT_STRING)

    next_week = selected_day  

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
from .utils import CustomDate
from .business.prediction_utils import create_or_update_prediction
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

            # normalement ça devrait être "http://film-prediction-api.francecentral.azurecontainer.io:8000/predict"
            fastapi_url = os.getenv("FASTAPI_URL")

            # Lancement des prédictions pour les films importés uniquement
            for movie_data in created_movies:
                logger.info(f"✅ Prédiction enregistrée pour prediction fastapi: {movie_data["title"]}")
                try:
                    # Création du payload avec les données du film
                    payload = {
                        "film_title": movie_data["title"],
                        "release_date": movie_data["release_date"],
                        "duration": movie_data["duration"],
                        "age_classification": movie_data["age_classification"],
                        "producers": movie_data["producers"],
                        "director": movie_data["director"],
                        "top_stars": movie_data["top_stars"],
                        "languages": movie_data["languages"],
                        "distributor": movie_data["distributor"],
                        "year_of_production": movie_data["year_of_production"],
                        "film_nationality": movie_data["film_nationality"],
                        "filming_secrets": movie_data["filming_secrets"],
                        "awards": movie_data["awards"],
                        "associated_genres": movie_data["associated_genres"],
                        "broadcast_category": movie_data["broadcast_category"],
                        "trailer_views": movie_data["trailer_views"],
                        "synopsis": movie_data["synopsis"]
                    }
                    logger.info(f"✅ Prédiction enregistrée pour prediction fastapi")

                     # ✅ Affichage du payload
                    logger.info(f"📦 Payload envoyé : {payload}")

                  
 
                    # Envoi de la requête POST vers l'API de prédiction
                    response = requests.post(
                        fastapi_url, 
                        json=payload,  # Envoi du payload au format JSON
                        timeout=10
                    )

                    response.raise_for_status()  # Soulever une exception si la réponse est une erreur HTTP
                    logger.info(f"📊 Résultat de la prédiction : {response.status_code }")
                    if response.status_code == 200:
                        prediction_data = response.json()
                        logger.info(f"📊 Résultat de la prédiction : {prediction_data}")

                    prediction_data = response.json()
                    #print(prediction_data)
                    logger.info(f"✅ Prédiction enregistrée pour prediction fastapi")
                    # Sauvegarde de la prédiction dans la base de données
                    try:
                        
                        movie_title = movie_data["title"]
                        movie_date = CustomDate().parse_french_date(movie_data["release_date"])

                        movie_obj = Movie.objects.filter(title=movie_title, release_date_fr=movie_date).first()
                        movie_id = movie_obj.id

                        first_week_predicted_entries_france=int(prediction_data.get("predicted_fr_entries", 0))
                        prediction_deviation = 0 # haaaaaaaaannnn c'est maaaal !
                        model_version=int(prediction_data.get("version", 0))
                        date_prediction=dt.datetime.now().date()

                        prediction_history = create_or_update_prediction(movie_id, first_week_predicted_entries_france, prediction_deviation, model_version, date_prediction)
                        
                        logger.info(f"✅ Prédiction enregistrée pour {movie_data["title"]}")
                    except Movie.DoesNotExist:
                        print(f"Aucun film trouvé avec le titre : {movie_title}")

                except Exception as prediction_error:
                    logger.warning(f"❌ Échec de la prédiction pour {movie_data["title"]}: {prediction_error}")

            messages.success(request, f"{success_count} films importés, {error_count} erreurs. Prédictions générées pour les films importés.")

        except Exception as e:
            messages.error(request, f"Erreur globale : {str(e)}")
            logger.exception("❌ Erreur critique lors de l'importation ou de la prédiction.")

    return render(request, 'films/settings.html', {
        'active_tab': 'settings'
    })