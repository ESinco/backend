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

from api_projeto.models import Projeto, Associacao
from api_professor.models import Professor
from api_aluno.models import Aluno, HistoricoAcademico, Disciplina
from api_rest.models import Habilidade, Experiencia, Interesse
from api_projeto.views import *

from io import StringIO

import os

import pytz


#Model
class ProjetoModelTest(TestCase):

    def setUp(self):        
        usuario = User.objects.create_user(
            username='joao@example.com',
            email='joao@example.com',
            password='1234'
        )
        
        self.professor = Professor.objects.create(nome="João Arthur", email="joao@example.com", user=usuario)
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
        time_now_date = datetime.now(tz)
        data_de_criacao_date = self.projeto.data_de_criacao.date()
        self.assertEqual(data_de_criacao_date, time_now_date.date())
        self.assertEqual(self.projeto.vagas, 5)
        self.assertEqual(self.projeto.responsavel, self.professor)

    def test_projeto_str(self):
        expected_str = (f'nome: Projeto de Teste\n'
                f'descrição: Este é um projeto de teste.\n'
                f'laboratório: João Arthur\n'
                f'data de criação: {timezone.now().strftime("%d/%m/%Y")}\n'
                f'vagas: 5\n'
                f'responsavel: {self.projeto.responsavel}')
    
        self.assertEqual(str(self.projeto), expected_str)
        
#Views
# Testando POST de projeto.
class CriarProjetoViewTest(APITestCase):
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
        }

        refresh = RefreshToken.for_user(usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
    def test_criar_projeto_sucesso(self):
        response = self.client.post(self.url, self.projeto_data, format='json')
        
        # Asserts
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['nome'], self.projeto_data['nome'])
        self.assertEqual(response.data['responsavel'], self.professor.id)


    def test_criar_projeto_nome_vazio(self):
        invalid_data = self.projeto_data.copy()
        invalid_data['nome'] = ''
        response = self.client.post(self.url, invalid_data, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_criar_projeto_laboratorio_vazio(self):
        invalid_data = self.projeto_data.copy()
        invalid_data['laboratorio'] = ''
        response = self.client.post(self.url, invalid_data, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_criar_projeto_token_invalido(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer TOKEN_INVALIDO')
        response = self.client.post(self.url, self.projeto_data, format='json')
        
        #Asserts
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertIn("detail", response.data)
        self.assertIn("code", response.data)
        self.assertIn("messages", response.data)
        self.assertEqual("token_not_valid", response.data["code"])
        self.assertEqual("O token é inválido ou expirado", response.data["messages"][0]["message"])
    
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
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertIn("detail", response.data)
        self.assertIn("code", response.data)
        self.assertIn("messages", response.data)
        self.assertEqual("token_not_valid", response.data["code"])
        self.assertEqual("O token é inválido ou expirado", str(response.data["messages"][0]["message"]))
        
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
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertIn("detail", response.data)
        self.assertEqual("Acesso negado. Apenas professores podem criar projetos.", response.data["detail"])

    
# Testes de GETALL projetos
class GetProjetosViewTest(APITestCase):
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
        
# Testes de GETbyId para projetos
class GetByIdProjetoViewTest(APITestCase):
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

# Testes para a View de get_all_projetos_by_professor
class GetAllProjetosByProfessorViewTest(APITestCase):
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


class GetAllProjetosByAlunoViewTest(APITestCase):
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
        self.assertEqual(1, len(response.data))
        self.assertEqual('Projeto 1', response.data[0]['nome'])
        self.assertEqual('Descrição 1', response.data[0]['descricao'])
        self.assertEqual('Dono 1', response.data[0]['laboratorio'])
        self.assertEqual(5, response.data[0]['vagas'])
        self.assertEqual(None, response.data[0]['status'])

    def test_get_all_projetos_by_aluno_token_invalido(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer TOKEN_INVALIDO')        
        response = self.client.get(self.url, format='json')
        
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual("token_not_valid",response.data['code'])
        self.assertEqual("O token é inválido ou expirado",response.data['messages'][0]['message'])
    
    def test_get_all_projetos_by_aluno_token_do_tipo_errado(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.refresh}')        
        response = self.client.get(self.url, format='json')
        
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)
        self.assertEqual("token_not_valid",response.data['code'])
        self.assertEqual("Token tem tipo errado",response.data['messages'][0]['message'])

    def test_get_all_projetos_by_aluno_token_professor(self):
        refresh_professor = RefreshToken.for_user(self.usuario_professor)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh_professor.access_token}')        
        response = self.client.get(self.url, format='json')
        
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual("Acesso negado. Apenas alunos podem ver seus próprios projetos inscritos.", response.data['detail'])

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
        self.assertEqual("Nenhum projeto encontrado.", response.data['detail'])
        
        

class FiltragemPelaDisciplinaViewTestCase(APITestCase):
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
        self.historico = HistoricoAcademico.objects.create(
            aluno = self.aluno,
            historico_pdf='/media/historicos/historico.pdf',
            cra=8.9
        )
        self.disciplina = Disciplina.objects.create(
            historico=self.historico,
            codigo="1212555",
            nome="Engenharia de Software",
            professor="Rohit Gheyi",
            tipo="obrigatória",
            creditos=4,
            carga_horaria=20,
            media=9.6,
            situacao="Aprovado",
            periodo="2024.1"
        )
        self.associacao = Associacao.objects.create(
            projeto=self.projeto,
            aluno=self.aluno,
            status=None
        )
        self.parametros = {
            "alunos": ["232323232"],
            "disciplina": self.disciplina.codigo,
            "nota": ''
        }
        self.url = reverse('filtragem_disciplina')
        self.refresh = RefreshToken.for_user(self.usuario_professor)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}')

    def test_filtragem_de_projetos_pela_disciplina_sucesso(self):
        response = self.client.post(self.url, self.parametros, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
        self.assertEqual('232323232', response.data[0]['matricula'])
        self.assertEqual('levi', response.data[0]['nome'])
        self.assertEqual('levi@example.com', response.data[0]['email'])
        


class FiltragemPeloCraViewTestCase(APITestCase):
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
        self.historico = HistoricoAcademico.objects.create(
            aluno = self.aluno,
            historico_pdf='/media/historicos/historico.pdf',
            cra=8.9
        )
        self.associacao = Associacao.objects.create(
            projeto=self.projeto,
            aluno=self.aluno,
            status=None
        )
        self.parametros = {
            "alunos": ["232323232"],
            "cra": '8.0'
        }
        self.url = reverse('filtragem_cra')
        self.refresh = RefreshToken.for_user(self.usuario_professor)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}')

    def test_filtragem_de_projetos_pelo_cra_sucesso(self):
        response = self.client.post(self.url, self.parametros, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
        self.assertEqual('232323232', response.data[0]['matricula'])
        self.assertEqual('levi', response.data[0]['nome'])
        self.assertEqual('levi@example.com', response.data[0]['email'])
        

class FiltragemPelaHabilidadeViewTestCase(APITestCase):
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
        self.tag = Habilidade.objects.create(
            nome="Organização de Projetos",
            grupo="Soft Skills"
        )
        self.aluno.habilidades.add(self.tag)
        self.parametros = {
            "alunos": ["232323232"],            
            "habilidade": self.tag.nome
        }
        self.url = reverse('filtragem_habilidade')
        self.refresh = RefreshToken.for_user(self.usuario_professor)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}')

    def test_filtragem_de_projetos_pela_habilidade_sucesso(self):
        response = self.client.post(self.url, self.parametros, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
        self.assertEqual('232323232', response.data[0]['matricula'])
        self.assertEqual('levi', response.data[0]['nome'])
        self.assertEqual('levi@example.com', response.data[0]['email'])
        

class FiltragemPelaExperienciaViewTestCase(APITestCase):
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
        self.tag = Experiencia.objects.create(
            nome="Gestão de Equipes",
            grupo="Experiências"
        )
        self.aluno.experiencias.add(self.tag)
        self.parametros = {
            "alunos": ["232323232"],            
            "experiencia": self.tag.nome
        }
        self.url = reverse('filtragem_experiencia')
        self.refresh = RefreshToken.for_user(self.usuario_professor)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}')

    def test_filtragem_de_projetos_pela_experiencia_sucesso(self):
        response = self.client.post(self.url, self.parametros, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
        self.assertEqual('232323232', response.data[0]['matricula'])
        self.assertEqual('levi', response.data[0]['nome'])
        self.assertEqual('levi@example.com', response.data[0]['email'])
        

class FiltragemPeloInteresseViewTestCase(APITestCase):
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
        self.tag = Interesse.objects.create(
            nome="Banco de Dados",
            grupo="Interesses"
        )
        self.aluno.interesses.add(self.tag)
        self.parametros = {
            "alunos": ["232323232"],
            "interesse": self.tag.nome
        }
        self.url = reverse('filtragem_interesse')
        self.refresh = RefreshToken.for_user(self.usuario_professor)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.refresh.access_token}')

    def test_filtragem_de_projetos_pelo_interesse_sucesso(self):
        response = self.client.post(self.url, self.parametros, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
        self.assertEqual('232323232', response.data[0]['matricula'])
        self.assertEqual('levi', response.data[0]['nome'])
        self.assertEqual('levi@example.com', response.data[0]['email'])