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
from django.core import mail

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
        self.habilidade = Habilidade.objects.create(nome='Programação', grupo='Hard Skills')
        self.projeto_data = {
            "nome": "Projeto Teste",
            "descricao": "Descrição do projeto teste",
            "laboratorio": "Dono Teste",
            "vagas": 5,
            "habilidades": [self.habilidade.id]
        }

        refresh = RefreshToken.for_user(usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
    def test_criar_projeto_sucesso(self):
        response = self.client.post(self.url, self.projeto_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['nome'], self.projeto_data['nome'])
        self.assertEqual(response.data['responsavel']['id'], self.professor.id)
        self.assertEqual(response.data['responsavel']['nome'], self.professor.nome)
        self.assertEqual(response.data['responsavel']['email'], self.professor.email)
        self.assertEqual(response.data['habilidades'][0]['id'], self.habilidade.id)


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
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("detail", response.data)
        self.assertEqual(response.data["detail"], "Acesso negado. Apenas professores podem criar projetos.")


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
        
        refresh = RefreshToken.for_user(usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
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
        self.user = User.objects.create_user(username='professor@teste.com', password='senha123')
        self.professor = Professor.objects.create(user=self.user, nome='Professor Teste', email='professor@teste.com')
        
        self.aluno1 = Aluno.objects.create(user=User.objects.create_user(username='aluno1@teste.com', password='senha123'),
                                           matricula='123456789', nome='Aluno 1', email='aluno1@teste.com')
        self.aluno2 = Aluno.objects.create(user=User.objects.create_user(username='aluno2@teste.com', password='senha123'),
                                           matricula='987654321', nome='Aluno 2', email='aluno2@teste.com')
        
        self.url = reverse('criar_projeto_csv')
        self.client.force_authenticate(user=self.user)

    def test_criar_projeto_csv_sucesso(self):
        file_path = os.path.join(os.path.dirname(__file__), 'test_data/testeProjetoCSV.csv')
        
        with open(file_path, 'rb') as f:
            csv_file = SimpleUploadedFile("alunos.csv", f.read(), content_type="text/csv")
        
        url = reverse('criar_projeto_csv')
        response = self.client.post(url, {'file': csv_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Projeto.objects.count(), 1)
        self.assertEqual(Associacao.objects.count(), 2)

    def test_arquivo_nao_enviado(self):
        response = self.client.post(self.url, {}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Arquivo não encontrado.')

    def test_arquivo_nao_csv(self):
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
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Projeto.objects.count(), 1)
        self.assertEqual(Associacao.objects.count(), 1)
        
    def test_csv_vazio(self):
        file_path = os.path.join(os.path.dirname(__file__), './test_data/testeVazio.csv')
        
        with open(file_path, 'rb') as f:
            csv_file = SimpleUploadedFile("alunos.csv", f.read(), content_type="text/csv")
            
        url = reverse('criar_projeto_csv')
        response = self.client.post(url, {'file': csv_file}, format='multipart')
        
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
        url_projeto_invalido = reverse('cadastrar_colaborador', args=[9999, self.professor_colaborador.email])
        response = self.client.post(url_projeto_invalido, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'Projeto não encontrado.')
    
    def test_professor_nao_responsavel_acesso_negado(self):
        user_professor_nao_responsavel = User.objects.create_user(username='outro_professor@example.com', password='1234')
        professor_nao_responsavel = Professor.objects.create(user=user_professor_nao_responsavel, nome='Outro Professor', email='outro_professor@example.com')

        self.client.force_authenticate(user=user_professor_nao_responsavel)
        response = self.client.post(self.url, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'Acesso negado. Apenas o responsavel do projeto pode cadastrar um colaborador.')

    def test_professor_colaborador_nao_encontrado(self):
        url_colaborador_invalido = reverse('cadastrar_colaborador', args=[self.projeto.id_projeto, 'nao_existe@example.com'])
        response = self.client.post(url_colaborador_invalido, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'Professor colaborador não encontrado.')

    def test_professor_ja_e_colaborador(self):
        Colaborador.objects.create(professor=self.professor_colaborador, projeto=self.projeto)

        response = self.client.post(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Professor ja é colaborador desse projeto.')


class EditarProjetoTests(APITestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(
            username='profmarcos@example.com',
            email='profmarcos@example.com',
            password='senhaSegura'
        )
        self.professor = Professor.objects.create(
            nome="Prof. Marcos",
            user=self.usuario
        )
        self.projeto = Projeto.objects.create(
            nome="Projeto Inicial",
            descricao="Descrição inicial do projeto.",
            laboratorio="Lab A",
            vagas=3,
            responsavel=self.professor
        )
        
        self.habilidade1 = Habilidade.objects.create(nome="Computação em Nuvem", grupo="Hard Skills")
        self.habilidade2 = Habilidade.objects.create(nome="Pensamento Criativo", grupo="Soft Skills")

        self.url_editar = reverse('editar_projeto', args=[self.projeto.id_projeto])
        self.client.force_authenticate(user=self.usuario)

        self.data = {
            'nome': 'Novo Projeto',
            'descricao': 'Nova descrição',
            'laboratorio': 'Lab B',
            'vagas': 5,
            'habilidades': [self.habilidade1.id, self.habilidade2.id]
        }

    def test_editar_projeto(self):
        response = self.client.put(self.url_editar, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        projeto_atualizado = Projeto.objects.get(id_projeto=self.projeto.id_projeto)
        self.assertEqual(projeto_atualizado.nome, 'Novo Projeto')
        self.assertEqual(projeto_atualizado.descricao, 'Nova descrição')
        self.assertEqual(projeto_atualizado.laboratorio, 'Lab B')
        self.assertEqual(projeto_atualizado.vagas, 5)

        habilidades_projeto = list(projeto_atualizado.habilidades.all())
        self.assertEqual(len(habilidades_projeto), 2)
        self.assertIn(self.habilidade1, habilidades_projeto)
        self.assertIn(self.habilidade2, habilidades_projeto)

    def test_projeto_nao_encontrado(self):
        url_invalida = reverse('editar_projeto', args=[999])
        response = self.client.put(url_invalida, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_acesso_negado_para_nao_professor(self):
        usuario_nao_professor = User.objects.create_user(
            username='aluno@example.com',
            email='aluno@example.com',
            password='senhaSegura'
        )
        self.client.force_authenticate(user=usuario_nao_professor)
        
        response = self.client.put(self.url_editar, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_acesso_negado_para_outro_professor_nao_responsavel(self):
        usuario_professor2 = User.objects.create_user(
            username='profjoao@teste.com', 
            email='profjoao@teste.com',                                              
            password='senha123'
        )
        self.client.force_authenticate(user=usuario_professor2)
        response = self.client.put(self.url_editar, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class RecomendacaoTests(APITestCase):
    def setUp(self):
        self.usuario_aluno = User.objects.create_user(
            username='beatriz@example.com',
            email='beatriz@example.com',
            password='senhaSegura'
        )
        self.aluno = Aluno.objects.create(
            matricula="200000002",
            nome="Beatriz", 
            email="beatriz@example.com", 
            user=self.usuario_aluno
        )
        self.usuario_professor1 = User.objects.create_user(
            username='prof1@example.com',
            email='prof1@example.com',
            password='senhaSegura'
        )
        self.professor1 = Professor.objects.create(
            nome="Prof. 1",
            email='prof1@example.com',
            user=self.usuario_professor1
        )
        self.usuario_professor2 = User.objects.create_user(
            username='prof2@example.com',
            email='prof2@example.com',
            password='senhaSegura'
        )
        self.professor2 = Professor.objects.create(
            nome="Prof. 2",
            email='prof2@example.com',
            user=self.usuario_professor2
        )

        self.habilidade1 = Habilidade.objects.create(nome="Computação em Nuvem", grupo="Hard Skills")
        self.habilidade2 = Habilidade.objects.create(nome="Pensamento Criativo", grupo="Soft Skills")
        self.habilidade3 = Habilidade.objects.create(nome="Inteligência Artificial", grupo="Hard Skills")
        self.habilidade4 = Habilidade.objects.create(nome="Desenvolvimento Mobile", grupo="Hard Skills")
        self.habilidade5= Habilidade.objects.create(nome="Testes", grupo="Hard Skills")
        self.habilidade6 = Habilidade.objects.create(nome="Negociação", grupo="Soft Skills")

        self.projeto1 = Projeto.objects.create(
            nome='Projeto 1',
            descricao='Descrição do Projeto 1',
            laboratorio='Laboratório 1',
            vagas=5,
            responsavel=self.professor1
        )
        self.projeto2 = Projeto.objects.create(
            nome='Projeto 2',
            descricao='Descrição do Projeto 2',
            laboratorio='Laboratório 2',
            vagas=5,
            responsavel=self.professor2
        )
        self.projeto3 = Projeto.objects.create(
            nome='Projeto 3',
            descricao='Descrição do Projeto 3',
            laboratorio='Laboratório 3',
            vagas=5,
            responsavel=self.professor2
        )
        self.projeto4 = Projeto.objects.create(
            nome='Projeto 4',
            descricao='Descrição do Projeto 4',
            laboratorio='Laboratório 4',
            vagas=5,
            responsavel=self.professor1
        )
        self.projeto5 = Projeto.objects.create(
            nome='Projeto 5',
            descricao='Descrição do Projeto 5',
            laboratorio='Laboratório 5',
            vagas=5,
            responsavel=self.professor1
        )
        self.projeto1.habilidades.add(self.habilidade1, self.habilidade2, self.habilidade3)
        self.projeto2.habilidades.add(self.habilidade1, self.habilidade2)
        self.projeto3.habilidades.add(self.habilidade1)
        self.projeto5.habilidades.add(self.habilidade4)

        self.url_recomendacao = reverse('recomendacao')

    def test_recomendacao_aluno_com_recomendacoes(self):
        self.aluno.habilidades.add(self.habilidade2, self.habilidade3, self.habilidade4, self.habilidade6)
        self.client.force_authenticate(user=self.usuario_aluno)
        response = self.client.get(self.url_recomendacao)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 3)
        self.assertEqual(response.data[0]['id_projeto'], self.projeto1.id_projeto)
        self.assertEqual(response.data[1]['id_projeto'], self.projeto5.id_projeto)
        self.assertEqual(response.data[2]['id_projeto'], self.projeto2.id_projeto)
        self.assertEqual(response.data[3]['id_projeto'], self.projeto4.id_projeto)
        self.assertEqual(response.data[4]['id_projeto'], self.projeto3.id_projeto)

    def test_recomendacao_aluno_sem_recomendacoes(self):
        self.aluno.habilidades.add(self.habilidade5, self.habilidade6)
        self.client.force_authenticate(user=self.usuario_aluno)
        response = self.client.get(self.url_recomendacao)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_recomendacao_aluno_sem_habilidades(self):
        self.client.force_authenticate(user=self.usuario_aluno)
        response = self.client.get(self.url_recomendacao)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_acesso_negado_para_usuario_nao_aluno(self):
        self.client.force_authenticate(user=self.usuario_professor1)
        response = self.client.get(self.url_recomendacao)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("Acesso negado. Apenas alunos podem ver recomendações de projetos.", str(response.data))

    def test_metodo_nao_permitido(self):
        self.client.force_authenticate(user=self.usuario_aluno)
        response = self.client.post(self.url_recomendacao)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class GerenciarInscricaoTests(APITestCase):
    def setUp(self):
        self.aluno_usuario = User.objects.create_user(
            username='beatriz@example.com',
            email='beatriz@example.com',
            password='senhaSegura'
        )
        self.aluno = Aluno.objects.create(
            matricula='200000002',
            nome='Beatriz', 
            email='beatriz@example.com', 
            user=self.aluno_usuario
        )
        self.professor_usuario = User.objects.create_user(
            username='profjoao@example.com',
            email='profjoao@example.com',
            password='senhaSegura'
        )
        self.professor = Professor.objects.create(
            nome='Prof. Joao',
            email='profjoao@example.com',
            user=self.professor_usuario
        )
        self.projeto = Projeto.objects.create(
            nome='Projeto 1',
            descricao='Descrição do Projeto 1',
            laboratorio='Laboratório 1',
            vagas=5,
            responsavel=self.professor
        )

        self.associacao = Associacao.objects.create(aluno=self.aluno, projeto=self.projeto, status=True)

        self.url_gerenciar_inscricao = reverse('gerenciar_inscricao', args=[self.projeto.id_projeto, self.aluno.matricula])
    
    def test_gerenciar_inscricao_com_sucesso(self):
        self.client.force_authenticate(user=self.professor_usuario)
        response = self.client.post(self.url_gerenciar_inscricao, data={'status': False, 'enviar_email': True})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.associacao.refresh_from_db()
        self.assertFalse(self.associacao.status)
        self.assertTrue(response.data['email_enviado'])

    def test_inscricao_nao_encontrada(self):
        self.client.force_authenticate(user=self.professor_usuario)
        usuario_sem_inscricao = User.objects.create_user(
            username='seminscricao@example.com',
            email='seminscricao@example.com',
            password='senhaSegura'
        )
        aluno_sem_inscricao = Aluno.objects.create(
            matricula='000000000',
            nome='Aluno sem inscrição', 
            email='seminscricao@example.com', 
            user=usuario_sem_inscricao
        )
        url_aluno_sem_inscricao = reverse('gerenciar_inscricao', args=[self.projeto.id_projeto, aluno_sem_inscricao.matricula])
        response = self.client.post(url_aluno_sem_inscricao, data={'status': True, 'enviar_email': True})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("Essa inscrição não existe.", response.data['detail'])


    def test_acesso_negado_para_aluno(self):
        self.client.force_authenticate(user=self.aluno_usuario)
        response = self.client.post(self.url_gerenciar_inscricao, data={})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("Acesso negado. Apenas professores podem gerenciar inscrições.", response.data['detail'])

    def test_projeto_nao_encontrado(self):
        self.client.force_authenticate(user=self.professor_usuario)
        url_invalida = reverse('gerenciar_inscricao', args=[999, self.aluno.matricula])
        response = self.client.post(url_invalida, data={})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("Projeto não encontrado.", response.data['detail'])

    def test_metodo_incorreto(self):
        self.client.force_authenticate(user=self.professor_usuario)
        response = self.client.put(self.url_gerenciar_inscricao, data={})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
        
class SalvarFiltragemTest(APITestCase):
    def setUp(self):
        self.professor_usuario = User.objects.create_user(
            username='profjoao@example.com',
            email='profjoao@example.com',
            password='senhaSegura'
        )
        self.professor = Professor.objects.create(
            nome='Prof. Joao',
            email='profjoao@example.com',
            user=self.professor_usuario
        )

        self.projeto = Projeto.objects.create(
            nome='Projeto 1',
            descricao='Descrição do Projeto 1',
            laboratorio='Laboratório 1',
            vagas=5,
            responsavel=self.professor
        )
        
        self.colaborador_usuario = User.objects.create_user(
            username='colaborador@example.com',
            email='colaborador@example.com',
            password='senhaSegura'
        )
        self.colaborador = Professor.objects.create(
            nome='Prof. Maria',
            email='colaborador@example.com',
            user=self.colaborador_usuario
        )

        Colaborador.objects.create(
            professor=self.colaborador,
            projeto=self.projeto
        )

        self.habilidade1 = Habilidade.objects.create(nome='Python')
        self.habilidade2 = Habilidade.objects.create(nome='Java')
        
        self.experiencia1 = Experiencia.objects.create(nome='Estágio em TI')
        self.experiencia2 = Experiencia.objects.create(nome='Desenvolvimento de Software')

        self.interesse1 = Interesse.objects.create(nome='Desenvolvimento Web', grupo='Tecnologia')
        self.interesse2 = Interesse.objects.create(nome='Data Science', grupo='Tecnologia')

        self.client = APIClient()
    
    def test_professor_responsavel_criar_filtragem(self):
        self.client.force_authenticate(user=self.professor_usuario)

        data = {
            'id_projeto': self.projeto.id_projeto,
            'titulo': 'Filtro 1',
            'filtro_habilidades': [self.habilidade1.id, self.habilidade2.id],
            'filtro_experiencias': [self.experiencia1.id],
            'filtro_interesses': [self.interesse1.id],
            'filtro_disciplinas': [{"disciplina": "Matemática", "nota": 8}],
            'filtro_cra': 7.5
        }

        response = self.client.post(reverse('salvar_filtragem'), data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['titulo'], 'Filtro 1')
    
    def test_criar_filtragem_sem_titulo(self):
        self.client.force_authenticate(user=self.professor_usuario)
        data = {
            'id_projeto': self.projeto.id_projeto,
            'titulo': '',
            'filtro_habilidades': [],
            'filtro_experiencias': [],
            'filtro_interesses': [],
            'filtro_disciplinas': [{"disciplina": "Matemática", "nota": 8}],
            'filtro_cra': 7.5
        }
        response = self.client.post(reverse('salvar_filtragem'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_criar_filtragem_disciplinas_invalidas(self):
        self.client.force_authenticate(user=self.professor_usuario)
        data = {
            'id_projeto': self.projeto.id_projeto,
            'titulo': 'Filtro 2',
            'filtro_habilidades': [],
            'filtro_experiencias': [],
            'filtro_interesses': [],
            'filtro_disciplinas': [{"invalid_key": "Matemática", "nota": 8}],
            'filtro_cra': 7.5
        }
        response = self.client.post(reverse('salvar_filtragem'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_criar_filtragem_nota_fora_do_intervalo(self):
        self.client.force_authenticate(user=self.professor_usuario)
        data = {
            'id_projeto': self.projeto.id_projeto,
            'titulo': 'Filtro 3',
            'filtro_habilidades': [],
            'filtro_experiencias': [],
            'filtro_interesses': [],
            'filtro_disciplinas': [{"disciplina": "Matemática", "nota": 11}],  # Nota inválida
            'filtro_cra': 7.5
        }
        response = self.client.post(reverse('salvar_filtragem'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_criar_filtragem_sem_autenticacao(self):
        data = {
            'id_projeto': self.projeto.id_projeto,
            'titulo': 'Filtro 4',
            'filtro_habilidades': [],
            'filtro_experiencias': [],
            'filtro_interesses': [],
            'filtro_disciplinas': [{"disciplina": "Matemática", "nota": 8}],
            'filtro_cra': 7.5
        }
        response = self.client.post(reverse('salvar_filtragem'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_colaborador_criar_filtragem(self):
        self.client.force_authenticate(user=self.colaborador_usuario)

        data = {
            'id_projeto': self.projeto.id_projeto,
            'titulo': 'Filtro do Colaborador',
            'filtro_habilidades': [self.habilidade1.id],
            'filtro_experiencias': [self.experiencia1.id],
            'filtro_interesses': [self.interesse1.id, self.interesse2.id],
            'filtro_disciplinas': [{"disciplina": "Matemática", "nota": 8}],
            'filtro_cra': 7.5
        }
        response = self.client.post(reverse('salvar_filtragem'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

class GetListaByIdTest(APITestCase):
    
    def setUp(self):
        self.professor_usuario = User.objects.create_user(
            username='profjoao@example.com',
            email='profjoao@example.com',
            password='senhaSegura'
        )
        self.professor = Professor.objects.create(
            nome='Prof. Joao',
            email='profjoao@example.com',
            user=self.professor_usuario
        )
        
        self.professor_nao_dono_usuario = User.objects.create_user(
            username='profmaria@example.com',
            email='profmaria@example.com',
            password='senhaSegura'
        )
        self.professor_nao_dono = Professor.objects.create(
            nome='Prof. Maria',
            email='profmaria@example.com',
            user=self.professor_nao_dono_usuario
        )
        
        self.projeto = Projeto.objects.create(
            nome='Projeto 1',
            descricao='Descrição do Projeto 1',
            laboratorio='Laboratório 1',
            vagas=5,
            responsavel=self.professor
        )

        self.lista = Lista_Filtragem.objects.create(
            id_projeto=self.projeto,
            id_professor=self.professor,
            titulo='Lista Original',
            filtro_disciplinas=[{"disciplina": "Matemática", "nota": 8}],
            filtro_cra=7.5
        )
        
        self.url = reverse('get_lista_by_id', args=[self.lista.id_lista])
    
    def test_professor_dono_acessa_lista(self):
        self.client.force_authenticate(user=self.professor_usuario)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['titulo'], "Lista Original")
    
    def test_professor_nao_dono_nao_acessa_lista(self):
        self.client.force_authenticate(user=self.professor_nao_dono_usuario)
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], "Apenas o dono da lista pode visualizá-la")
    
    def test_lista_nao_encontrada(self):
        self.client.force_authenticate(user=self.professor_usuario)
        
        url_invalida = reverse('get_lista_by_id', args=[999])
        response = self.client.get(url_invalida)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class DeletarListaFiltragemTest(APITestCase):
    def setUp(self):
        self.professor_usuario = User.objects.create_user(
            username='professor@example.com',
            email='professor@example.com',
            password='senhaSegura'
        )
        self.professor = Professor.objects.create(
            nome='Prof. Exemplo',
            email='professor@example.com',
            user=self.professor_usuario
        )
        
        self.projeto = Projeto.objects.create(
            nome='Projeto 1',
            descricao='Descrição do Projeto 1',
            laboratorio='Laboratório 1',
            vagas=5,
            responsavel=self.professor
        )
        
        self.lista = Lista_Filtragem.objects.create(
            id_projeto= self.projeto,
            id_professor=self.professor,
            titulo='Lista para deletar',
            filtro_disciplinas=[{"disciplina": "Matemática", "nota": 8}],
            filtro_cra=7.5
        )

        self.url_deletar = reverse('deletar_lista_filtragem', args=[self.lista.id_lista])

    def test_deletar_lista_com_sucesso(self):
        self.client.force_authenticate(user=self.professor_usuario)
        response = self.client.delete(self.url_deletar)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lista_Filtragem.objects.filter(pk=self.lista.id_lista).exists())

    def test_deletar_lista_usuario_nao_autenticado(self):
        response = self.client.delete(self.url_deletar)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_deletar_lista_dono_nao_encontrado(self):
        self.client.force_authenticate(user=self.professor_usuario)
        self.lista.delete()
        response = self.client.delete(self.url_deletar)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_deletar_lista_acesso_negado(self):
        outro_usuario = User.objects.create_user(
            username='outro_professor@example.com',
            email='outro_professor@example.com',
            password='senhaSegura'
        )

        self.client.force_authenticate(user=outro_usuario)
        response = self.client.delete(self.url_deletar)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
class EditarFiltragemTest(APITestCase):
    def setUp(self):
        self.professor_usuario = User.objects.create_user(
            username='professor@example.com',
            email='professor@example.com',
            password='senhaSegura'
        )
        self.professor = Professor.objects.create(
            nome='Prof. Exemplo',
            email='professor@example.com',
            user=self.professor_usuario
        )

        self.habilidade1 = Habilidade.objects.create(nome='Python')
        self.experiencia1 = Experiencia.objects.create(nome='Estágio em TI')
        self.interesse1 = Interesse.objects.create(nome='Desenvolvimento Web')

        self.projeto = Projeto.objects.create(
            nome='Projeto 1',
            descricao='Descrição do Projeto 1',
            laboratorio='Laboratório 1',
            vagas=5,
            responsavel=self.professor
        )
        
        self.lista = Lista_Filtragem.objects.create(
            id_projeto= self.projeto,
            id_professor=self.professor,
            titulo='Lista Original',
            filtro_disciplinas=[{"disciplina": "Matemática", "nota": 8}],
            filtro_cra=7.5
        )
        
        self.lista.filtro_habilidades.set([self.habilidade1])
        self.url_editar = reverse('editar_filtragem', args=[self.lista.id_lista])

    def test_editar_lista_com_sucesso(self):
        self.client.force_authenticate(user=self.professor_usuario)
        data = {
            'titulo': 'Lista Editada',
            'filtro_experiencias': [self.experiencia1.id],
            'filtro_interesses': [self.interesse1.id],
            'filtro_disciplinas': [{"disciplina": "Matemática", "nota": 9}],
            'filtro_cra': 8.0
        }
        response = self.client.put(self.url_editar, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.lista.refresh_from_db()
        self.assertEqual(self.lista.titulo, 'Lista Editada')
        self.assertEqual(self.lista.filtro_cra, 8.0)
        self.assertEqual(len(self.lista.filtro_interesses.all()),1)
        self.assertTrue(self.lista.filtro_interesses.filter(id=self.interesse1.id).exists())
        
    def test_editar_lista_usuario_nao_autenticado(self):
        data = {
            'titulo': 'Lista Editada',
            'filtro_habilidades': [self.habilidade1.id],
            'filtro_experiencias': [self.experiencia1.id],
            'filtro_interesses': [self.interesse1.id],
            'filtro_disciplinas': [{"disciplina": "Matemática", "nota": 9}],
            'filtro_cra': 8.0
        }
        response = self.client.put(self.url_editar, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_editar_lista_dono_nao_encontrado(self):
        self.client.force_authenticate(user=self.professor_usuario)
        self.lista.delete() 
        data = {
            'titulo': 'Lista Editada',
            'filtro_habilidades': [self.habilidade1.id],
            'filtro_experiencias': [self.experiencia1.id],
            'filtro_interesses': [self.interesse1.id],
            'filtro_disciplinas': [{"disciplina": "Matemática", "nota": 9}],
            'filtro_cra': 8.0
        }
        response = self.client.put(self.url_editar, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_editar_lista_acesso_negado(self):
        outro_usuario = User.objects.create_user(
            username='outro_professor@example.com',
            email='outro_professor@example.com',
            password='senhaSegura'
        )
        outro_professor = Professor.objects.create(
            nome='Outro Professor',
            email='outro_professor@example.com',
            user=outro_usuario
        )

        self.client.force_authenticate(user=outro_usuario)
        data = {
            'titulo': 'Lista Editada',
            'filtro_habilidades': [self.habilidade1.id],
            'filtro_experiencias': [self.experiencia1.id],
            'filtro_interesses': [self.interesse1.id],
            'filtro_disciplinas': [{"disciplina": "Matemática", "nota": 9}],
            'filtro_cra': 8.0
        }
        response = self.client.put(self.url_editar, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)