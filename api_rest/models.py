from django.db import models

class Professor(models.Model):
    id_professor = models.AutoField(primary_key=True)
    nome = models.TextField()
    email = models.TextField(unique=True)
    senha = models.TextField()

    def __str__(self):
        return (f'id_Professor: {self.id_professor}\n'
                f'nome: {self.nome}\n'
                f'email: {self.email}\n'
                f'senha: {self.senha}')

class Aluno(models.Model):
    matricula = models.CharField(max_length=9, primary_key=True)
    nome = models.TextField()
    email = models.TextField(unique=True)
    senha = models.TextField()

    def __str__(self):
        return (f'matricula: {self.matricula}\n'
                f'nome: {self.nome}\n'
                f'email: {self.email}\n'
                f'senha: {self.senha}')

class Projeto(models.Model):
    id_projeto = models.AutoField(primary_key=True)
    nome = models.TextField()
    descricao = models.TextField()

    def __str__(self):
        return (f'id_projeto: {self.id_projeto}\n'
                f'nome: {self.nome}\n'
                f'descrição: {self.descricao}')
    
class Tags(models.Model):
    nome = models.TextField()
    grupo = models.TextField()

    def __str__(self):
        return f'Habilidade: {self.nome}'

