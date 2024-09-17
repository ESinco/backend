from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from api_professor.models import Professor
from .models import Habilidade, Experiencia, Interesse, Feedback
from .views import *


class LoginTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        usuario_professor = User.objects.create_user(
            username='andre@example.com',
            email='andre@example.com',
            password='1234'
        )
        self.professor = Professor.objects.create(
            nome='Andre Souza',
            email='andre@example.com',
            user=usuario_professor
        )
        self.login_professor = {
            "email" : "andre@example.com",
            "senha" : "1234"
        }

        usuario_aluno = User.objects.create_user(
            username='andre1@example.com',
            email='andre1@example.com',
            password='1234'
        )
        self.aluno = Aluno.objects.create(
            matricula='121210210',
            nome='Andre Souza',
            email='andre1@example.com',
            user=usuario_aluno
        )
        self.login_aluno = {
            "email" : "andre1@example.com",
            "senha" : "1234"
        }
        
        self.url = reverse('login')

    def test_login_professor_sucesso(self):
        response = self.client.post(self.url, self.login_professor, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)
        self.assertNotEqual(response.data['refresh'], '')
        self.assertNotEqual(response.data['access'], '')
        
    def test_login_com_email_vazio(self):
        invalid_data = {
            "email": "",
            "senha": "1234"
        }
        response = self.client.post(self.url, invalid_data, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Email e senha são obrigatórios.')

    def test_login_com_senha_vazia(self):
        invalid_data = {
            "email": "andre@example.com",
            "senha": ""
        }
        response = self.client.post(self.url, invalid_data, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Email e senha são obrigatórios.')

        
    def test_login_inexistente(self):
        invalid_data = {
            "email": "joao.silva@example.com",
            "senha": "senha123"
        }
        response = self.client.post(self.url, invalid_data, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Usuário não encontrado.')
        
    def test_login_professor_senha_incorreta(self):
        invalid_data = {
            "email": "andre@example.com",
            "senha": "12345"
        }
        response = self.client.post(self.url, invalid_data, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Senha incorreta.')


    def test_login_aluno_sucesso(self):
        response = self.client.post(self.url, self.login_aluno, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)
        self.assertNotEqual(response.data['refresh'], '')
        self.assertNotEqual(response.data['access'], '')
        
    def test_login_aluno_senha_incorreta(self):
        invalid_data = {
            "email": "andre@example.com",
            "senha": "12345"
        }
        response = self.client.post(self.url, invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Senha incorreta.')


class TagTestCase(APITestCase):
    def setUp(self):
        Habilidade.objects.create(nome='Programação', grupo='Hard Skills')
        Experiencia.objects.create(nome='Gestão de Projetos', grupo='Experiências')
        Interesse.objects.create(nome='Inteligência Artificial', grupo='Interesses')
        Feedback.objects.create(nome='Boa Comunicação', grupo='Feedbacks')

    def test_get_habilidades(self):
        url = reverse('get_all_habilidades')
        response = self.client.get(url)
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nome'], 'Programação')
        self.assertEqual(response.data[0]['grupo'], 'Hard Skills')

    def test_get_experiencias(self):
        url = reverse('get_all_experiencias')
        response = self.client.get(url)
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nome'], 'Gestão de Projetos')
        self.assertEqual(response.data[0]['grupo'], 'Experiências')

    def test_get_interesses(self):
        url = reverse('get_all_interesses')
        response = self.client.get(url)
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nome'], 'Inteligência Artificial')
        self.assertEqual(response.data[0]['grupo'], 'Interesses')

    def test_get_feedbacks(self):
        url = reverse('get_all_feedbacks')
        response = self.client.get(url)
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nome'], 'Boa Comunicação')
        self.assertEqual(response.data[0]['grupo'], 'Feedbacks')