import os
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Movie, PredictionHistory
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import csv


def dashboard(request):
    # Obtenez tous les films
    selected_movies = Movie.objects.all()[:2]  # Les deux premiers films
    upcoming_movies = Movie.objects.all()[2:]  # Tous les films à venir

    context = {
        'selected_movies': selected_movies,
        'upcoming_movies': upcoming_movies,
    }

    return render(request, 'films/dashboard.html', context)

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
                        movie = Movie(
                            title=row['titre'],
                            image_url=row['image_url'],
                            synopsis=row['synopsis'],
                            genre=row['genre_principale'],
                            cast=row['acteurs'],
                            predicted_attendance = 0,  # Valeur par défaut pour la prédiction
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