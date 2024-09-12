from django.db import models


class Habilidade(models.Model):
    nome = models.TextField(primary_key=True)
    grupo = models.TextField()

    def __str__(self):
        return f'{self.grupo}: {self.nome}'
    
class Experiencia(models.Model):
    nome = models.TextField(primary_key=True)
    grupo = models.TextField()

    def __str__(self):
        return f'{self.grupo}: {self.nome}'
    
class Interesse(models.Model):
    nome = models.TextField(primary_key=True)
    grupo = models.TextField()

    def __str__(self):
        return f'{self.grupo}: {self.nome}'
    
class Feedback(models.Model):
    nome = models.TextField(primary_key=True)
    grupo = models.TextField()

    def __str__(self):
        return f'{self.grupo}: {self.nome}'