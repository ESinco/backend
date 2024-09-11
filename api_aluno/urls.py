from django.contrib import admin
from django.urls import path

from . import views


urlpatterns = [
    path('', views.get_all_alunos, name='get_all_alunos'),
    path('cadastrar/', views.criar_aluno, name='criar_aluno'),
    path('login/', views.login_aluno, name='login_aluno'),
    path('<str:matricula>/', views.get_by_matricula_aluno, name='get_by_matricula_aluno'),
    path('historico/importar/', views.upload_historico, name='upload_historico'),
    path('historico/<str:matricula>/', views.visualizar_historico, name='visualizar_historico'),
    path('interesse_projeto/<int:projeto_id>/', views.interessarNoProjeto, name='interesse_projeto'),
    path('delete_interesse_projeto/<int:projeto_id>/', views.deleteInteressarNoProjeto, name='delete_interesse_projeto'),
]
