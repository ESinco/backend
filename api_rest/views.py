from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Professor, Aluno
from .serializers import *

import json

@api_view(['POST'])
def criar_professor(request):
    if request.method == 'POST':
        novo_professor = request.data
        serializer = ProfessorSemIdSerializer(data=novo_professor)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
def criar_aluno(request):
    if request.method == 'POST':
        novo_aluno = request.data
        serializer = AlunoSerializer(data=novo_aluno)

        if serializer.is_valid():
            professor = serializer.save()
            response_serializer = ProfessorSerializer(professor)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
def criar_projeto(request):
    if request.method == 'POST':
        serializer = ProjetoSemIdSerializer(data=request.data)

        if serializer.is_valid():
            projeto = serializer.save()
            response_serializer = ProjetoSerializer(projeto)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

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
        responsavel = request.GET['responsavel']
        if responsavel is not None:
            try:
                projetos = Projeto.objects.filter(responsavel__id_professor=responsavel)
                serializer = ProjetoSerializer(projetos, many=True)
                return Response(serializer.data)
            except Projeto.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"detail": "O parâmetro 'responsavel' é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)