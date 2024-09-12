from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *


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
