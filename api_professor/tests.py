from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from api_professor.models import Professor
from django.contrib.auth.models import User
from api_aluno.models import Feedback
from api_professor.views import *


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


class CriarAvaliacaoViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.usuario_professor = User.objects.create_user(
            username='fabio@example.com',
            email='fabio@example.com',
            password='1234'
        )
        self.professor = Professor.objects.create(nome="Fabio", email="fabio@example.com", user=self.usuario_professor)
        self.login = {
            "email" : "andre@example.com",
            "senha" : "1234"
        }
        self.usuario_aluno = User.objects.create_user(
            username='andre@example.com',
            email='andre@example.com',
            password='1234'
        )
        self.aluno = Aluno.objects.create(
            matricula='121210210',
            nome='Andre Souza',
            email='andre@example.com',
            user=self.usuario_aluno
        )

        self.tag_criativo = Feedback.objects.create(nome="Criativo", grupo="Feedbacks")
        self.tag_proativo = Feedback.objects.create(nome="Proativo", grupo="Feedbacks")
        
        self.avaliacao_data = {
            "comentario" : "Bom demais",
            "tags" : ["Criativo", "Proativo"]
        }
        
        
        self.url = reverse('criar_avaliacao', kwargs={'id_aluno': self.aluno.matricula})
        refresh = RefreshToken.for_user(self.usuario_professor)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_criar_avaliacao_sucesso(self):
        response = self.client.post(self.url, self.avaliacao_data, format='json')
        
        # Asserts
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(response.data['id_professor'], self.professor.id)
        self.assertEqual(response.data['id_aluno'], self.aluno.matricula)
        self.assertEqual(response.data['comentario'], self.avaliacao_data['comentario'])
        self.assertEqual(response.data['tags'][0], self.avaliacao_data['tags'][0])
        self.assertEqual(response.data['tags'][1], self.avaliacao_data['tags'][1])

    def test_criar_avaliacao_comentario_nulo(self):
        invalid_data = self.avaliacao_data.copy()
        invalid_data['comentario'] = None
        response = self.client.post(self.url, invalid_data, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['comentario'][0]), "Este campo não pode ser nulo.")

    def test_criar_avaliacao_comentario_e_tag_vazio(self):
        invalid_data = self.avaliacao_data.copy()
        invalid_data['comentario'] = ""
        invalid_data['tags'] = []
        response = self.client.post(self.url, invalid_data, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data['non_field_errors'][0]), "Pelo menos um dos campos 'comentario' ou 'tags' deve ser fornecido.")
  
    def test_criar_avaliacao_comentario_vazio(self):
        valid_data = self.avaliacao_data.copy()
        valid_data['comentario'] = ""
        response = self.client.post(self.url, valid_data, format='json')
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['id_professor'], self.professor.id)
        self.assertEqual(response.data['id_aluno'], self.aluno.matricula)
        self.assertEqual(response.data['comentario'], valid_data['comentario'])
        self.assertEqual(response.data['tags'][0], valid_data['tags'][0])
        self.assertEqual(response.data['tags'][1], valid_data['tags'][1])
             
    def test_criar_avaliacao_tags_vazia(self):
        valid_data = self.avaliacao_data.copy()
        valid_data['tags'] = []
        response = self.client.post(self.url, valid_data, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['id_professor'], self.professor.id)
        self.assertEqual(response.data['id_aluno'], self.aluno.matricula)
        self.assertEqual(response.data['comentario'], valid_data['comentario'])
        self.assertEqual(response.data['tags'], valid_data['tags'])
        
    def test_criar_avaliacao_token_invalido(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer TOKEN_INVALIDO')
        response = self.client.post(self.url, self.avaliacao_data, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)
        self.assertIn("code", response.data)
        self.assertIn("messages", response.data)
        self.assertEqual(response.data["code"], "token_not_valid")
        self.assertEqual(response.data["messages"][0]["message"], "O token é inválido ou expirado")
    
    def test_criar_avaliacao_token_tipo_invalido(self):
        refresh = RefreshToken.for_user(self.usuario_professor)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer ${refresh}')
        response = self.client.post(self.url, self.avaliacao_data, format='json')
        
        #Asserts
        self.assertEqual(response.status_code ,status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)
        self.assertIn("code", response.data)
        self.assertIn("messages", response.data)
        self.assertEqual(response.data["code"], "token_not_valid")
        self.assertEqual(str(response.data["messages"][0]["message"]), "O token é inválido ou expirado")
        
    def test_criar_avaliacao_token_aluno(self):
        refresh = RefreshToken.for_user(self.usuario_aluno)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.post(self.url, self.avaliacao_data, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("detail", response.data)
        self.assertEqual(response.data["detail"], "Acesso negado. Apenas professores podem criar avaliações.")


class DeletarAvaliacaoViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.usuario_professor = User.objects.create_user(
            username='fabio@example.com',
            email='fabio@example.com',
            password='1234'
        )
        self.professor = Professor.objects.create(
            nome="Fabio", 
            email="fabio@example.com",
            user=self.usuario_professor)
        self.login = {
            "email" : "andre@example.com",
            "senha" : "1234"
        }
        self.usuario_aluno = User.objects.create_user(
            username='andre@example.com',
            email='andre@example.com',
            password='1234'
        )
        self.aluno = Aluno.objects.create(
            matricula='121210210',
            nome='Andre Souza',
            email='andre@example.com',
            user=self.usuario_aluno
        )

        self.tag_criativo = Feedback.objects.create(nome="Criativo", grupo="Feedbacks")
        self.tag_proativo = Feedback.objects.create(nome="Proativo", grupo="Feedbacks")
        
        self.avaliacao = Avaliacao.objects.create(
            id_professor=self.professor,
            id_aluno=self.aluno,
            comentario="Bom demais",
        )
        self.avaliacao.tags.set([self.tag_criativo, self.tag_proativo])
        
        
        self.usuario_professor_2 = User.objects.create_user(
            username='fabio1@example.com',
            email='fabio1@example.com',
            password='1234'
        )
        self.professor_2 = Professor.objects.create(
            nome="Fabio", 
            email="fabio1@example.com",
            user=self.usuario_professor_2)
        self.avaliacao_2 = Avaliacao.objects.create(
            id_professor=self.professor_2,
            id_aluno=self.aluno,
            comentario="Bom demais",
        )
        self.avaliacao_2.tags.set([self.tag_criativo, self.tag_proativo])
        
        self.url = reverse('deletar_avaliacao', kwargs={'id_avaliacao': self.avaliacao.id_avaliacao})
        refresh = RefreshToken.for_user(self.usuario_professor)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_deletar_avaliacao_sucesso(self):
        response = self.client.delete(self.url, format='json')
        
        # Asserts
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_deletar_avaliacao_de_outro_professor(self):
        self.url = reverse('deletar_avaliacao', kwargs={'id_avaliacao': self.avaliacao_2.id_avaliacao})
        response = self.client.delete(self.url, format='json')
        
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertIn("detail", response.data)
        self.assertEqual("Você não tem permissão para deletar esta avaliação.", response.data["detail"])
         
    def test_deletar_avaliacao_inexistente(self):
        self.url = reverse('deletar_avaliacao', kwargs={'id_avaliacao': '00'})
        response = self.client.delete(self.url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("detail", response.data)
        self.assertEqual(response.data['detail'], "Avaliação não encontrada.")
           
    def test_deletar_avaliacao_token_invalido(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer TOKEN_INVALIDO')
        response = self.client.delete(self.url, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)
        self.assertIn("code", response.data)
        self.assertIn("messages", response.data)
        self.assertEqual(response.data["code"], "token_not_valid")
        self.assertEqual(response.data["messages"][0]["message"], "O token é inválido ou expirado")
    
    def test_deletar_avaliacao_token_tipo_invalido(self):
        refresh = RefreshToken.for_user(self.usuario_professor)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer ${refresh}')
        response = self.client.delete(self.url, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)
        self.assertIn("code", response.data)
        self.assertIn("messages", response.data)
        self.assertEqual(response.data["code"], "token_not_valid")
        self.assertEqual(str(response.data["messages"][0]["message"]), "O token é inválido ou expirado")
        
    def test_deletar_avaliacao_token_aluno(self):
        refresh = RefreshToken.for_user(self.usuario_aluno)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.delete(self.url, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("detail", response.data)
        self.assertEqual(response.data["detail"], "Acesso negado. Apenas o dono da avaliação pode deletá-la.")