from ..models import Movie, PredictionHistory
import datetime as dt
    
def get_week_movies(starting_wednesday : dt.date, ending_wednesday : dt.date) -> list[Movie]:
    week_movies = Movie.objects.filter(  
            release_date_fr__gte = starting_wednesday, 
            release_date_fr__lt = ending_wednesday 
        ).order_by(
            '-release_date_fr'
        ).prefetch_related(
            'predictions'
        )
    
    return list(week_movies)
    