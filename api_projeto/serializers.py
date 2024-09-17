from rest_framework import serializers

from .models import Projeto


class ProjetoSerializer(serializers.ModelSerializer):
    data_de_criacao = serializers.DateTimeField(format="%d/%m/%Y")
    
    class Meta:
        model = Projeto
        fields = '__all__'

class ProjetoSemIdSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Projeto
        fields = ['nome', 'descricao', 'laboratorio', 'data_de_criacao', 'vagas', 'responsavel']
        
class ProjetoInformacoesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projeto
        fields = ['nome', 'descricao', 'laboratorio', 'vagas']