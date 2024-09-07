from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from api_aluno.views import *
from api_aluno.models import Aluno, HistoricoAcademico, Disciplina

import os


#Models
# Testando model de ALuno.
class AlunoModelTest(TestCase):

    def setUp(self):
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

    def test_aluno_creation(self):
        #Asserts
        self.assertIsInstance(self.aluno, Aluno)
        self.assertEqual(self.aluno.matricula, '121210210')
        self.assertEqual(self.aluno.nome, 'Andre Souza')
        self.assertEqual(self.aluno.email, 'andre@example.com')
        self.assertTrue(self.aluno.user.check_password('1234'))

    def test_aluno_str(self):
        expected_str = (f'matricula: 121210210\n'
                        f'nome: Andre Souza\n'
                        f'email: andre@example.com\n'
                        f'curriculo: None\n'
                        f'github: None\n'
                        f'linkedin: None\n'
                        f'cra: None')
                
        #Asserts
        self.assertEqual(str(self.aluno), expected_str)

#Views
# Testando POST de alunoes
class CriarAlunoViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('criar_aluno')
        self.aluno_data = {
            "matricula": '121210210',
            "nome": "João da Silva",
            "email": "joao.silva@example.com",
            "senha": "senha123"
        }

    def test_criar_aluno_sucesso(self):
        response = self.client.post(self.url, self.aluno_data, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['matricula'], self.aluno_data['matricula'])
        self.assertEqual(response.data['nome'], self.aluno_data['nome'])
        self.assertEqual(response.data['email'], self.aluno_data['email'])

    def test_criar_aluno_com_nome_vazio(self):
        invalid_data = {
            "matricula": '121210110',
            "email": "vazio@example.com",
            "senha": "senha123"
        }
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertIn('nome', response.data)
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('nome', response.data)

    def test_criar_aluno_com_matricula_vazia(self):
        invalid_data = {
            "matricula": '',
            "nome": "Gabriel Souza",
            "email": "vazio@example.com",
            "senha": "senha123"
        }
        response = self.client.post(self.url, invalid_data, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('matricula', response.data)
        
    def test_criar_aluno_com_matricula_repetida(self):
        self.client.post(self.url, self.aluno_data, format='json')
        invalid_data = {
            "matricula": '121210210',
            "nome": "Gabriel Souza",
            "email": "vazio@example.com",
            "senha": "senha123"
        }
        response = self.client.post(self.url, invalid_data, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        
    def test_criar_aluno_com_email_repetido(self):
        self.client.post(self.url, self.aluno_data, format='json')
        invalid_data = {
            "matricula": '121210310',
            "nome": "Gabriel Souza",
            "email": "joao.silva@example.com",
            "senha": "senha123"
        }
        response = self.client.post(self.url, invalid_data, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_criar_aluno_com_email_vazio(self):
        invalid_data = {
            "matricula": '121210410',
            "nome": "Gabriel Souza",
            "senha": "senha123"
        }
        response = self.client.post(self.url, invalid_data, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_criar_aluno_com_senha_vazia(self):
        invalid_data = {
            "matricula": '121210410',
            "nome": "Gabriel Souza",
            "email": "joao.silva@example.com"
        }
        response = self.client.post(self.url, invalid_data, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('senha', response.data)

# Testando GET de todos os alunos.
class getAllAlunoViewTest(APITestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('get_all_alunos')
        usuario = User.objects.create_user(
            username='andre@example.com',
            email='andre@example.com',
            password='213'
        )        
        Aluno.objects.create(matricula = "121210110", nome="Andre", email="andre@example.com", user=usuario)
        usuario = User.objects.create_user(
            username='rian@example.com',
            email='rian@example.com',
            password='213'
        )
        Aluno.objects.create(matricula = "121210210", nome="Rian", email="rian@example.com", user=usuario)
        usuario = User.objects.create_user(
            username='luana@example.com',
            email='luana@example.com',
            password='213'
        )
        Aluno.objects.create(matricula = "121210310", nome="Luana", email="luana@example.com", user=usuario)
        
    def test_get_all_alunos_sucesso(self):
        response = self.client.get(self.url, format='json')
        nomes_alunos = [aluno['nome'] for aluno in response.data]
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
        self.assertIn("Andre", nomes_alunos)
        self.assertIn("Rian", nomes_alunos)
        self.assertIn("Luana", nomes_alunos)
        
    def test_get_all_alunos_vazio(self):
        Aluno.objects.all().delete()
        
        response = self.client.get(self.url, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        
# Testando GET de pegar Aluno por matricula.
class getAlunoPorMatriculaTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        usuario = User.objects.create_user(
            username='andre@example.com',
            email='andre@example.com',
            password='213'
        )
        self.aluno1 = Aluno.objects.create(matricula = "121210110", nome="Andre", email="andre@example.com", user=usuario)
        usuario = User.objects.create_user(
            username='rian@example.com',
            email='rian@example.com',
            password='213'
        )
        self.aluno2 = Aluno.objects.create(matricula = "121210210", nome="Rian", email="rian@example.com", user=usuario)

    def test_get_Aluno_by_matricula_sucesso1(self):
        url = reverse('get_by_matricula_aluno', kwargs={'matricula': self.aluno1.matricula})
        response = self.client.get(url)
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome'], self.aluno1.nome)
        self.assertEqual(response.data['email'], self.aluno1.email)
        
        
    def test_get_Aluno_by_matricula_sucesso2(self):
        url = reverse('get_by_matricula_aluno', kwargs={'matricula': self.aluno1.matricula})
        response = self.client.get(url)
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['matricula'], self.aluno1.matricula)

    def test_get_Aluno_by_matricula_inexistente(self):
        url = reverse('get_by_matricula_aluno', kwargs={'matricula': 999999999})
        response = self.client.get(url)
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class HistoricoAcademicoTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.aluno = Aluno.objects.create(
            matricula="123456789",
            nome="João da Silva",
            email="joao.silva@example.com",
            curriculo="Link do curriculo",
            github="https://github.com/joaosilva",
            linkedin="https://linkedin.com/in/joaosilva",
            cra=9.3,
            senha="senhaSegura"
        )
        cls.url_upload = reverse('upload_historico')

        # Caminho para o PDF de teste
        cls.pdf_path = os.path.join(os.path.dirname(__file__), 'test_data', 'historico.pdf')

        if not os.path.exists(cls.pdf_path):
            raise FileNotFoundError(f"O arquivo PDF não foi encontrado em {cls.pdf_path}")

        cls.url_visualizar = reverse('visualizar_historico', kwargs={'matricula': cls.aluno.matricula})

    def test_upload_historico(self):
        with open(self.pdf_path, 'rb') as pdf_file:
            response = self.client.post(
                self.url_upload,
                data={'aluno': self.aluno.matricula, 'historico_pdf': SimpleUploadedFile('historico.pdf', pdf_file.read())},
                format='multipart'
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            historico = HistoricoAcademico.objects.filter(aluno=self.aluno).first()
            self.assertIsNotNone(historico)

            disciplinas = Disciplina.objects.filter(historico=historico)
            self.assertGreater(len(disciplinas), 0)

    def test_visualizar_historico(self):
        self.test_upload_historico()
        response = self.client.get(self.url_visualizar)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_visualizar_historico_aluno_nao_existe(self):
        url = reverse('visualizar_historico', kwargs={'matricula': '999999999'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_visualizar_historico_sem_historico(self):
        response = self.client.get(self.url_visualizar)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_verificar_dados_processados(self):
        self.test_upload_historico()
        historico = HistoricoAcademico.objects.get(aluno=self.aluno)

        self.assertIsNotNone(historico.cra)
        print(f"CRA: {historico.cra}")

        disciplinas = Disciplina.objects.filter(historico=historico)
        self.assertGreater(len(disciplinas), 0)
        for disciplina in disciplinas:
            print(
                f"Código: {disciplina.codigo} - Disciplina: {disciplina.nome} - Professor(es): {disciplina.professor} - Tipo: {disciplina.tipo} - Créditos: {disciplina.creditos} -"
                f" Carga Horária: {disciplina.carga_horaria} - Média: {disciplina.media} - Situação: {disciplina.situacao} - Período: {disciplina.periodo}")
