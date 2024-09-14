from django.contrib.auth.models import User
from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import *
from api_professor.serializers import ProfessorSerializer
from api_professor.models import Professor
from api_aluno.models import Aluno
from api_aluno.serializers import AlunoInformacoesSerializer
from rest_framework import status

from .serializers import *


@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    senha = request.data.get('senha')

    if not email or not senha:
        return Response({"detail": "Email e senha são obrigatórios."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        usuario = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"detail": "Professor não encontrado."}, status=status.HTTP_404_NOT_FOUND)

    if not usuario.check_password(senha):
        return Response({"detail": "Senha incorreta."}, status=status.HTTP_401_UNAUTHORIZED)

    response = {}
    isTeacher = True
    try:
        professor = Professor.objects.get(user=usuario)
        response = ProfessorSerializer(professor).data
    except Professor.DoesNotExist:
        try:
            aluno = Aluno.objects.get(user=usuario)
            isTeacher = False
            response = AlunoInformacoesSerializer(aluno).data
        except Aluno.DoesNotExist:
            return Response({"detail": "Usuário não cadastrado"}, status=status.HTTP_400_BAD_REQUEST)
    
    refresh = RefreshToken.for_user(usuario)
    response['isTeacher'] = isTeacher
    response['refresh'] = str(refresh)
    response['access'] = str(refresh.access_token)

    return Response(response)

@api_view(['GET'])
def get_all_habilidades(request):
    if request.method == 'GET':
        habilidades = Habilidade.objects.all()
        serializer = HabilidadeSerializer(habilidades, many=True)
        return Response(serializer.data)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
def get_all_experiencias(request):
    if request.method == 'GET':
        experiencias = Experiencia.objects.all()
        serializer = ExperienciaSerializer(experiencias, many=True)
        return Response(serializer.data)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
def get_all_interesses(request):
    if request.method == 'GET':
        interesses = Interesse.objects.all()
        serializer = InteresseSerializer(interesses, many=True)
        return Response(serializer.data)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
def get_all_feedbacks(request):
    if request.method == 'GET':
        feedbacks = Feedback.objects.all()
        serializer = FeedbackSerializer(feedbacks, many=True)
        return Response(serializer.data)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
