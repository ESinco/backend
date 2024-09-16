from django.http import JsonResponse
from django.contrib.auth.models import User
from django.utils import timezone

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.http import FileResponse
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
import os

from .utils import extrair_disciplinas_do_pdf
from api_rest.utils import atualizar_disciplinas
from .models import *
from .serializers import *
from api_projeto.models import Projeto, Associacao


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
def upload_historico(request):
    aluno_id = request.data.get('aluno')
    historico_pdf = request.FILES.get('historico_pdf')

    if not aluno_id or not historico_pdf or not historico_pdf.size:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    try:
        aluno = Aluno.objects.get(pk=aluno_id)
    except Aluno.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    try:
        historico_antigo = Historico_Academico.objects.filter(aluno=aluno).first()
        if historico_antigo:
            historico_antigo.delete()

        novo_historico = Historico_Academico.objects.create(
            aluno=aluno,
            historico_pdf=historico_pdf
        )
        
        atualizar_disciplinas()
        extrair_disciplinas_do_pdf(novo_historico)
        
        return Response(status=status.HTTP_200_OK)
    except Exception:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def visualizar_historico(request, matricula):
    try:
        aluno = Aluno.objects.get(pk=matricula)

        if request.user != aluno.user and not hasattr(request.user, 'professor'):
            return Response(status=status.HTTP_403_FORBIDDEN)

        try:
            historico = Historico_Academico.objects.get(aluno=aluno)
            if not historico.historico_pdf:
                return Response(status=status.HTTP_404_NOT_FOUND)

            pdf_path = historico.historico_pdf.path

            try:
                with open(pdf_path, 'rb') as pdf_file:
                    response = FileResponse(pdf_file, content_type='application/pdf')
                    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(pdf_path)}"'
                    return response
            except FileNotFoundError:
                return Response(status=status.HTTP_404_NOT_FOUND)
                
        except Historico_Academico.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    except Aluno.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Exception:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def interessar_no_projeto(request, projeto_id):
    try:
        aluno_autenticado = Aluno.objects.get(user=request.user)
    except Aluno.DoesNotExist:
        return Response({"detail": "Acesso negado. Apenas alunos podem se associar a projetos."}, status=status.HTTP_403_FORBIDDEN)

    try:
        Projeto.objects.get(id_projeto=projeto_id)
    except Projeto.DoesNotExist:
        return Response({"detail": "Projeto não encontrado."}, status=status.HTTP_404_NOT_FOUND)

    associacao, criado = Associacao.objects.get_or_create(aluno_id=aluno_autenticado.matricula, projeto_id=projeto_id)

    if criado:
        return Response({"detail": "Associação criada com sucesso."}, status=status.HTTP_201_CREATED)
    else:
        return Response({"detail": "Aluno já está associado a este projeto."}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def retirar_interessar_no_projeto(request, projeto_id):
    try:
        aluno_autenticado = Aluno.objects.get(user=request.user)
    except Aluno.DoesNotExist:
        return Response({"detail": "Acesso negado. Apenas alunos podem se associar a projetos."}, status=status.HTTP_403_FORBIDDEN)

    try:
        Projeto.objects.get(id_projeto=projeto_id)
    except Projeto.DoesNotExist:
        return Response({"detail": "Projeto não encontrado."}, status=status.HTTP_404_NOT_FOUND)

    try:
        associacao = Associacao.objects.get(aluno_id=aluno_autenticado.matricula, projeto_id=projeto_id)
        associacao.delete()
        return Response({"detail": "Associação deletada com sucesso."}, status=status.HTTP_200_OK)
    except:
        return Response({"detail": "Aluno não está associado a este projeto."}, status=status.HTTP_400_BAD_REQUEST)
