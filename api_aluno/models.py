from django.db import models
from django.contrib.auth.models import User
from api_professor.models import Professor


class Disciplina(models.Model):
    historico = models.ForeignKey('HistoricoAcademico', related_name='disciplinas', on_delete=models.CASCADE)
    codigo = models.CharField(max_length=20)
    nome = models.CharField(max_length=100)
    professor = models.CharField(max_length=300)
    tipo = models.CharField(max_length=50)
    creditos = models.IntegerField()
    carga_horaria = models.IntegerField()
    media = models.FloatField(null=True, blank=True)
    situacao = models.CharField(max_length=50)
    periodo = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.nome} - {self.media}"
    

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
    
class Aluno(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
    matricula = models.CharField(max_length=9, primary_key=True)
    nome = models.TextField()
    email = models.TextField(unique=True)
    curriculo = models.TextField(null=True)
    github = models.TextField(null=True)
    linkedin = models.TextField(null=True)
    cra = models.FloatField(null=True)
    habilidades = models.ManyToManyField(Habilidade, related_name="alunos")
    experiencias = models.ManyToManyField(Experiencia, related_name="alunos")
    interesses = models.ManyToManyField(Interesse, related_name="alunos")

    def __str__(self):
        return (f'matricula: {self.matricula}\n'
                f'nome: {self.nome}\n'
                f'email: {self.email}\n'
                f'curriculo: {self.curriculo}\n'
                f'github: {self.github}\n'
                f'linkedin: {self.linkedin}\n'
                f'cra: {self.cra}')
        
class HistoricoAcademico(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    cra = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Histórico de {self.aluno.nome}"
    
class Avaliacao(models.Model):
    id_avaliacao = models.AutoField(primary_key=True)
    id_professor = models.ForeignKey(Professor, null=False, on_delete=models.CASCADE)
    id_aluno = models.ForeignKey(Aluno, null=False, on_delete=models.CASCADE)
    comentario = models.CharField(max_length=280)
    tags = models.ManyToManyField(Feedback, related_name="avaliacoes")