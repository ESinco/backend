from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Professor(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
    nome = models.TextField(null=False)
    email = models.TextField(null=False, unique=True)

    def __str__(self):
        return (f'nome: {self.nome}\n'
                f'email: {self.email}')

class Aluno(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
    matricula = models.CharField(max_length=9, primary_key=True)
    nome = models.TextField()
    email = models.TextField(unique=True)
    curriculo = models.TextField(null=True)
    github = models.TextField(null=True)
    linkedin = models.TextField(null=True)
    cra = models.FloatField(null=True)

    def __str__(self):
        return (f'matricula: {self.matricula}\n'
                f'nome: {self.nome}\n'
                f'email: {self.email}\n'
                f'curriculo: {self.curriculo}'
                f'github: {self.github}'
                f'linkedin: {self.linkedin}'
                f'cra: {self.cra}')
    
class Projeto(models.Model):
    id_projeto = models.AutoField(primary_key=True)
    nome = models.TextField()
    descricao = models.TextField()
    laboratorio = models.TextField()
    data_de_criacao = models.DateTimeField(default=timezone.now)
    vagas = models.IntegerField()
    responsavel = models.ForeignKey(Professor, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return (f'nome: {self.nome}\n'
                f'descrição: {self.descricao}\n'
                f'laboratório: {self.laboratorio}\n'
                f'data de criação: {self.data_de_criacao.strftime("%d/%m/%Y")}\n'
                f'vagas: {self.vagas}\n'
                f'responsavel: {self.responsavel}')
    
class Tags(models.Model):
    nome = models.TextField()
    grupo = models.TextField()

    def __str__(self):
        return f'{self.grupo}: {self.nome}'

