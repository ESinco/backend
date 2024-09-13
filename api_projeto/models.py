from django.db import models
from django.utils import timezone
from api_professor.models import Professor  
from api_aluno.models import Aluno


class Projeto(models.Model):
    id_projeto = models.AutoField(primary_key=True)
    nome = models.TextField()
    descricao = models.TextField(null=True)
    laboratorio = models.TextField(null=True)
    vagas = models.IntegerField(null=True)
    data_de_criacao = models.DateTimeField(default=timezone.now)
    responsavel = models.ForeignKey(Professor, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return (f'nome: {self.nome}\n'
                f'descrição: {self.descricao}\n'
                f'laboratório: {self.laboratorio}\n'
                f'data de criação: {self.data_de_criacao.strftime("%d/%m/%Y")}\n'
                f'vagas: {self.vagas}\n'
                f'responsavel: {self.responsavel}')
        
class Associacao(models.Model):
    id_associacao = models.AutoField(primary_key=True)
    projeto = models.ForeignKey(Projeto, null= False, on_delete=models.CASCADE)
    aluno = models.ForeignKey(Aluno, null=False, on_delete=models.CASCADE)
    status = models.TextField(null=True)
    
class Colaborador(models.Model):
    id = models.AutoField(primary_key=True)
    professor = models.ForeignKey(Professor, null=False, on_delete=models.CASCADE)
    projeto = models.ForeignKey(Projeto, null=False, on_delete=models.CASCADE)
    