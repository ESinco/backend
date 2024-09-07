from django.contrib import admin
from django.urls import path

from . import views


urlpatterns = [
path('cadastrar/', views.criar_projeto, name='criar_projeto'),
path('cadastrar/csv', views.criar_projeto_csv, name='criar_projeto_csv'),
path('', views.get_projetos, name='get_projetos'),
path('<int:id_projeto>/', views.get_by_id_projeto, name='get_by_id_projeto'),
path('professor/', views.get_all_projetos_by_professor, name='get_all_projetos_by_professor')
]