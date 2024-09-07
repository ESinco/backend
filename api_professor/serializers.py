from rest_framework import serializers

from .models import Professor

from django.contrib.auth.models import User


class ProfessorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professor
        fields = ['id', 'nome', 'email']
        
class ProfessorPostSerializer(serializers.ModelSerializer):
    senha = serializers.CharField(write_only=True)

    class Meta:
        model = Professor
        fields = ['nome', 'email', 'senha']

    def create(self, validated_data):
        senha = validated_data.pop('senha')
        usuario = User.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=senha
        )
        professor = Professor.objects.create(user=usuario, **validated_data)
        return professor