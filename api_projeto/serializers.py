from rest_framework import serializers

from .models import Projeto, Lista_Filtragem, Associacao, Colaborador
from api_rest.models import Habilidade, Experiencia, Interesse
from api_professor.serializers import ProfessorSerializer
from api_aluno.serializers import AlunoInformacoesSerializer, AlunoDadosSerializer
from api_rest.serializers import HabilidadeSerializer, ExperienciaSerializer, FeedbackSerializer, InteresseSerializer

class ProjetoSemIdSerializer(serializers.ModelSerializer):
    habilidades = serializers.PrimaryKeyRelatedField(many=True, queryset=Habilidade.objects.all(), required=False)
    
    class Meta:
        model = Projeto
        fields = ['nome', 'descricao', 'laboratorio', 'data_de_criacao', 'vagas', 'responsavel', 'habilidades']
        
class ProjetoInformacoesSerializer(serializers.ModelSerializer):
    habilidades = serializers.PrimaryKeyRelatedField(many=True, queryset=Habilidade.objects.all(), required=False)

    class Meta:
        model = Projeto
        fields = ['nome', 'descricao', 'laboratorio', 'vagas', 'habilidades']

class ListaFiltragemPostSerializer(serializers.ModelSerializer):
    filtro_habilidades = serializers.PrimaryKeyRelatedField(many=True, queryset=Habilidade.objects.all(), required=False)
    filtro_experiencias = serializers.PrimaryKeyRelatedField(many=True, queryset=Experiencia.objects.all(), required=False)
    filtro_interesses = serializers.PrimaryKeyRelatedField(many=True, queryset=Interesse.objects.all(), required=False)
    filtro_disciplinas = serializers.JSONField(required=False)
    filtro_cra = serializers.FloatField(required=False)

    class Meta:
        model = Lista_Filtragem
        fields = ['id_projeto', 'titulo', 'filtro_habilidades', 'filtro_experiencias', 'filtro_interesses', 'filtro_cra', 'filtro_disciplinas']
    
    def validate_filtro_disciplinas(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("O campo 'filtro_disciplinas' deve ser uma lista de objetos.")
        
        for item in value:
            if not isinstance(item, dict):
                raise serializers.ValidationError("Cada item de 'filtro_disciplinas' deve ser um JSON.")
            if "disciplina" not in item or "nota" not in item:
                raise serializers.ValidationError("Cada item deve ter as chaves 'disciplina' e 'nota'.")
            if not isinstance(item["disciplina"], str):
                raise serializers.ValidationError("'disciplina' deve ser uma string.")
            if not isinstance(item["nota"], (int, float)):
                raise serializers.ValidationError("'nota' deve ser um número.")
            if item["nota"] < 0 or item["nota"] > 10:
                raise serializers.ValidationError("'nota' deve estar entre 0 e 10.")
        
        return value

class ListaFiltragemPutSerializer(serializers.ModelSerializer):
    filtro_habilidades = serializers.PrimaryKeyRelatedField(many=True, queryset=Habilidade.objects.all(), required=False)
    filtro_experiencias = serializers.PrimaryKeyRelatedField(many=True, queryset=Experiencia.objects.all(), required=False)
    filtro_interesses = serializers.PrimaryKeyRelatedField(many=True, queryset=Interesse.objects.all(), required=False)
    filtro_disciplinas = serializers.JSONField(required=False)
    filtro_cra = serializers.FloatField(required=False)

    class Meta:
        model = Lista_Filtragem
        fields = ['id_lista', 'titulo', 'filtro_habilidades', 'filtro_experiencias', 'filtro_interesses', 'filtro_cra', 'filtro_disciplinas']
    
    def validate_filtro_disciplinas(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("O campo 'filtro_disciplinas' deve ser uma lista de objetos.")
        
        for item in value:
            if not isinstance(item, dict):
                raise serializers.ValidationError("Cada item de 'filtro_disciplinas' deve ser um JSON.")
            if "disciplina" not in item or "nota" not in item:
                raise serializers.ValidationError("Cada item deve ter as chaves 'disciplina' e 'nota'.")
            if not isinstance(item["disciplina"], str):
                raise serializers.ValidationError("'disciplina' deve ser uma string.")
            if not isinstance(item["nota"], (int, float)):
                raise serializers.ValidationError("'nota' deve ser um número.")
            if item["nota"] < 0 or item["nota"] > 10:
                raise serializers.ValidationError("'nota' deve estar entre 0 e 10.")
        
        return value
    
class ListaFiltragemSemIdSerializer(serializers.ModelSerializer):
    filtro_habilidades = serializers.PrimaryKeyRelatedField(many=True, queryset=Habilidade.objects.all(), required=False)
    filtro_experiencias = serializers.PrimaryKeyRelatedField(many=True, queryset=Experiencia.objects.all(), required=False)
    filtro_interesses = serializers.PrimaryKeyRelatedField(many=True, queryset=Interesse.objects.all(), required=False)
    filtro_disciplinas = serializers.JSONField(required=False)
    filtro_cra = serializers.FloatField(required=False)

    class Meta:
        model = Lista_Filtragem
        fields = ['id_projeto', 'id_professor', 'titulo', 'filtro_habilidades', 'filtro_experiencias', 'filtro_interesses', 'filtro_cra', 'filtro_disciplinas']
        
class ListaFiltragemSerializer(serializers.ModelSerializer):
    filtro_habilidades = HabilidadeSerializer(many=True)
    filtro_experiencias = ExperienciaSerializer(many=True)
    filtro_interesses = InteresseSerializer(many=True)
    filtro_disciplinas = serializers.JSONField(required=False)
    filtro_cra = serializers.FloatField(required=False)

    class Meta:
        model = Lista_Filtragem
        fields = '__all__'
        
class AssociacaoInfoSerializer(serializers.ModelSerializer):
    aluno = AlunoInformacoesSerializer()

    class Meta:
        model = Associacao
        fields = ['id_associacao', 'aluno', 'status']

class AssociacaoCompletaSerializer(serializers.ModelSerializer):
    aluno = AlunoDadosSerializer()

    class Meta:
        model = Associacao
        fields = ['id_associacao', 'aluno', 'status']
        
class ListaFiltragemInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lista_Filtragem
        fields = ['id_lista', 'titulo']
        
class RecomendacaoSerializer(serializers.ModelSerializer):
    habilidades_em_comum = serializers.IntegerField(read_only=True)

    class Meta:
        model = Projeto
        fields = ['nome', 'responsavel', 'habilidades', 'data_de_criacao', 'habilidades_em_comum']
        
class ColaboradorSerializer(serializers.ModelSerializer):
    professor = ProfessorSerializer()
    
    class Meta:
        model = Colaborador
        fields = ['id', 'professor']
        
class ProjetoSerializer(serializers.ModelSerializer):
    data_de_criacao = serializers.DateTimeField(format="%d/%m/%Y")
    habilidades = HabilidadeSerializer(many=True)
    responsavel = ProfessorSerializer()
    colaboradores = ColaboradorSerializer(many=True)
    
    class Meta:
        model = Projeto
        fields = ['id_projeto', 'nome', 'descricao', 'laboratorio', 'data_de_criacao', 'vagas', 'responsavel', 'habilidades', 'colaboradores']
