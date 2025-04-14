import os
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Movie, PredictionHistory
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import csv


def dashboard(request):
    
    selected_movies = Movie.objects.prefetch_related('predictions').all()[:2]  # Les deux premiers films
    upcoming_movies = Movie.objects.prefetch_related('predictions').all()[2:]  # Tous les films à venir

    predictions = []
    for movie in selected_movies :
        predictions = movie.predictions.all()
        if len(predictions) >0 :
            movie.last_prediction = predictions.last().first_week_predicted_entries_france

    for movie in upcoming_movies :
        predictions = movie.predictions.all()
        if len(predictions) >0 :
            movie.last_prediction = predictions.last().first_week_predicted_entries_france
    
    context = {
        'selected_movies': selected_movies, 
        'upcoming_movies': upcoming_movies,
        'predictions': predictions,
    }

    return render(request, 'films/dashboard.html', context)

def run_movie_prediction(request, movie_id) :
    movie = get_object_or_404(Movie, id=movie_id)

    # chargement modèle
    import joblib
    from sklearn.pipeline import Pipeline
    dummy_model: Pipeline  = joblib.load("dummy_pipeline.joblib")

    # chargement data 
    import pandas as pd
    original_csv = pd.read_csv('static/films_jp_box.csv')
    
    movie_row = original_csv[original_csv['titre']== movie.title].iloc[[0]]
    prediction = dummy_model.predict(movie_row)

    pred_int = int(prediction[0])
    import datetime as dt

    today = dt.datetime.now().date()

    new_entry = PredictionHistory(
        movie_id = movie.id, 
        first_week_predicted_entries_france = pred_int, 
        metric_score = float(pred_int/4),
        model_version = 0,
        date = today
    )
    new_entry.save()

    messages.success(request, f"Action launched for the film: {movie.title}")
    return redirect('dashboard')  

def history(request):
    prediction_history = PredictionHistory.objects.all().order_by('date')
    return render(request, 'films/history.html', {
        'prediction_history': prediction_history,
        'active_tab': 'history'
    })

def financials(request):
    weekly_revenue = 9000
    weekly_costs = 4900
    weekly_profit = weekly_revenue - weekly_costs
    occupancy_rate = 85
    
    metrics = {
        'weekly_revenue': weekly_revenue,
        'weekly_profit': weekly_profit,
        'occupancy_rate': occupancy_rate,
        'weekly_costs': weekly_costs
    }
    
    return render(request, 'films/financials.html', {
        'metrics': metrics,
        'active_tab': 'financials'
    })

def settings(request):
    return render(request, 'films/settings.html')

def import_csv(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        try:
            # Récupérer le fichier CSV téléchargé
            csv_file = request.FILES['csv_file']
            if not csv_file.name.endswith('.csv'):
                messages.error(request, "Invalid file type. Please upload a CSV file.")
                return render(request, 'films/settings.html')

            # Stocker temporairement le fichier CSV
            fs = FileSystemStorage()
            filename = fs.save(csv_file.name, csv_file)
            file_path = fs.path(filename)
            print(f"File path: {file_path}")  # Affiche le chemin du fichier

            # Vérification si le fichier existe
            if not os.path.exists(file_path):
                messages.error(request, "File not found.")
                return render(request, 'films/settings.html')

            # Lire le fichier CSV et remplir la base de données
            with open(file_path, newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                print("Headers:", reader.fieldnames)  # Affiche les noms des colonnes

                movie_count = 0
                for row in reader:
                    print(row)  # Affiche les données de chaque ligne

                    try:
                        total_entries = int(str(row['entrees_totales_france']).replace(' ', ''))

                        movie = Movie(
                            title=row['titre'],
                            image_url=row['image_url'],
                            synopsis=row['synopsis'],
                            genre=row['genre_principale'],
                            cast=row['acteurs'], 
                            actual_entries_france = total_entries, 
                        )
                        movie.save()
                        movie_count += 1
                    except Exception as movie_error:
                        print(f"Error inserting movie: {movie_error}")
                        continue  # Continue même si une ligne échoue

            # Afficher un message de succès
            messages.success(request, f"{movie_count} movies successfully imported.")
            return render(request, 'films/settings.html')

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return render(request, 'films/settings.html')

        finally:
            # Supprimer le fichier temporaire s'il existe
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                print(f"Temporary file deleted: {file_path}")

    return render(request, 'films/settings.html')