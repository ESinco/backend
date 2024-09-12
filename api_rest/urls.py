from django.urls import path
from . import views

urlpatterns = [
    path('habilidades/', views.get_all_habilidades, name='get_all_habilidades'),
    path('experiencias/', views.get_all_experiencias, name='get_all_experiencias'),
    path('interesses/', views.get_all_interesses, name='get_all_interesses'),
    path('feedbacks/', views.get_all_feedbacks, name='get_all_feedbacks'),
]
