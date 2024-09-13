from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from api_aluno.views import *
from api_aluno.models import Aluno, Historico_Academico, Disciplina_Matriculada
from api_professor.models import Professor

from api_projeto.models import Projeto

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
        cls.usuario = User.objects.create_user(
            username='joao.silva@example.com',
            email='joao.silva@example.com',
            password='senhaSegura'
        )
        cls.aluno = Aluno.objects.create(
            matricula="123456789",
            nome="João da Silva",
            email="joao.silva@example.com",
            curriculo="Link do curriculo",
            github="https://github.com/joaosilva",
            linkedin="https://linkedin.com/in/joaosilva",
            cra=9.3,
            user=cls.usuario
        )
        cls.url_upload = reverse('upload_historico')
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
            historico = Historico_Academico.objects.get(aluno=self.aluno)
            self.assertIsNotNone(historico)
            self.assertTrue(os.path.isfile(historico.historico_pdf.path))
            self.assertIsNotNone(historico.cra)
            disciplinas_matriculadas = Disciplina_Matriculada.objects.filter(historico=historico)
            self.assertGreater(len(disciplinas_matriculadas), 0)

    def test_upload_novo_historico_apaga_antigo(self):
        with open(self.pdf_path, 'rb') as pdf_file:
            response = self.client.post(
                self.url_upload,
                data={'aluno': self.aluno.matricula, 'historico_pdf': SimpleUploadedFile('historico.pdf', pdf_file.read())},
                format='multipart'
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        historico = Historico_Academico.objects.get(aluno=self.aluno)
        caminho_pdf_antigo = historico.historico_pdf.path
        disciplinas_anteriores = Disciplina_Matriculada.objects.filter(historico=historico)
        self.assertTrue(os.path.isfile(caminho_pdf_antigo))
        self.assertGreater(len(disciplinas_anteriores), 0)

        with open(self.pdf_path, 'rb') as novo_pdf_file:
            response = self.client.post(
                self.url_upload,
                data={'aluno': self.aluno.matricula, 'historico_pdf': SimpleUploadedFile('historico_novo.pdf', novo_pdf_file.read())},
                format='multipart'
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertFalse(os.path.isfile(caminho_pdf_antigo))
        historico_atualizado = Historico_Academico.objects.get(aluno=self.aluno)
        caminho_pdf_novo = historico_atualizado.historico_pdf.path
        self.assertTrue(os.path.isfile(caminho_pdf_novo))
        disciplinas_novas = Disciplina_Matriculada.objects.filter(historico=historico_atualizado)
        self.assertNotEqual(list(disciplinas_anteriores), list(disciplinas_novas))

    def test_upload_historico_aluno_nao_existe(self):
        with open(self.pdf_path, 'rb') as pdf_file:
            response = self.client.post(
                self.url_upload,
                data={'aluno': '999999999', 'historico_pdf': SimpleUploadedFile('historico.pdf', pdf_file.read())},
                format='multipart'
            )
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_upload_pdf_vazio(self):
        empty_pdf = SimpleUploadedFile('historico.pdf', b'')
        response = self.client.post(
            self.url_upload,
            data={'aluno': self.aluno.matricula, 'historico_pdf': empty_pdf},
            format='multipart'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_historico_removes_pdf(self):
        self.test_upload_historico()
        historico = Historico_Academico.objects.get(aluno=self.aluno)
        pdf_file_path = historico.historico_pdf.path
        self.assertTrue(os.path.isfile(pdf_file_path))
        historico.delete()
        self.assertFalse(os.path.isfile(pdf_file_path))
        self.assertEqual(Historico_Academico.objects.filter(aluno=self.aluno).count(), 0)
        self.assertEqual(Disciplina_Matriculada.objects.filter(historico__aluno=self.aluno).count(), 0)

    def test_visualizar_historico_com_aluno(self):
        self.client.force_authenticate(user=self.usuario)
        self.test_upload_historico()
        response = self.client.get(self.url_visualizar)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('Content-Disposition', response)
        historico = Historico_Academico.objects.get(aluno=self.aluno)
        historico.delete()

    def test_visualizar_historico_com_professor(self):
        professor_usuario = User.objects.create_user(
            username='professor@universidade.com',
            email='professor@universidade.com',
            password='senhaSegura'
        )
        Professor.objects.create(
            user=professor_usuario,
            nome='Professor',
            email='professor@universidade.com'
        )
        self.test_upload_historico()

        self.client.force_authenticate(user=professor_usuario)
        response = self.client.get(self.url_visualizar)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('Content-Disposition', response)
        historico = Historico_Academico.objects.get(aluno=self.aluno)
        historico.delete()

    def test_visualizar_historico_outro_aluno(self):
        outro_usuario = User.objects.create_user(
            username='outro.aluno@example.com',
            email='outro.aluno@example.com',
            password='senhaSegura'
        )
        Aluno.objects.create(
            matricula="987654321",
            nome="Outro Aluno",
            email="outro.aluno@example.com",
            curriculo="Link do curriculo",
            github="https://github.com/outroaluno",
            linkedin="https://linkedin.com/in/outroaluno",
            cra=8.5,
            user=outro_usuario
        )
        self.client.force_authenticate(user=outro_usuario)
        response = self.client.get(self.url_visualizar)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_visualizar_historico_aluno_nao_existe(self):
        url = reverse('visualizar_historico', kwargs={'matricula': '999999999'})
        self.client.force_authenticate(user=self.usuario)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_visualizar_historico_sem_historico(self):
        Historico_Academico.objects.filter(aluno=self.aluno).delete()
        self.client.force_authenticate(user=self.usuario)
        response = self.client.get(self.url_visualizar)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_verificar_dados_processados(self):
        self.test_upload_historico()
        historico = Historico_Academico.objects.get(aluno=self.aluno)

        self.assertIsNotNone(historico.cra)

        disciplinas_matriculadas = Disciplina_Matriculada.objects.filter(historico=historico)
        self.assertGreater(len(disciplinas_matriculadas), 0)

        
class InteresseNoProjetoTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='aluno@teste.com', password='senha123')
        self.aluno = Aluno.objects.create(user=self.user, matricula='123456789', nome='Aluno Teste', email='aluno@teste.com')
        self.userP = User.objects.create_user(username='professor@teste.com', password='senha123')
        self.professor = Professor.objects.create(user=self.userP, nome='Professor Teste', email='professor@teste.com')

        self.projeto = Projeto.objects.create(nome='Projeto Teste', data_de_criacao=timezone.now(), responsavel=self.professor)

        self.url = reverse('interessar_no_projeto', args=[self.projeto.id_projeto])
        self.client.force_authenticate(user=self.user)  

    def test_interesse_no_projeto_sucesso(self):
        response = self.client.post(self.url, {'projeto_id': self.projeto.id_projeto}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Associacao.objects.count(), 1)
        self.assertEqual(Associacao.objects.first().aluno, self.aluno)
        self.assertEqual(Associacao.objects.first().projeto, self.projeto)
        
    def test_interesse_no_projeto_projeto_nao_existe(self):
        url = reverse('interessar_no_projeto', args=[9999]) 
        response = self.client.post(url, {'projeto_id': 9999}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'Projeto não encontrado.')
        self.assertEqual(Associacao.objects.count(), 0)
    
    def test_interesse_no_projeto_associacao_ja_existe(self):
        Associacao.objects.create(aluno=self.aluno, projeto=self.projeto)
        
        url = reverse('interessar_no_projeto', args=[self.projeto.id_projeto])
        response = self.client.post(url, {'projeto_id': self.projeto.id_projeto}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Aluno já está associado a este projeto.')
        self.assertEqual(Associacao.objects.count(), 1) 
        
    def test_interesse_no_projeto_aluno_negado(self):
        self.client.force_authenticate(user=self.professor.user)
    
        url = reverse('interessar_no_projeto', args=[self.projeto.id_projeto])
        response = self.client.post(url, {'projeto_id': self.projeto.id_projeto}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'Acesso negado. Apenas alunos podem se associar a projetos.')
        self.assertEqual(Associacao.objects.count(), 0)
    
    def test_associacao_deletada_quando_aluno_e_deletado(self):
        Associacao.objects.create(aluno=self.aluno, projeto=self.projeto)

        self.assertEqual(Associacao.objects.count(), 1)
        
        self.aluno.delete()

        self.assertEqual(Associacao.objects.count(), 0)

    def test_associacao_deletada_quando_projeto_e_deletado(self):
        Associacao.objects.create(aluno=self.aluno, projeto=self.projeto)

        self.assertEqual(Associacao.objects.count(), 1)
        
        self.projeto.delete()

        self.assertEqual(Associacao.objects.count(), 0)
        
class DeleteInteressarNoProjetoTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='beatriz@teste.com', password='senha123')
        self.aluno = Aluno.objects.create(user=self.user, matricula='987654321', nome='Beatriz', email='beatriz@teste.com')
        self.userP = User.objects.create_user(username='joseane@teste.com', password='senha123')
        self.professor = Professor.objects.create(user=self.userP, nome='Joseane', email='joseane@teste.com')

        self.projeto = Projeto.objects.create(nome='Projeto Teste', data_de_criacao=timezone.now(), responsavel=self.professor)

        self.associacao = Associacao.objects.create(aluno=self.aluno, projeto=self.projeto)

        self.url = reverse('retirar_interesse_no_projeto', args=[self.projeto.id_projeto])
        self.client.force_authenticate(user=self.user)

    def test_delete_interesse_no_projeto_sucesso(self):
        response = self.client.delete(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Associação deletada com sucesso.')
        self.assertEqual(Associacao.objects.count(), 0)

    def test_delete_interesse_no_projeto_projeto_nao_existe(self):
        url = reverse('retirar_interesse_no_projeto', args=[9999])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'Projeto não encontrado.')
        self.assertEqual(Associacao.objects.count(), 1)

    def test_delete_interesse_no_projeto_associacao_nao_existe(self):
        Associacao.objects.filter(aluno=self.aluno, projeto=self.projeto).delete()
        
        response = self.client.delete(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Aluno não está associado a este projeto.')
        self.assertEqual(Associacao.objects.count(), 0)

    def test_delete_interesse_no_projeto_aluno_negado(self):
        self.client.force_authenticate(user=self.professor.user)
    
        response = self.client.delete(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'Acesso negado. Apenas alunos podem se associar a projetos.')
        self.assertEqual(Associacao.objects.count(), 1)
