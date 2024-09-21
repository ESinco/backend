from django.contrib import admin
from .models import Aluno, Historico_Academico, Avaliacao


admin.site.register(Aluno)
admin.site.register(Historico_Academico)
admin.site.register(Avaliacao)