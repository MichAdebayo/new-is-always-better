from django.db import models

INITIAL_DATE_FORMAT_STRING = "%d/%m/%Y"
ALLOCINE_DATE_FORMAT_STRING = "%d %B %Y"
ALLOCINE_DATE_FORMAT_STRING2 = "%B %Y"

class Movie(models.Model):
    title = models.CharField(max_length=200)
    image_url = models.URLField()
    synopsis = models.TextField()
    genre = models.CharField(max_length=100)
    cast = models.TextField()
    release_date_fr = models.DateField(null=True, default=None)
    first_week_actual_entries_france = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class PredictionHistory(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='predictions')
    first_week_predicted_entries_france = models.IntegerField(default=0)
    prediction_error = models.IntegerField(default=0)
    model_version = models.IntegerField(default=0)
    date = models.DateField()
   
    def __str__(self):
        return f"{self.movie.title} - {self.date}"
    
class Boadcast (models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    room_1 =  models.IntegerField(null=True, blank=True)
    room_2 =  models.IntegerField(null=True, blank=True)

    
class Recette (models.Model):
    date = models.DateField()

    ticket_price = models.DecimalField( max_digits=10, decimal_places=2, default=0.00)
    
    room_1_movie = models.ForeignKey(Movie, on_delete=models.SET_NULL, null=True, related_name = 'recettes')
    room_1_predicted = models.FloatField(default=0.0)  
    room_1_actual = models.IntegerField(default=0)
    room_1_amount = models.DecimalField( max_digits=10, decimal_places=2, default=0.00)

    room_2_movie = models.ForeignKey(Movie)
    room_2_predicted = models.FloatField(default=0.0)  
    room_2_actual = models.IntegerField(default=0)
    room_2_amount = models.DecimalField( max_digits=10, decimal_places=2, default=0.00)

    consumptions = models.DecimalField( max_digits=10, decimal_places=2, default=0.00)