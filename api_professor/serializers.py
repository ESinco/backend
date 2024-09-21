from django.forms import ValidationError
from rest_framework import serializers
from .models import Professor
from api_aluno.models import Avaliacao
from django.contrib.auth.models import User
from api_rest.models import Feedback
from api_rest.serializers import FeedbackSerializer

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
    tags = FeedbackSerializer(many=True)
    
    class Meta:
        model = Avaliacao
        fields = '__all__'
        
class AvaliacaoSemIdSerializer(serializers.ModelSerializer):   
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Feedback.objects.all(),
        required=False
    )
    
    comentario = serializers.CharField(
        max_length=280,
        min_length=0,
        required=False,
        allow_blank=True
    )
    
    class Meta:
        model = Avaliacao
        fields = ['id_professor', 'id_aluno', 'comentario', 'tags']
        
class AvaliacaoInformacoesSerializer(serializers.ModelSerializer):   
    tags = FeedbackSerializer(many=True)
    
    comentario = serializers.CharField(
        max_length=280,
        min_length=0,
        required=False,
        allow_blank=True
    )
    
    class Meta:
        model = Avaliacao
        fields = ['id_avaliacao', 'id_professor', 'id_aluno', 'comentario', 'tags']
        
class AvaliacaoPostSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False
    )
    
    comentario = serializers.CharField(
        max_length=280,
        min_length=0,
        required=False,
        allow_blank=True
    )
    
    class Meta:
        model = Avaliacao
        fields = ['comentario', 'tags']
        
    def validate(self, data):
        comentario = data.get('comentario')
        tags = data.get('tags')
        
        if not comentario and not tags:
            raise ValidationError("Pelo menos um dos campos 'comentario' ou 'tags' deve ser fornecido.")
        
        return data
    