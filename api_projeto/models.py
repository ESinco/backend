from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from api_professor.models import Professor
from api_aluno.models import Aluno, Disciplina
from api_rest.models import Habilidade, Experiencia, Interesse


class Projeto(models.Model):
    id_projeto = models.AutoField(primary_key=True)
    nome = models.TextField()
    descricao = models.TextField(null=True)
    laboratorio = models.TextField(null=True)
    vagas = models.IntegerField(null=True)
    data_de_criacao = models.DateTimeField(default=timezone.now)
    responsavel = models.ForeignKey(Professor, null=False, on_delete=models.CASCADE)
    habilidades = models.ManyToManyField(Habilidade, related_name="habilidades_desejadas", blank=True)
    encerrado = models.BooleanField(default=False)

    def __str__(self):
        return (f'nome: {self.nome}\n'
                f'descrição: {self.descricao}\n'
                f'laboratório: {self.laboratorio}\n'
                f'data de criação: {self.data_de_criacao.strftime("%d/%m/%Y")}\n'
                f'vagas: {self.vagas}\n'
                f'responsavel: {self.responsavel}')


class Associacao(models.Model):
    id_associacao = models.AutoField(primary_key=True)
    projeto = models.ForeignKey(Projeto, null=False, on_delete=models.CASCADE)
    aluno = models.ForeignKey(Aluno, null=False, on_delete=models.CASCADE)
    status = models.BooleanField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['projeto', 'aluno'], name='unique_projeto_aluno')
        ]


class Lista_Filtragem(models.Model):
    id_lista = models.AutoField(primary_key=True)
    id_projeto = models.ForeignKey(Projeto, on_delete=models.CASCADE)
    id_professor = models.ForeignKey(Professor, null=False, on_delete=models.CASCADE)
    titulo = models.TextField(null=False)
    filtro_habilidades = models.ManyToManyField(Habilidade, related_name="filtros", blank=True)
    filtro_experiencias = models.ManyToManyField(Experiencia, related_name="filtros", blank=True)
    filtro_interesses = models.ManyToManyField(Interesse, related_name="filtros", blank=True)
    filtro_disciplinas = models.JSONField(blank=True)
    filtro_cra = models.FloatField(null=True)

    def clean(self):
        super().clean()
        self.validate_filtro_disciplinas()

    def validate_filtro_disciplinas(self):
        if self.filtro_disciplinas is None:
            raise ValidationError("O campo 'filtro_disciplinas' não pode ser None.")
        if not isinstance(self.filtro_disciplinas, list):
            raise ValidationError("O campo 'filtro_disciplinas' deve ser uma lista de objetos.")
        
        if self.filtro_disciplinas == []:
            return self.filtro_disciplinas

        for item in self.filtro_disciplinas:
            if not isinstance(item, dict):
                raise ValidationError("Cada item de 'filtro_disciplinas' deve ser um JSON.")
            if "codigo_da_disciplina" not in item or "nota" not in item:
                raise ValidationError("Cada item deve ter as chaves 'codigo_da_disciplina' e 'nota'.")
            if not isinstance(item["codigo_da_disciplina"], str):
                raise ValidationError("'codigo_da_disciplina' deve ser uma string.")
            if not isinstance(item["nota"], (int, float)):
                raise ValidationError("'nota' deve ser um número.")
            if item["nota"] < 0 or item["nota"] > 10:
                raise ValidationError("'nota' deve estar entre 0 e 10.")

        return self.filtro_disciplinas

    def clean(self):
        super().clean()
        if self.filtro_disciplinas is None:
            self.filtro_disciplinas = []
        elif not isinstance(self.filtro_disciplinas, list):
            raise ValidationError("O campo 'filtro_disciplinas' deve ser uma lista de objetos.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Colaborador(models.Model):
    id = models.AutoField(primary_key=True)
    professor = models.ForeignKey(Professor, null=False, on_delete=models.CASCADE)
    projeto = models.ForeignKey(Projeto, null=False, on_delete=models.CASCADE, related_name="colaboradores")
