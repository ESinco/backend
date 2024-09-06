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

from io import StringIO

import csv

@api_view(['POST'])
def criar_professor(request):
    if request.method == 'POST':
        serializer = ProfessorPostSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
        
        professor = serializer.save()
        response_serializer = ProfessorSerializer(professor)
        
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
def get_professores(request):
    if request.method == 'GET':
        professores = Professor.objects.all()
        serializer = ProfessorSerializer(professores, many=True)
        return Response(serializer.data)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
def get_by_id_professor(request, id_professor):
    try:
        professor = Professor.objects.get(pk=id_professor)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProfessorSerializer(professor)
        return Response(serializer.data)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
def login_professor(request):
    email = request.data.get('email')
    senha = request.data.get('senha')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"detail": "Professor não encontrado."}, status=404)

    try:
        professor = Professor.objects.get(user=user)
    except Professor.DoesNotExist:
        return Response({"detail": "Professor não encontrado."}, status=404)

    if not user.check_password(senha):
        return Response({"detail": "Senha incorreta."}, status=401)

    refresh = RefreshToken.for_user(user)

    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    })

@api_view(['POST'])
def criar_aluno(request):
    if request.method == 'POST':
        serializer = AlunoPostSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
        
        aluno = serializer.save()
        response_serializer = AlunoSerializer(aluno)
        
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
def get_all_alunos(request):
    if request.method == 'GET':
        alunos = Aluno.objects.all()
        serializer = AlunoSerializer(alunos, many=True)
        return Response(serializer.data)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
def get_by_matricula_aluno(request, matricula):
    try:
        aluno = Aluno.objects.get(pk=matricula)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = AlunoSerializer(aluno)
        return Response(serializer.data)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
def login_aluno(request):
    email = request.data.get('email')
    senha = request.data.get('senha')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"detail": "Aluno não encontrado."}, status=404)

    try:
        aluno = Aluno.objects.get(user=user)
    except Aluno.DoesNotExist:
        return Response({"detail": "Aluno não encontrado."}, status=404)
    
    if not user.check_password(senha):
        return Response({"detail": "Senha incorreta."}, status=401)

    refresh = RefreshToken.for_user(user)

    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    })

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
                    Associacao.objects.create(projeto=projeto, aluno=aluno, status=None)
                except Aluno.DoesNotExist:
                    matricula_inexistente.append(matricula)
        
        return JsonResponse({'id_projeto': projeto.id_projeto,'matriculas_inexistente': matricula_inexistente}, status=201)
    
    except Exception as e:
        return JsonResponse({'detail': f'Erro ao processar CSV: {str(e)}'}, status=500)
       
   
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