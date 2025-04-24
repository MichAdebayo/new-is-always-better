from django.urls import path
from . import views
from .views_fold import dashboard_view, recette_view, finance_view

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', dashboard_view.dashboard, name='dashboard'),
    path('movie/<int:movie_id>/run-prediction/', dashboard_view.run_movie_prediction, name='run_movie_prediction'),
    path('top-ten/', views.top_ten_list, name='top_ten_list'),
    #path('history/', views.history, name='history'),
    path('recettes/', recette_view.recettes_view, name='recettes'),
    path('recettes/update/', recette_view.update_recettes, name='update_recettes'),
    path('finance/', finance_view.finance, name='finance'),
    path('settings/', views.settings, name='settings'),
    path('update_data/', views.update_data, name='update_data'),
    path('import_csv/', views.import_csv, name='import_csv'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)