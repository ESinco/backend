from django.http import JsonResponse
from django.contrib.auth.models import User
from django.utils import timezone

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

from .models import *
from .serializers import *
from api_aluno.models import HistoricoAcademico, Disciplina
from api_aluno.serializers import AlunoInformacoesSerializer

from io import StringIO

import csv


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def criar_projeto(request):
    try:
        professor_autenticado = Professor.objects.get(user=request.user)
    except Professor.DoesNotExist:
        return Response({"detail": "Acesso negado. Apenas professores podem criar projetos."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'POST':
        serializer = ProjetoPostSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = request.data.copy()
        data['responsavel'] = professor_autenticado.id
        
        data['data_de_criacao'] = timezone.now()
        
        serializer = ProjetoSemIdSerializer(data=data)
        if serializer.is_valid():
            projeto = serializer.save()
            response_serializer = ProjetoSerializer(projeto)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def criar_projeto_csv(request):
    try:
        professor_autenticado = Professor.objects.get(user=request.user)
    except Professor.DoesNotExist:
        return Response({"detail": "Acesso negado. Apenas professores podem criar projetos."}, status=status.HTTP_403_FORBIDDEN)
    
    if 'file' not in request.data:
        return Response({'detail':'Arquivo não encontrado.'}, status=status.HTTP_400_BAD_REQUEST)
    
    csv_file = request.data['file']

    if not csv_file.name.endswith('.csv'):
        return Response({'detail':'O arquivo não é CSV.'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Simulação de leitura do arquivo CSV
        csv_content = csv_file.read().decode('utf-8')
        csv_io = StringIO(csv_content)
        csv_reader = csv.DictReader(csv_io)
        
        if len(csv_content.splitlines()) < 2:
            return Response({'detail': 'O arquivo CSV está vazio.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({'detail': f'Erro ao processar CSV: {str(e)}'}, status=500)
    
    projeto = Projeto.objects.create(
            nome="Projeto Novo",
            data_de_criacao=timezone.now(),
            responsavel=professor_autenticado
        )
    matricula_inexistente = []
        
    for linha in csv_reader:
        matricula = linha.get('Matricula')
        if matricula:
            try:
                aluno = Aluno.objects.get(pk=matricula)
                Associacao.objects.create(projeto_id=projeto.id_projeto, aluno_id=aluno.matricula, status=None)
            except Aluno.DoesNotExist:
                matricula_inexistente.append(matricula)
    
    return JsonResponse({'id_projeto': projeto.id_projeto,'matriculas_inexistente': matricula_inexistente}, status=201)  
   
@api_view(['GET'])
def get_projetos(request):
    if request.method == 'GET':
        projetos = Projeto.objects.all()
        serializer = ProjetoSerializer(projetos, many=True)
        return Response(serializer.data)

@api_view(['GET'])
def get_by_id_projeto(request, id_projeto):
    if request.method == 'GET':
        try:
            projeto = Projeto.objects.get(pk=id_projeto)
            serializer = ProjetoSerializer(projeto)
            return Response(serializer.data)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
def get_all_projetos_by_professor(request):
    if request.method == 'GET':
        try:
            responsavel_id = request.GET.get('responsavel')
            responsavel = Professor.objects.get(pk=responsavel_id)
        except:
            return Response({"detail": "O parâmetro 'responsavel' é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            projetos = Projeto.objects.filter(responsavel=responsavel)
            serializer = ProjetoSerializer(projetos, many=True)
            return Response(serializer.data)
        except Projeto.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_projetos_by_aluno(request):
    if request.method == 'GET':
        try:
            aluno_autenticado = Aluno.objects.get(user=request.user)
        except Aluno.DoesNotExist:
            return Response({"detail": "Acesso negado. Apenas alunos podem ver seus próprios projetos inscritos."},
                status=status.HTTP_403_FORBIDDEN)
        
        associacoes = Associacao.objects.filter(aluno=aluno_autenticado.matricula)
        projetos_com_status = []
        for associacao in associacoes:
            try:
                projeto = Projeto.objects.get(pk=associacao.projeto.id_projeto)
                projeto_dados = ProjetoSerializer(projeto).data
                projeto_dados['status'] = associacao.status
                projetos_com_status.append(projeto_dados)
            except Projeto.DoesNotExist:
                continue
        
        if not projetos_com_status:
            return Response({"detail": "Nenhum projeto encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(projetos_com_status, status=status.HTTP_200_OK)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def filtragem_disciplina(request):
    if request.method == 'POST':
        disciplina = request.data.get('disciplina')
        nota = request.data.get('nota')
        alunos = request.data.get('alunos')
        try:
            Professor.objects.get(user=request.user)
        except Professor.DoesNotExist:
            return Response({"detail": "Acesso negado. Apenas professores podem realizar filtragens."}, status=status.HTTP_403_FORBIDDEN)
      
        if not alunos or not disciplina:
            return Response({'detail': 'Não há parâmetros para filtrar.'}, status=status.HTTP_400_BAD_REQUEST)
        
        alunos_filtrados = []
        for aluno_id in alunos:
            try:
                aluno = Aluno.objects.get(pk=aluno_id)
            except Aluno.DoesNotExist:
                continue

            informacoesAluno = AlunoInformacoesSerializer(aluno).data
            historico = HistoricoAcademico.objects.filter(aluno=aluno).first()
            if not historico:
                continue
            
            disciplina_historico = Disciplina.objects.get(historico=historico, codigo=disciplina)
            if not disciplina_historico:
                continue
            
            if not nota == '':
                if disciplina_historico.media is None or disciplina_historico.media < float(nota):
                    continue
                
            alunos_filtrados.append(informacoesAluno)
            
        return Response(alunos_filtrados, status.HTTP_200_OK)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def filtragem_cra(request):
    if request.method == 'POST':
        alunos = request.data.get('alunos')
        cra = request.data.get('cra')
        try:
            Professor.objects.get(user=request.user)
        except Professor.DoesNotExist:
            return Response({"detail": "Acesso negado. Apenas professores podem realizar filtragens."}, status=status.HTTP_403_FORBIDDEN)
        
        if not alunos or not cra:
            return Response({'detail': 'Não há parâmetros para filtrar.'}, status=status.HTTP_400_BAD_REQUEST)
        
        alunos_filtrados = []
        for aluno_id in alunos:
            try:
                aluno = Aluno.objects.get(pk=aluno_id)
            except Aluno.DoesNotExist:
                continue

            informacoesAluno = AlunoInformacoesSerializer(aluno).data
            historico = HistoricoAcademico.objects.filter(aluno=aluno).first()
            if not historico:
                continue
            
            if not cra == '':
                if historico.cra is None or historico.cra < float(cra):
                    continue
                
            alunos_filtrados.append(informacoesAluno)
            
        return Response(alunos_filtrados, status.HTTP_200_OK)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def filtragem_habilidade(request):
    if request.method == 'POST':
        alunos = request.data.get('alunos')
        habilidade = request.data.get('habilidade')
        try:
            Professor.objects.get(user=request.user)
        except Professor.DoesNotExist:
            return Response({"detail": "Acesso negado. Apenas professores podem realizar filtragens."}, status=status.HTTP_403_FORBIDDEN)
        
        if not alunos or not habilidade:
            return Response({'detail': 'Não há parâmetros para filtrar.'}, status=status.HTTP_400_BAD_REQUEST)
        
        alunos_filtrados = []
        for aluno_id in alunos:
            try:
                aluno = Aluno.objects.get(pk=aluno_id)
            except Aluno.DoesNotExist:
                continue
            
            if aluno.habilidades.filter(nome=habilidade).exists():
                informacoesAluno = AlunoInformacoesSerializer(aluno).data
                informacoesAluno['habilidades'] = [habilidade.nome for habilidade in aluno.habilidades.all()]
                
                alunos_filtrados.append(informacoesAluno)
            
        return Response(alunos_filtrados, status.HTTP_200_OK)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def filtragem_experiencia(request):
    if request.method == 'POST':
        alunos = request.data.get('alunos')
        experiencia = request.data.get('experiencia')
        try:
            Professor.objects.get(user=request.user)
        except Professor.DoesNotExist:
            return Response({"detail": "Acesso negado. Apenas professores podem realizar filtragens."}, status=status.HTTP_403_FORBIDDEN)
        
        if not alunos or not experiencia:
            return Response({'detail': 'Não há parâmetros para filtrar.'}, status=status.HTTP_400_BAD_REQUEST)
        
        alunos_filtrados = []
        for aluno_id in alunos:
            try:
                aluno = Aluno.objects.get(pk=aluno_id)
            except Aluno.DoesNotExist:
                continue
            
            if aluno.experiencias.filter(nome=experiencia).exists():
                informacoesAluno = AlunoInformacoesSerializer(aluno).data
                informacoesAluno['experiencias'] = [experiencia.nome for experiencia in aluno.experiencias.all()]
                
                alunos_filtrados.append(informacoesAluno)
            
        return Response(alunos_filtrados, status.HTTP_200_OK)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def filtragem_interesse(request):
    if request.method == 'POST':
        alunos = request.data.get('alunos')
        interesse = request.data.get('interesse')
        try:
            Professor.objects.get(user=request.user)
        except Professor.DoesNotExist:
            return Response({"detail": "Acesso negado. Apenas professores podem realizar filtragens."}, status=status.HTTP_403_FORBIDDEN)
        
        if not alunos or not interesse:
            return Response({'detail': 'Não há parâmetros para filtrar.'}, status=status.HTTP_400_BAD_REQUEST)
        
        alunos_filtrados = []
        for aluno_id in alunos:
            try:
                aluno = Aluno.objects.get(pk=aluno_id)
            except Aluno.DoesNotExist:
                continue
            
            if aluno.interesses.filter(nome=interesse).exists():
                informacoesAluno = AlunoInformacoesSerializer(aluno).data
                informacoesAluno['interesses'] = [interesse.nome for interesse in aluno.interesses.all()]
                
                alunos_filtrados.append(informacoesAluno)
            
        return Response(alunos_filtrados, status.HTTP_200_OK)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)