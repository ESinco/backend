
from django.contrib.auth.models import User

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import *
from api_professor.serializers import ProfessorSerializer
from api_professor.models import Professor
from api_aluno.models import Aluno
from api_aluno.serializers import AlunoLoginSerializer
from rest_framework import status

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
    if Professor.objects.exists(user=usuario):
        professor = Professor.objects.get(user=usuario)
        response = ProfessorSerializer(professor).data
    elif Aluno.objects.exists(user=usuario):
        isTeacher = False
        aluno = Aluno.objects.get(user=usuario)
        response = AlunoLoginSerializer(aluno).data
    else:
        return Response({"detail": "Usuário não cadastrado"}, status=status.HTTP_400_BAD_REQUEST)
    
    refresh = RefreshToken.for_user(usuario)
    response['refresh'] = str(refresh)
    response['access'] = str(refresh.access_token)
    response['isTeacher'] = isTeacher

    return Response(response)