from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Aluno, Disciplina, HistoricoAcademico

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

class AlunoPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aluno
        fields = ['matricula', 'nome', 'email', 'curriculo', 'github', 'linkedin', 'cra']

    def update(self, instance, validated_data):
        instance.nome = validated_data.get('nome', instance.nome)
        instance.email = validated_data.get('email', instance.email)
        instance.curriculo = validated_data.get('curriculo', instance.curriculo)
        instance.github = validated_data.get('github', instance.github)
        instance.linkedin = validated_data.get('linkedin', instance.linkedin)
        instance.cra = validated_data.get('cra', instance.cra)
        instance.save()
        return instance
            
class AlunoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aluno
        fields = ['matricula', 'nome', 'email', 'curriculo', 'github', 'linkedin', 'cra']

class AlunoLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aluno
        fields = ['matricula', 'nome', 'email']

class DisciplinaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disciplina
        fields = '__all__'

class HistoricoAcademicoSerializer(serializers.ModelSerializer):
    disciplinas = DisciplinaSerializer(many=True, read_only=True)

    class Meta:
        model = HistoricoAcademico
        fields = ['id', 'aluno', 'cra', 'disciplinas']