from rest_framework import serializers

from .models import Professor, Aluno, Projeto


class ProfessorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professor
        fields = '__all__'

class ProfessorSemIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professor
        fields = ['nome', 'email', 'senha']

class AlunoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aluno
        fields = '__all__'

class ProjetoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projeto
        fields = '__all__'

class ProjetoSemIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projeto
        fields = ['nome', 'descricao', 'dono', 'data_de_criacao', 'vagas', 'responsavel']