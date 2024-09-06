from django.contrib import admin
from .models import Professor, Aluno, Projeto, HistoricoAcademico

admin.site.register(Professor)
admin.site.register(Aluno)
admin.site.register(Projeto)
admin.site.register(HistoricoAcademico)
