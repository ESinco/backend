from django.contrib import admin
from .models import Aluno, HistoricoAcademico, Avaliacao


admin.site.register(Aluno)
admin.site.register(HistoricoAcademico)
admin.site.register(Avaliacao)