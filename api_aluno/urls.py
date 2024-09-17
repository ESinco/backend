from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views


urlpatterns = [
    path('cadastrar/', views.criar_aluno, name='criar_aluno'),
    path('historico/importar/', views.upload_historico, name='upload_historico'),
    path('historico/<str:matricula>/', views.visualizar_historico, name='visualizar_historico'),
    path('interesse_projeto/<int:projeto_id>/', views.interessar_no_projeto, name='interessar_no_projeto'),
    path('retirar_interesse_projeto/<int:projeto_id>/', views.retirar_interessar_no_projeto, name='retirar_interesse_no_projeto'),
    path('editar_perfil/', views.editar_perfil_aluno, name='editar_perfil_aluno'),
    path('visualizar_perfil/<str:matricula>/', views.visualizar_perfil_aluno, name='visualizar_perfil_aluno'),
    path('<str:matricula>/', views.get_by_matricula_aluno, name='get_by_matricula_aluno'),
    path('', views.get_all_alunos, name='get_all_alunos'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
