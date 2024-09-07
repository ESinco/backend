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