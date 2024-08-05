from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path('professor/', views.get_professores, name='get_all_professores'),
    path('professor/<int:id_professor>/', views.get_by_id_professor, name='get_by_id_professor'),
    path('professor/cadastrar/', views.criar_professor, name='criar_professor'),
    path('projeto/all/', views.get_projetos, name='get_projetos'),
    path('projeto/cadastrar/', views.criar_projeto, name='criar_projeto'),
    path('projeto/<int:id_projeto>/', views.get_by_id_projeto, name='get_by_id_projeto'),
    path('projeto/', views.get_all_projetos_by_professor, name='get_all_projetos_by_professor'),
]