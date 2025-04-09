from django.db import models

class Movie(models.Model):
    title = models.CharField(max_length=200)
    image_url = models.URLField()
    synopsis = models.TextField()
    genre = models.CharField(max_length=100)
    cast = models.TextField()
    predicted_attendance = models.IntegerField()
    room = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class PredictionHistory(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    predicted_attendance = models.IntegerField()
    actual_attendance = models.IntegerField()
    date = models.DateField()
    accuracy = models.FloatField()

    def __str__(self):
        return f"{self.movie.title} - {self.date}"