import os
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from .models import Movie, PredictionHistory, DATE_FORMAT_STRING

import csv
import datetime as dt

#__________________________________________________________________________________________________
#
# region dashboard
#__________________________________________________________________________________________________
def dashboard(request):
    
    today = dt.datetime.now()
    limit_date =  today - dt.timedelta(days=14)

    recent_movies = Movie.objects.filter(  
            release_date_fr__gt = limit_date
        ).order_by(
            '-release_date_fr'
        ).prefetch_related('predictions').all()

    for movie in recent_movies :
        predictions = movie.predictions.all()
        if len(predictions) >0 :
            movie.last_prediction = predictions.last().first_week_predicted_entries_france

    selected_movies = recent_movies[:2]
    upcoming_movies = recent_movies[2:] 
    
    context = {
        'selected_movies': selected_movies, 
        'upcoming_movies': upcoming_movies
    }

    return render(request, 'films/dashboard.html', context)

#__________________________________________________________________________________________________
#
# region run_movie_prediction
#__________________________________________________________________________________________________
def run_movie_prediction(request, movie_id) :
    movie = get_object_or_404(Movie, id=movie_id)

    model_version = 0

    from first_predictor import FirstPredictor
    predictor = FirstPredictor(model_version)
    (prediction, error) = predictor.predict(movie.title, "")
    
    import datetime as dt
    today = dt.datetime.now().date()

    new_entry = PredictionHistory(
        movie_id = movie.id, 
        first_week_predicted_entries_france = prediction, 
        prediction_error = error,
        model_version = predictor.model_version,
        date = today
    )
    new_entry.save()

    messages.success(request, f"Action launched for the movie: {movie.title}")
    return redirect('dashboard')  

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
# region financials
#__________________________________________________________________________________________________
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

#__________________________________________________________________________________________________
#
# region settings
#__________________________________________________________________________________________________
def settings(request):
    return render(request, 'films/settings.html')

#__________________________________________________________________________________________________
#
# region import_csv
#__________________________________________________________________________________________________
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
                #reader = csv.DictReader(file )
                reader = csv.DictReader(file, delimiter=';')
                #print("Headers:", reader.fieldnames)  # Affiche les noms des colonnes

                movie_count = 0
                for row in reader:
                    #print(row)  # Affiche les données de chaque ligne

                    try:
                        
                        total_entries_str = str(row['entrees_totales_france']).replace(' ', '')
                        total_entries =  int(total_entries_str) if isinstance (total_entries_str, int)  else 0

                        release_date_france = dt.datetime.strptime(row['date_sortie_france'], DATE_FORMAT_STRING)

                        movie = Movie(
                            title=row['titre'],
                            image_url=row['image_url'],
                            synopsis=row['synopsis'],
                            genre=row['genre_principale'],
                            cast=row['acteurs'], 
                            actual_entries_france = total_entries, 
                            release_date_fr = release_date_france
                        )
                        movie.save()
                        movie_count += 1
                    except Exception as movie_error:
                        print(f"Error inserting movie : {row['titre']}, {release_date_france}")
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