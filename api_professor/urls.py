from django.contrib import admin
from django.urls import path

from . import views


urlpatterns = [
    path('', views.get_professores, name='get_all_professores'),
    path('cadastrar/', views.criar_professor, name='criar_professor'),
    path('<int:id_professor>/', views.get_by_id_professor, name='get_by_id_professor'),
    path('login/', views.login_professor, name='login_professor'),
]
