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
path('<int:id_projeto>/editar/', views.editar_projeto, name='editar_projeto'),
path('cadastrar-lista/', views.salvar_filtragem, name='salvar_filtragem'),
path('editar-lista/<int:id_lista>', views.editar_filtragem, name='editar_filtragem'),
path('cadastrar_colaborador/<int:id_projeto>/<str:email_colaborador>/',views.cadastrar_colaborador, name='cadastrar_colaborador')
]