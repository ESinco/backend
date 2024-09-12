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
from .models import *
from .serializers import *


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
        historico_antigo = HistoricoAcademico.objects.filter(aluno=aluno).first()
        if historico_antigo:
            historico_antigo.delete()

        novo_historico = HistoricoAcademico.objects.create(
            aluno=aluno,
            historico_pdf=historico_pdf
        )

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
            historico = HistoricoAcademico.objects.get(aluno=aluno)
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
                
        except HistoricoAcademico.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    except Aluno.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except Exception:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
