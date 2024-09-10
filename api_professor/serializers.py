from rest_framework import serializers

from .models import Professor
from api_aluno.models import Avaliacao

from django.contrib.auth.models import User


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
    
class AvaliacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Avaliacao
        fields = '__all__'
        
class AvaliacaoSemIdSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False
    )
    
    class Meta:
        model = Avaliacao
        fields = ['id_professor', 'id_aluno', 'comentario', 'tags']
        
class AvaliacaoPostSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False
    )
    
    class Meta:
        model = Avaliacao
        fields = ['comentario', 'tags']