from django.contrib import admin
from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView
from . import views


urlpatterns = [
    path('login/renovar/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', views.login, name='login'),
    path('habilidades/', views.get_all_habilidades, name='get_all_habilidades'),
    path('experiencias/', views.get_all_experiencias, name='get_all_experiencias'),
    path('interesses/', views.get_all_interesses, name='get_all_interesses'),
    path('feedbacks/', views.get_all_feedbacks, name='get_all_feedbacks'),
    path('disciplinas/', views.get_all_disciplinas, name='get_all_disciplinas'),
]
