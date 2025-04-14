from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('movie/<int:movie_id>/run-prediction/', views.run_movie_prediction, name='run_movie_prediction'),
    path('history/', views.history, name='history'),
    path('financials/', views.financials, name='financials'),
    path('settings/', views.settings, name='settings'),
    path('import_csv/', views.import_csv, name='import_csv'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)