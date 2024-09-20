from django.http import JsonResponse
from django.contrib.auth.models import User
from django.utils import timezone
from allauth.account.models import EmailAddress

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

from .models import *
from .serializers import *
from api_aluno.models import Aluno, Avaliacao


@api_view(['POST'])
def criar_professor(request):
    if request.method == 'POST':
        serializer = ProfessorPostSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
        
        professor = serializer.save()
        
        usuario = professor.user 
        email_address = EmailAddress.objects.create(
            user=usuario,
            email=usuario.email,
            verified=False,
            primary=True,
        )
        
        email_address.send_confirmation(request)
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
@permission_classes([IsAuthenticated])
def criar_avaliacao(request, id_aluno):
    try:
        professor_autenticado = Professor.objects.get(user=request.user)
    except Professor.DoesNotExist:
        return Response({"detail": "Acesso negado. Apenas professores podem criar avaliações."}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'POST':
        serializer = AvaliacaoPostSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            Aluno.objects.get(pk=id_aluno)
        except Professor.DoesNotExist:
            return Response({"detail": "Aluno não encontrado."}, status=404)

        data = request.data.copy()
        data['id_professor'] = professor_autenticado.id
        data['id_aluno'] = id_aluno
        
        serializer = AvaliacaoSemIdSerializer(data=data)
        if serializer.is_valid():
            avaliacao = serializer.save()
            response_serializer = AvaliacaoSerializer(avaliacao)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deletar_avaliacao(request, id_avaliacao):
    try:
        professor_autenticado = Professor.objects.get(user=request.user)
    except Professor.DoesNotExist:
        return Response({"detail": "Acesso negado. Apenas o dono da avaliação pode deletá-la."}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        avaliacao = Avaliacao.objects.get(pk=id_avaliacao)
    except Avaliacao.DoesNotExist:
        return Response({"detail": "Avaliação não encontrada."}, status=status.HTTP_404_NOT_FOUND)
    
    dados = AvaliacaoSerializer(avaliacao).data
    if dados['id_professor'] != professor_autenticado.id:
        return Response({"detail": "Você não tem permissão para deletar esta avaliação."}, status=status.HTTP_403_FORBIDDEN)
        
    avaliacao.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)