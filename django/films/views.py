import io
import os
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
import requests

from .models import Movie, PredictionHistory, INITIAL_DATE_FORMAT_STRING

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
            for movie_data in created_movies:
                logger.info(f"✅ Prédiction enregistrée pour prediction fastapi")
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

                    try:
                        # Envoi de la requête POST vers l'API de prédiction
                        response = requests.post(
                            "http://film-prediction-api.francecentral.azurecontainer.io:8000/predict", 
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
                    
                    except Exception as prediction_response_error:
                        logger.warning(f"❌ Échec de la réponse de prédiction: {prediction_response_error}")

                    # Sauvegarde de la prédiction dans la base de données
                    try:
                        movie_title = prediction_data.get("film_title")
                        movie_obj = Movie.objects.get(title=movie_title)
                        movie_id = movie_obj.id
                        
                        PredictionHistory.objects.create(
                        first_week_predicted_entries_france=prediction_data.get("predicted_fr_entries", 0),
                        model_version=prediction_data.get("version", 0),
                        date=dt.datetime.now().date(),
                        movie_id =movie_id
                        )
                        logger.info(f"✅ Prédiction enregistrée")
                    
                    except Movie.DoesNotExist:
                        print(f"Aucun film trouvé avec le titre : {movie_title}")

                except Exception as prediction_error:
                    logger.warning(f"❌ Échec de la prédiction: {prediction_error}")

            messages.success(request, f"{success_count} films importés, {error_count} erreurs. Prédictions générées pour les films importés.")

        except Exception as e:
            messages.error(request, f"Erreur globale : {str(e)}")
            logger.exception("❌ Erreur critique lors de l'importation ou de la prédiction.")

    return render(request, 'films/settings.html', {
        'active_tab': 'settings'
    })