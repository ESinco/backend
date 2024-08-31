from django.db import models

class Professor(models.Model):
    id_professor = models.AutoField(primary_key=True)
    nome = models.TextField(null=False)
    email = models.TextField(null=False, unique=True)
    senha = models.TextField(null=False)

    def __str__(self):
        return (f'nome: {self.nome}\n'
                f'email: {self.email}\n'
                f'senha: {self.senha}')

class Aluno(models.Model):
    matricula = models.CharField(max_length=9, primary_key=True)
    nome = models.TextField()
    email = models.TextField(unique=True)
    curriculo = models.TextField(null=True)
    github = models.TextField(null=True)
    linkedin = models.TextField(null=True)
    cra = models.FloatField(null=True)
    senha = models.TextField()

    def __str__(self):
        return (f'matricula: {self.matricula}\n'
                f'nome: {self.nome}\n'
                f'email: {self.email}\n'
                f'curriculo: {self.curriculo}'
                f'github: {self.github}'
                f'linkedin: {self.linkedin}'
                f'cra: {self.cra}'
                f'senha: {self.senha}')

class Projeto(models.Model):
    id_projeto = models.AutoField(primary_key=True)
    nome = models.TextField()
    descricao = models.TextField()
    laboratorio = models.TextField()
    data_de_criacao = models.BigIntegerField()
    vagas = models.IntegerField()
    responsavel = models.ForeignKey(Professor, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return (f'nome: {self.nome}\n'
                f'descrição: {self.descricao}\n'
                f'laboratório: {self.laboratorio}\n'
                f'data de criação: {self.data_de_criacao}\n'
                f'vagas: {self.vagas}\n'
                f'responsavel: {self.responsavel}')

class Tags(models.Model):
    nome = models.TextField()
    grupo = models.TextField()

    def __str__(self):
        return f'{self.grupo}: {self.nome}'

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

class HistoricoAcademico(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    historico_pdf = models.FileField(upload_to='historicos/')
    cra = models.FloatField(null=True, blank=True)
    # Não é necessário adicionar ManyToMany aqui; apenas use a relação inversa a partir de Disciplina

    def __str__(self):
        return f"Histórico de {self.aluno.nome}"