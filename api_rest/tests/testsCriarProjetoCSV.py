from rest_framework.test import APITestCase
from rest_framework import status

from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from api_rest.models import Professor, Aluno, Projeto, Associacao

from io import StringIO

import os


class CriarProjetoCSVTests(APITestCase):

    def setUp(self):
        # Criar usuário e professor autenticado
        self.user = User.objects.create_user(username='professor@teste.com', password='senha123')
        self.professor = Professor.objects.create(user=self.user, nome='Professor Teste', email='professor@teste.com')
        
        # Criar alunos
        self.aluno1 = Aluno.objects.create(user=User.objects.create_user(username='aluno1@teste.com', password='senha123'),
                                           matricula='123456789', nome='Aluno 1', email='aluno1@teste.com')
        self.aluno2 = Aluno.objects.create(user=User.objects.create_user(username='aluno2@teste.com', password='senha123'),
                                           matricula='987654321', nome='Aluno 2', email='aluno2@teste.com')
        
        self.url = reverse('criar_projeto_csv')
        self.client.force_authenticate(user=self.user)  # Autenticar como o professor

    def test_criar_projeto_csv_sucesso(self):
        # Caminho para o arquivo CSV
        file_path = os.path.join(os.path.dirname(__file__), 'test_data/testeProjetoCSV.csv')
        
        # Abrir o arquivo e criar o SimpleUploadedFile
        with open(file_path, 'rb') as f:
            csv_file = SimpleUploadedFile("alunos.csv", f.read(), content_type="text/csv")
        
        # Fazer a requisição POST simulando o upload do CSV
        url = reverse('criar_projeto_csv')
        response = self.client.post(url, {'file': csv_file}, format='multipart')
        
        # Asserts
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Projeto.objects.count(), 1)
        self.assertEqual(Associacao.objects.count(), 2)

    def test_arquivo_nao_enviado(self):
        response = self.client.post(self.url, {}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Arquivo não encontrado.')

    def test_arquivo_nao_csv(self):
        # Simular arquivo não CSV
        file_data = "Conteúdo de um arquivo de texto"
        file = StringIO(file_data)
        file.name = 'arquivo.txt'

        response = self.client.post(self.url, {'file': file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'O arquivo não é CSV.')

    def test_matricula_invalida_no_csv(self):
        file_path = os.path.join(os.path.dirname(__file__), './test_data/testeMatriculaInexistente.csv')
        
        with open(file_path, 'rb') as f:
            csv_file = SimpleUploadedFile("alunos.csv", f.read(), content_type="text/csv")
            
        url = reverse('criar_projeto_csv')
        response = self.client.post(url, {'file': csv_file}, format='multipart')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Projeto.objects.count(), 1)
        self.assertEqual(Associacao.objects.count(), 1)
        
    def test_csv_vazio(self):
        file_path = os.path.join(os.path.dirname(__file__), './test_data/testeVazio.csv')
        
        with open(file_path, 'rb') as f:
            csv_file = SimpleUploadedFile("alunos.csv", f.read(), content_type="text/csv")
            
        url = reverse('criar_projeto_csv')
        response = self.client.post(url, {'file': csv_file}, format='multipart')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

