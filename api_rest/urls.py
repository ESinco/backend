from django.contrib import admin
from django.urls import path, include

from . import views

urlpatterns = [
    path('professor/', views.get_professores, name='get_all_professores'),
    path('professor/<int:id_professor>/', views.get_by_id_professor, name='get_by_id_professor'),
    path('professor/cadastrar/', views.criar_professor, name='criar_professor'),
]