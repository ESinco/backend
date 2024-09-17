from rest_framework import serializers

from .models import Projeto
from api_professor.serializers import ProfessorSerializer

class ProjetoSerializer(serializers.ModelSerializer):
    data_de_criacao = serializers.DateTimeField(format="%d/%m/%Y")
    responsavel = ProfessorSerializer()
    
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