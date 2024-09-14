from django.contrib import admin
from django.urls import path

from . import views


urlpatterns = [
path('cadastrar/', views.criar_projeto, name='criar_projeto'),
path('cadastrar/csv', views.criar_projeto_csv, name='criar_projeto_csv'),
path('', views.get_projetos, name='get_projetos'),
path('<int:id_projeto>/', views.get_by_id_projeto, name='get_by_id_projeto'),
path('professor/', views.get_all_projetos_by_professor, name='get_all_projetos_by_professor'),
path('aluno/', views.get_all_projetos_by_aluno, name='get_all_projetos_by_aluno'),
path('filtrar/disciplina/', views.filtragem_disciplina, name='filtragem_disciplina'),
path('filtrar/cra/', views.filtragem_cra, name='filtragem_cra'),
path('filtrar/habilidade/', views.filtragem_habilidade, name='filtragem_habilidade'),
path('filtrar/experiencia/', views.filtragem_experiencia, name='filtragem_experiencia'),
path('filtrar/interesse/', views.filtragem_interesse, name='filtragem_interesse'),
]