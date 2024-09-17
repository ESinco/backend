from urllib.parse import urlencode

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
from datetime import datetime

from api_projeto.models import Projeto, Associacao, Colaborador
from api_professor.models import Professor
from api_aluno.models import Aluno
from api_projeto.views import *

from io import StringIO
import os
import pytz


class ProjetoModelTestCase(TestCase):

    def setUp(self):
        self.usuario = User.objects.create_user(
            username='joao@example.com',
            email='joao@example.com',
            password='1234'
        )
        self.professor = Professor.objects.create(nome="João Arthur", email="joao@example.com", user=self.usuario)
        self.projeto = Projeto.objects.create(
            nome='Projeto de Teste',
            descricao='Este é um projeto de teste.',
            laboratorio='João Arthur',
            vagas=5,
            responsavel=self.professor
        )

    def test_projeto_creation(self):
        self.assertIsInstance(self.projeto, Projeto)
        self.assertEqual(self.projeto.nome, 'Projeto de Teste')
        self.assertEqual(self.projeto.descricao, 'Este é um projeto de teste.')
        self.assertEqual(self.projeto.laboratorio, 'João Arthur')
        
        timezone_str = 'America/Fortaleza'
        tz = pytz.timezone(timezone_str)
        time_now_date = datetime.now(tz).date()
        data_de_criacao_date = self.projeto.data_de_criacao.date()
        self.assertEqual(data_de_criacao_date, time_now_date)
        self.assertEqual(self.projeto.vagas, 5)
        self.assertEqual(self.projeto.responsavel, self.professor)

    def test_projeto_str(self):
        expected_str = (
            f'nome: Projeto de Teste\n'
            f'descrição: Este é um projeto de teste.\n'
            f'laboratório: João Arthur\n'
            f'data de criação: {timezone.now().strftime("%d/%m/%Y")}\n'
            f'vagas: 5\n'
            f'responsavel: {self.projeto.responsavel}'
        )
        self.assertEqual(expected_str, str(self.projeto), "A representação em string do projeto está incorreta.")


class CriarProjetoViewTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        usuario = User.objects.create_user(
            username='fabio@example.com',
            email='fabio@example.com',
            password='1234'
        )
        self.professor = Professor.objects.create(nome="Fabio", email="fabio@example.com", user=usuario)
        self.url = reverse('criar_projeto')
        self.projeto_data = {
            "nome": "Projeto Teste",
            "descricao": "Descrição do projeto teste",
            "laboratorio": "Dono Teste",
            "vagas": 5,
            "habilidades": ["Programação"]
        }

        refresh = RefreshToken.for_user(usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        self.habilidade = Habilidade.objects.create(nome='Programação', grupo='Hard Skills')
        
    def test_criar_projeto_sucesso(self):
        response = self.client.post(self.url, self.projeto_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['nome'], self.projeto_data['nome'])
        self.assertEqual(response.data['responsavel']['id'], self.professor.id)
        self.assertEqual(response.data['responsavel']['nome'], self.professor.nome)
        self.assertEqual(response.data['responsavel']['email'], self.professor.email)
        self.assertEqual


    def test_criar_projeto_nome_vazio(self):
        invalid_data = self.projeto_data.copy()
        invalid_data['nome'] = ''
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_criar_projeto_laboratorio_vazio(self):
        invalid_data = self.projeto_data.copy()
        invalid_data['laboratorio'] = ''
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_criar_projeto_token_invalido(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer TOKEN_INVALIDO')
        response = self.client.post(self.url, self.projeto_data, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)
        self.assertIn("code", response.data)
        self.assertIn("messages", response.data)
        self.assertEqual(response.data["code"], "token_not_valid")
        self.assertEqual(response.data["messages"][0]["message"], "O token é inválido ou expirado")
    
    def test_criar_projeto_token_tipo_invalido(self):
        usuario = User.objects.create_user(
            username='fabio1@example.com',
            email='fabio1@example.com',
            password='1234'
        )
        refresh = RefreshToken.for_user(usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer ${refresh}')
        response = self.client.post(self.url, self.projeto_data, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)
        self.assertIn("code", response.data)
        self.assertIn("messages", response.data)
        self.assertEqual(response.data["code"], "token_not_valid")
        self.assertEqual(str(response.data["messages"][0]["message"]), "O token é inválido ou expirado")
        
    def test_criar_projeto_token_aluno(self):
        usuario = User.objects.create_user(
            username='andre@example.com',
            email='andre@example.com',
            password='1234'
        )
        self.aluno = Aluno.objects.create(
            matricula='121210210',
            nome='Andre Souza',
            email='andre@example.com',
            user=usuario
        )
        refresh = RefreshToken.for_user(usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        response = self.client.post(self.url, self.projeto_data, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("detail", response.data)
        self.assertEqual(response.data["detail"], "Acesso negado. Apenas professores podem criar projetos.")


class GetProjetosViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('get_projetos')
        usuario = User.objects.create_user(
            username='manel@example.com',
            email='manel@example.com',
            password='1234'
        )
        self.professor = Professor.objects.create(nome="Manel", email="manel@example.com", user=usuario)
        Projeto.objects.create(nome="Projeto 1", descricao="Descrição 1", laboratorio="Dono 1", vagas=5, responsavel=self.professor)
        Projeto.objects.create(nome="Projeto 2", descricao="Descrição 2", laboratorio="Dono 2", vagas=3, responsavel=self.professor)

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
        

class GetProjetoByIdViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        usuario = User.objects.create_user(
            username='eliane@example.com',
            email='eliane@example.com',
            password='1234'
        )
        self.professor = Professor.objects.create(nome="Eliane", email="eliane@example.com", user=usuario)
        self.projeto = Projeto.objects.create(nome="Projeto 1", descricao="Descrição 1", laboratorio="Dono 1", vagas=5, responsavel=self.professor)
        self.url = reverse('get_by_id_projeto', kwargs={'id_projeto': self.projeto.id_projeto})

    def test_get_by_id_projeto_sucesso(self):
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome'], self.projeto.nome)

    def test_get_by_id_projeto_nao_encontrado(self):
        url = reverse('get_by_id_projeto', kwargs={'id_projeto': 9999})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class GetAllProjetosByProfessorViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        usuario = User.objects.create_user(
            username='jorge@example.com',
            email='jorge@example.com',
            password='1234'
        )
        self.professor = Professor.objects.create(nome="Jorge", email="jorge@example.com", user=usuario)
        self.url = reverse('get_all_projetos_by_professor')
        Projeto.objects.create(nome="Projeto 1", descricao="Descrição 1", laboratorio="Dono 1", vagas=5, responsavel=self.professor)
        Projeto.objects.create(nome="Projeto 2", descricao="Descrição 2", laboratorio="Dono 2", vagas=3, responsavel=self.professor)

    def test_get_all_projetos_by_professor_sucesso(self):
        response = self.client.get(self.url, {'responsavel': self.professor.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_all_projetos_by_professor_nao_encontrado(self):
        response = self.client.get(self.url, {'responsavel': 9999}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_all_projetos_by_professor_sem_projeto(self):
        usuario = User.objects.create_user(
            username="dalton@example.com",
            email="dalton@example.com",
            password='1234'
        )
        self.professor2 = Professor.objects.create(nome="Dalton", email="dalton@example.com", user=usuario)
        response = self.client.get(self.url, {'responsavel': self.professor2.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        

class CriarProjetoCSVTestCase(APITestCase):

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


class GetAllProjetosByAlunoViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.usuario_aluno = User.objects.create_user(
            username='levi@example.com',
            email='levi@example.com',
            password='1234'
        )
        self.aluno = Aluno.objects.create(
            matricula="232323232",
            nome="levi", 
            email="levi@example.com", 
            user=self.usuario_aluno
        )
        self.usuario_professor = User.objects.create_user(
            username='professor@teste.com', 
            email='professor@teste.com',                                              
            password='senha123'
        )
        self.professor = Professor.objects.create(
            user=self.usuario_professor, 
            nome='Professor Teste', 
            email='professor@teste.com'
        )
        self.projeto = Projeto.objects.create(
            nome="Projeto 1", 
            descricao="Descrição 1", 
            laboratorio="Dono 1", 
            vagas=5, 
            responsavel=self.professor
        )
        self.associacao = Associacao.objects.create(
            projeto=self.projeto,
            aluno=self.aluno,
            status=None
        )
        self.url = reverse('get_all_projetos_by_aluno')
        self.refresh = RefreshToken.for_user(self.usuario_aluno)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}')

    def test_get_all_projetos_by_aluno_sucesso(self):
        response = self.client.get(self.url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nome'], 'Projeto 1')
        self.assertEqual(response.data[0]['descricao'], 'Descrição 1')
        self.assertEqual(response.data[0]['laboratorio'], 'Dono 1')
        self.assertEqual(response.data[0]['vagas'], 5)
        self.assertEqual(response.data[0]['status'], None)

    def test_get_all_projetos_by_aluno_token_invalido(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer TOKEN_INVALIDO')        
        response = self.client.get(self.url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['code'], "token_not_valid")
        self.assertEqual(response.data['messages'][0]['message'], "O token é inválido ou expirado")
    
    def test_get_all_projetos_by_aluno_token_do_tipo_errado(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.refresh}')        
        response = self.client.get(self.url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['code'], "token_not_valid")
        self.assertEqual(response.data['messages'][0]['message'], "Token tem tipo errado")

    def test_get_all_projetos_by_aluno_token_professor(self):
        refresh_professor = RefreshToken.for_user(self.usuario_professor)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh_professor.access_token}')        
        response = self.client.get(self.url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], "Acesso negado. Apenas alunos podem ver seus próprios projetos inscritos.")

    def test_get_all_projetos_by_aluno_sem_projeto(self):
        usuario_aluno2 = User.objects.create_user(
            username="fernando@example.com",
            email="fernando@example.com",
            password='1234'
        )
        self.aluno2 = Aluno.objects.create(
            matricula="232323233",
            nome="fernando", 
            email="fernando@example.com", 
            user=usuario_aluno2
        )
        refresh = RefreshToken.for_user(usuario_aluno2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')   
        response = self.client.get(self.url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'],"Nenhum projeto encontrado.")
        
class CadastrarColaboradorTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.user_responsavel = User.objects.create_user(username='professor_responsavel@example.com', password='1234')
        self.professor_responsavel = Professor.objects.create(user=self.user_responsavel, nome='Professor Responsável', email='professor_responsavel@example.com')

        self.user_colaborador = User.objects.create_user(username='professor_colaborador@example.com', password='1234')
        self.professor_colaborador = Professor.objects.create(user=self.user_colaborador, nome='Professor Colaborador', email='professor_colaborador@example.com')

        self.projeto = Projeto.objects.create(nome='Projeto Teste', data_de_criacao=timezone.now(), responsavel=self.professor_responsavel)

        self.url = reverse('cadastrar_colaborador', args=[self.projeto.id_projeto, self.professor_colaborador.email])
        self.client.force_authenticate(user=self.user_responsavel)

    def test_cadastrar_colaborador_com_sucesso(self):
        response = self.client.post(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['detail'], 'Associação criada com sucesso.')
        self.assertEqual(Colaborador.objects.count(), 1)
        
    def test_projeto_nao_encontrado(self):
        # Tentando associar a um projeto que não existe
        url_projeto_invalido = reverse('cadastrar_colaborador', args=[9999, self.professor_colaborador.email])
        response = self.client.post(url_projeto_invalido, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'Projeto não encontrado.')
    
    def test_professor_nao_responsavel_acesso_negado(self):
        # Autenticar como outro professor que não é o responsável
        user_professor_nao_responsavel = User.objects.create_user(username='outro_professor@example.com', password='1234')
        professor_nao_responsavel = Professor.objects.create(user=user_professor_nao_responsavel, nome='Outro Professor', email='outro_professor@example.com')

        self.client.force_authenticate(user=user_professor_nao_responsavel)
        response = self.client.post(self.url, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'Acesso negado. Apenas o responsavel do projeto pode cadastrar um colaborador.')

    def test_professor_colaborador_nao_encontrado(self):
        # Tentando associar um professor colaborador que não existe
        url_colaborador_invalido = reverse('cadastrar_colaborador', args=[self.projeto.id_projeto, 'nao_existe@example.com'])
        response = self.client.post(url_colaborador_invalido, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'Professor colaborador não encontrado.')

    def test_professor_ja_e_colaborador(self):
        # Tentando criar colaborador duas vezes
        Colaborador.objects.create(professor=self.professor_colaborador, projeto=self.projeto)

        response = self.client.post(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Professor ja é colaborador desse projeto.')
