from django.db import models
from django.contrib.postgres.fields import ArrayField

class Habilidade(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.TextField(unique=True)
    grupo = models.TextField()

    def __str__(self):
        return f'{self.grupo}: {self.nome}'
    
class Experiencia(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.TextField(unique=True)
    grupo = models.TextField()

    def __str__(self):
        return f'{self.grupo}: {self.nome}'
    
class Interesse(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.TextField(unique=True)
    grupo = models.TextField()

    def __str__(self):
        return f'{self.grupo}: {self.nome}'
    
class Feedback(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.TextField(unique=True)
    grupo = models.TextField()

    def __str__(self):
        return f'{self.grupo}: {self.nome}'

class Disciplina(models.Model):
    codigo = models.PositiveIntegerField(primary_key=True)
    nome = models.TextField(null=False)
    disciplinas_equivalentes = ArrayField(models.PositiveIntegerField(), default=list)