from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse

from api_rest.views import *
from api_rest.models import Projeto, Professor

#Model
class ProjetoModelTest(TestCase):

    def setUp(self):
        self.professor = Professor.objects.create(nome="João Arthur", email="joao@example.com", senha="senha123")
        self.projeto = Projeto.objects.create(
            nome='Projeto de Teste',
            descricao='Este é um projeto de teste.',
            dono='João Arthur',
            data_de_criacao=20240814,
            vagas=5,
            responsavel=self.professor
        )

    def test_projeto_creation(self):
        self.assertIsInstance(self.projeto, Projeto)
        self.assertEqual(self.projeto.nome, 'Projeto de Teste')
        self.assertEqual(self.projeto.descricao, 'Este é um projeto de teste.')
        self.assertEqual(self.projeto.dono, 'João Arthur')
        self.assertEqual(self.projeto.data_de_criacao, 20240814)
        self.assertEqual(self.projeto.vagas, 5)
        self.assertEqual(self.projeto.responsavel, self.professor)

    def test_projeto_str(self):
        expected_str = (f'nome: Projeto de Teste\n'
                f'descrição: Este é um projeto de teste.\n'
                f'dono: João Arthur\n'
                f'data de criação: 20240814\n'
                f'vagas: 5\n'
                f'responsavel: {self.projeto.responsavel}')
    
        self.assertEqual(str(self.projeto), expected_str)
        
#Views
# Testando POST de projeto.
class CriarProjetoViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.professor = Professor.objects.create(nome="Fabio", email="fabio@example.com", senha="1234")
        self.url = reverse('criar_projeto')
        self.projeto_data = {
            "nome": "Projeto Teste",
            "descricao": "Descrição do projeto teste",
            "dono": "Dono Teste",
            "data_de_criacao": 123456789,
            "vagas": 5,
            "responsavel": self.professor.id_professor
        }

    def test_criar_projeto_sucesso(self):
        response = self.client.post(self.url, self.projeto_data, format='json')
        
        # Asserts
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['nome'], self.projeto_data['nome'])
        self.assertEqual(response.data['responsavel'], self.projeto_data['responsavel'])


    def test_criar_projeto_nome_vazio(self):
        invalid_data = self.projeto_data.copy()
        invalid_data['nome'] = ''
        response = self.client.post(self.url, invalid_data, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_criar_projeto_professor_vazio(self):
        invalid_data = self.projeto_data.copy()
        invalid_data['responsavel'] = ''
        response = self.client.post(self.url, invalid_data, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_criar_projeto_dono_vazio(self):
        invalid_data = self.projeto_data.copy()
        invalid_data['dono'] = ''
        response = self.client.post(self.url, invalid_data, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    
# Testes de GETALL projetos
class GetProjetosViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('get_projetos')
        self.professor = Professor.objects.create(nome="Manel", email="manel@example.com", senha="1234")
        Projeto.objects.create(nome="Projeto 1", descricao="Descrição 1", dono="Dono 1", data_de_criacao=123456789, vagas=5, responsavel=self.professor)
        Projeto.objects.create(nome="Projeto 2", descricao="Descrição 2", dono="Dono 2", data_de_criacao=123456780, vagas=3, responsavel=self.professor)

    def test_get_projetos_sucesso(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_get_projetos_sucesso2(self):
        Projeto.objects.all().delete()
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
    
    def test_get_projetos_professores_excluido(self):
        Professor.objects.all().delete()
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        
# Testes de GETbyId para projetos
class GetByIdProjetoViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.professor = Professor.objects.create(nome="Eliane", email="eliane@example.com", senha="1234")
        self.projeto = Projeto.objects.create(nome="Projeto 1", descricao="Descrição 1", dono="Dono 1", data_de_criacao=123456789, vagas=5, responsavel=self.professor)
        self.url = reverse('get_by_id_projeto', kwargs={'id_projeto': self.projeto.id_projeto})

    def test_get_by_id_projeto_sucesso(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome'], self.projeto.nome)

    def test_get_by_id_projeto_nao_encontrado(self):
        url = reverse('get_by_id_projeto', kwargs={'id_projeto': 9999})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

# Testes para a View de get_all_projetos_by_professor
class GetAllProjetosByProfessorViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.professor = Professor.objects.create(nome="Jorge", email="jorge@example.com", senha="1234")
        self.url = reverse('get_all_projetos_by_professor')
        Projeto.objects.create(nome="Projeto 1", descricao="Descrição 1", dono="Dono 1", data_de_criacao=123456789, vagas=5, responsavel=self.professor)
        Projeto.objects.create(nome="Projeto 2", descricao="Descrição 2", dono="Dono 2", data_de_criacao=123456780, vagas=3, responsavel=self.professor)

    def test_get_all_projetos_by_professor_sucesso(self):
        response = self.client.get(self.url, {'responsavel': self.professor.id_professor}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_all_projetos_by_professor_nao_encontrado(self):
        response = self.client.get(self.url, {'responsavel': 9999}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_all_projetos_by_professor_sem_projeto(self):
        self.professor2 = Professor.objects.create(nome="Dalton", email="dalton@example.com", senha="1234")
        response = self.client.get(self.url, {'responsavel': self.professor2.id_professor}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        