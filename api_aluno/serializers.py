from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Aluno, Disciplina_Matriculada, Historico_Academico
from api_rest.models import *
from api_rest.serializers import *
from .models import *
from api_professor.serializers import AvaliacaoSemIdSerializer

from django.contrib.auth.models import User


class AlunoPostSerializer(serializers.ModelSerializer):
    senha = serializers.CharField(write_only=True)

    class Meta:
        model = Aluno
        fields = ['matricula', 'nome', 'email', 'curriculo', 'github', 'linkedin', 'senha']

    def create(self, validated_data):
        senha = validated_data.pop('senha')
        usuario = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=senha
        )
        aluno = Aluno.objects.create(user=usuario, **validated_data)
        return aluno

class AlunoPerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aluno
        fields = '__all__'

class AlunoPerfilProfessorSerializer(serializers.ModelSerializer):
    avaliacao = serializers.SerializerMethodField()

    class Meta:
        model = Aluno
        fields = ['matricula', 'nome', 'email', 'curriculo', 'github', 'linkedin', 'habilidades', 'experiencias', 'interesses', 'avaliacao']

    def get_avaliacao(self, obj):
        avaliacoes = Avaliacao.objects.filter(id_aluno=obj)
        return AvaliacaoSemIdSerializer(avaliacoes, many=True).data

class AlunoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aluno
        fields = ['matricula', 'nome', 'email', 'curriculo', 'github', 'linkedin']

class AlunoInformacoesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aluno
        fields = ['matricula', 'nome', 'email']
        
class DisciplinaMatriculadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disciplina_Matriculada
        fields = '__all__'

class DisciplinaMatriculadaNotasSerializer(serializers.ModelSerializer):
    disciplina = DisciplinaNomeSerializer()
    
    class Meta:
        model = Disciplina_Matriculada
        fields = ['id', 'disciplina', 'media']

class AlunoDadosSerializer(serializers.ModelSerializer):
    disciplinas_matriculadas = serializers.SerializerMethodField()
    cra = serializers.SerializerMethodField()

    class Meta:
        model = Aluno
        fields = ['matricula', 'nome', 'email', 'disciplinas_matriculadas', 'cra', 'habilidades', 'experiencias', 'interesses']

    def get_disciplinas_matriculadas(self, obj):
        historico = obj.historicos.first()
        if historico:
            return DisciplinaMatriculadaNotasSerializer(historico.disciplinas_matriculadas, many=True).data
        return []

    def get_cra(self, obj):
        historico = obj.historicos.first()
        if historico:
            return historico.cra
        return None