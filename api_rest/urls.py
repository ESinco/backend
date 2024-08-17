from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path('professor/', views.get_professores, name='get_all_professores'),
    path('professor/cadastrar/', views.criar_professor, name='criar_professor'),
    path('professor/<int:id_professor>/', views.get_by_id_professor, name='get_by_id_professor'),
    path('aluno/', views.get_all_alunos, name='get_all_alunos'),
    path('aluno/cadastrar/', views.criar_aluno, name='criar_aluno'),
    path('aluno/<str:matricula>/', views.get_by_matricula_aluno, name='get_by_matricula_aluno'),
    path('projeto/cadastrar/', views.criar_projeto, name='criar_projeto'),
    path('projeto/all/', views.get_projetos, name='get_projetos'),
    path('projeto/<int:id_projeto>/', views.get_by_id_projeto, name='get_by_id_projeto'),
    path('projeto/', views.get_all_projetos_by_professor, name='get_all_projetos_by_professor'),
]