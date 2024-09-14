from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from api_professor.models import Professor
from django.contrib.auth.models import User


class ProfessorModelTestCase(APITestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(
            username='andre@example.com',
            email='andre@example.com',
            password='1234'
        )
        self.professor = Professor.objects.create(
            nome='Andre Souza',
            email='andre@example.com',
            user=self.usuario
        )

    def test_professor_creation(self):
        self.assertIsInstance(self.professor, Professor)
        self.assertEqual(self.professor.nome, 'Andre Souza')
        self.assertEqual(self.professor.email, 'andre@example.com')
        self.assertEqual(self.professor.user.email, 'andre@example.com')
        self.assertEqual(self.professor.user.username, 'andre@example.com')
        self.assertTrue(self.professor.user.check_password('1234'))

    def test_professor_str(self):
        expected_str = 'nome: Andre Souza\nemail: andre@example.com'
        self.assertEqual(str(self.professor), expected_str)


class CriarProfessorViewTestCase(APITestCase):
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
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('nome', response.data)

    def test_criar_professor_com_email_vazio(self):
        invalid_data = {
            "nome": "Carmelita Braga",
            "email": '',
            "senha": "senha123"
        }
        response = self.client.post(self.url, invalid_data, format='json')
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
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_criar_professor_senha_vazia(self):
        invalid_data = {
            "nome": "Gabriel Souza",
            "email": "gabriel.souza@email.com",
            "senha": ''
        }
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('senha', response.data)

    def test_criar_professor_vazio(self):
        invalid_data = {
            "nome": "",
            "email": '',
            "senha": ''
        }
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class GetAllProfessorViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('get_all_professores')

        usuarios = [
            {"username": 'andrey@example.com', "email": 'andrey@example.com', "password": '213'},
            {"username": 'fabio@example.com', "email": 'fabio@example.com', "password": '123'},
            {"username": 'wilkerson@example.com', "email": 'wilkerson@example.com', "password": '321'}
        ]
        for dados_usuario in usuarios:
            user = User.objects.create_user(**dados_usuario)
            Professor.objects.create(nome=dados_usuario['username'].split('@')[0].title(), email=dados_usuario['email'], user=user)

    def test_get_all_professores_sucesso(self):
        response = self.client.get(self.url, format='json')
        nomes_professores = [prof['nome'] for prof in response.data]
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertIn("Andrey", nomes_professores)
        self.assertIn("Fabio", nomes_professores)
        self.assertIn("Wilkerson", nomes_professores)

    def test_get_all_professores_vazio(self):
        Professor.objects.all().delete()
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


class GetProfessorPorIdTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

        user1 = User.objects.create_user(username='andrey@example.com', email='andrey@example.com', password='213')
        self.professor1 = Professor.objects.create(nome="Andrey", email="andrey@example.com", user=user1)

        user2 = User.objects.create_user(username='fabio@example.com', email='fabio@example.com', password='123')
        self.professor2 = Professor.objects.create(nome="Fabio", email="fabio@example.com", user=user2)

        user3 = User.objects.create_user(username='wilkerson@example.com', email='wilkerson@example.com', password='321')
        self.professor3 = Professor.objects.create(nome="Wilkerson", email="wilkerson@example.com", user=user3)

    def test_get_professor_by_id_sucesso(self):
        url = reverse('get_by_id_professor', kwargs={'id_professor': self.professor1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome'], self.professor1.nome)
        self.assertEqual(response.data['email'], self.professor1.email)

    def test_get_professor_by_id_inexistente(self):
        url = reverse('get_by_id_professor', kwargs={'id_professor': 999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class LoginProfessorViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('login_professor')
        self.usuario = User.objects.create_user(
            username='andre@example.com',
            email='andre@example.com',
            password='1234'
        )
        self.professor = Professor.objects.create(
            nome='Andre Souza',
            email='andre@example.com',
            user=self.usuario
        )
        self.login_data = {
            "email": "andre@example.com",
            "senha": "1234"
        }

    def test_login_professor_sucesso(self):
        response = self.client.post(self.url, self.login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)
        self.assertNotEqual(response.data['refresh'], '')
        self.assertNotEqual(response.data['access'], '')

    def test_login_professor_com_email_vazio(self):
        invalid_data = {
            "email": "",
            "senha": "1234"
        }
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Professor não encontrado.')

    def test_login_professor_com_senha_vazia(self):
        invalid_data = {
            "email": "andre@example.com",
            "senha": ""
        }
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Senha incorreta.')

    def test_login_professor_inexistente(self):
        invalid_data = {
            "email": "joao.silva@example.com",
            "senha": "senha123"
        }
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Professor não encontrado.')

    def test_login_professor_senha_incorreta(self):
        invalid_data = {
            "email": "andre@example.com",
            "senha": "12345"
        }
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
        self.assertEqual(response.data['detail'], 'Senha incorreta.')
