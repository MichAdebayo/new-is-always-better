from django.urls import path
from . import views
from . import recette_view

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('movie/<int:movie_id>/run-prediction/', views.run_movie_prediction, name='run_movie_prediction'),
    path('top-ten/', views.top_ten_list, name='top_ten_list'),
    #path('history/', views.history, name='history'),
    path('recettes/', recette_view.recettes_view, name='recettes'),
    path('financials/', views.financials, name='financials'),
    path('settings/', views.settings, name='settings'),
    path('update_data/', views.update_data, name='update_data'),
    path('import_csv/', views.import_csv, name='import_csv'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)