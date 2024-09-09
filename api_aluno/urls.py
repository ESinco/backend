from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views


urlpatterns = [
    path('', views.get_all_alunos, name='get_all_alunos'),
    path('cadastrar/', views.criar_aluno, name='criar_aluno'),
    path('login/', views.login_aluno, name='login_aluno'),
    path('<str:matricula>/', views.get_by_matricula_aluno, name='get_by_matricula_aluno'),
    path('historico/importar/', views.upload_historico, name='upload_historico'),
    path('historico/<str:matricula>/', views.visualizar_historico, name='visualizar_historico'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
