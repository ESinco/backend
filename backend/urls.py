from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('token/atualizar/', TokenRefreshView.as_view(), name='token_refresh'),
    path('professor/', include('api_professor.urls'), name='api_professor_urls'),
    path('aluno/', include('api_aluno.urls'), name='api_aluno_urls'),
    path('projeto/', include('api_projeto.urls'), name='api_projeto_urls'),
    path('', include('api_rest.urls'), name='api_rest_urls')
]
