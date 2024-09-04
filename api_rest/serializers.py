from rest_framework import serializers

from django.contrib.auth.models import User
from .models import Professor, Aluno, Projeto


class ProfessorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professor
        fields = ['id', 'nome', 'email']
        
class ProfessorPostSerializer(serializers.ModelSerializer):
    senha = serializers.CharField(write_only=True)

    class Meta:
        model = Professor
        fields = ['nome', 'email', 'senha']

    def create(self, validated_data):
        senha = validated_data.pop('senha')
        usuario = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=senha
        )
        professor = Professor.objects.create(user=usuario, **validated_data)
        return professor
    
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
            
class AlunoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aluno
        fields = ['matricula', 'nome', 'email', 'curriculo', 'github', 'linkedin', 'cra']

class ProjetoSerializer(serializers.ModelSerializer):
    data_de_criacao = serializers.DateTimeField(format="%d/%m/%Y")
    
    class Meta:
        model = Projeto
        fields = '__all__'

class ProjetoSemIdSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Projeto
        fields = ['nome', 'descricao', 'laboratorio', 'data_de_criacao', 'vagas', 'responsavel']
        
class ProjetoPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projeto
        fields = ['nome', 'descricao', 'laboratorio', 'vagas']