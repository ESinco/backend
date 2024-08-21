from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse

from api_rest.views import *
from api_rest.models import Professor

#Models
# Testando model de professor.
class ProfessorModelTest(TestCase):

    def setUp(self):
        self.professor = Professor.objects.create(
            nome='Andre Souza',
            email='andre@example.com',
            senha= '1234'
        )

    def test_professor_creation(self):
        #Asserts
        self.assertIsInstance(self.professor, Professor)
        self.assertEqual(self.professor.nome, 'Andre Souza')
        self.assertEqual(self.professor.email, 'andre@example.com')

    def test_professor_str(self):
        expected_str = ('nome: Andre Souza\n'
                        'email: andre@example.com\n'
                        'senha: 1234')
        
        #Asserts
        self.assertEqual(str(self.professor), expected_str)

#Views
# Testando POST de professores
class CriarProfessorViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('criar_professor')
        self.professor_data = {
            "nome": "João da Silva",
            "email": "joao.silva@example.com",
            "senha": "senha123"
        }

    def test_criar_professor_sucesso(self):
        response = self.client.post(self.url, self.professor_data, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['nome'], self.professor_data['nome'])
        self.assertEqual(response.data['email'], self.professor_data['email'])

    def test_criar_professor_com_nome_vazio(self):
        invalid_data = {
            "nome": "",
            "email": "vazio@example.com",
            "senha": "senha123"
        }
        response = self.client.post(self.url, invalid_data, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('nome', response.data)


    def test_criar_professor_com_email_vazio(self):
        invalid_data = {
            "nome": "Carmelita Braga",
            "email": '',
            "senha": "senha123"
        }
        response = self.client.post(self.url, invalid_data, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_criar_professor_com_email_repetido(self):
        self.client.post(self.url, self.professor_data, format='json')
        invalid_data = {
            "nome": "Carmelita Braga",
            "email": 'joao.silva@example.com',
            "senha": "senha123"
        }
        response = self.client.post(self.url, invalid_data, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_criar_professor_senha_vazia(self):
        invalid_data= {
            "nome": "Gabriel Souza",
            "email": "gabriel.souza@email.com",
            "senha": ''
        }
        response= self.client.post(self.url, invalid_data, format='json')
        
        #Asserts
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.assertIn('senha', response.data)

    def test_criar_professor_vazio(self):
        invalid_data= {
            "nome": "",
            "email": '',
            "senha": ''
        }
        response= self.client.post(self.url, invalid_data, format='json')
        
        #Asserts
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)

# Testando GET de todos os professores.
class getAllProfessorViewTest(APITestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('get_all_professores')
        
        Professor.objects.create(nome="Andrey", email="andrey@example.com", senha="213")
        Professor.objects.create(nome="Fabio", email="fabio@example.com", senha="123")
        Professor.objects.create(nome="Wilkerson", email="wilkerson@example.com", senha="321")
    
    def test_get_all_professores_sucesso(self):
        response = self.client.get(self.url, format='json')
        nomes_professores = [prof['nome'] for prof in response.data]
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertIn("Andrey", nomes_professores)
        self.assertIn("Fabio", nomes_professores)
        self.assertIn("Wilkerson", nomes_professores)
        
    def test_get_all_professores_vazio(self):
        Professor.objects.all().delete()
        
        response = self.client.get(self.url, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


# Testando GET de pegar professor por ID.
class getProfessorPorIdTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        
        self.professor1 = Professor.objects.create(nome="Andrey", email="andrey@example.com", senha="213")
        self.professor2 = Professor.objects.create(nome="Fabio", email="fabio@example.com", senha="123")
        self.professor3 = Professor.objects.create(nome="Wilkerson", email="wilkerson@example.com", senha="321")

    def test_get_professor_by_id_sucesso(self):
        url = reverse('get_by_id_professor', kwargs={'id_professor': self.professor1.id_professor})
        response = self.client.get(url)
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome'], self.professor1.nome)
        self.assertEqual(response.data['email'], self.professor1.email)

    def test_get_professor_by_id_inexistente(self):
        url = reverse('get_by_id_professor', kwargs={'id_professor': 999})
        response = self.client.get(url)
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)