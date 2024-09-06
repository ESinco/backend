from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

urlpatterns = [
    path('professor/', views.get_professores, name='get_all_professores'),
    path('professor/cadastrar/', views.criar_professor, name='criar_professor'),
    path('professor/<int:id_professor>/', views.get_by_id_professor, name='get_by_id_professor'),
    path('professor/login/', views.login_professor, name='login_professor'),
    path('aluno/', views.get_all_alunos, name='get_all_alunos'),
    path('aluno/cadastrar/', views.criar_aluno, name='criar_aluno'),
    path('aluno/login/', views.login_aluno, name='login_aluno'),
    path('aluno/<str:matricula>/', views.get_by_matricula_aluno, name='get_by_matricula_aluno'),
    path('projeto/cadastrar/', views.criar_projeto, name='criar_projeto'),
    path('projeto/cadastrar/csv', views.criar_projeto_csv, name='criar_projeto_csv'),
    path('projeto/all/', views.get_projetos, name='get_projetos'),
    path('projeto/<int:id_projeto>/', views.get_by_id_projeto, name='get_by_id_projeto'),
    path('projeto/', views.get_all_projetos_by_professor, name='get_all_projetos_by_professor'),
    path('historico/upload/', views.upload_historico, name='upload_historico'),
    path('historico/<str:matricula>/', views.visualizar_historico, name='visualizar_historico'),
    path('token/atualizar/', TokenRefreshView.as_view(), name='token_refresh')
]