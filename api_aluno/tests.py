from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from api_aluno.views import *
from api_aluno.models import Aluno, Historico_Academico, Disciplina_Matriculada
from api_professor.models import Professor
from api_projeto.models import Projeto
from api_rest.models import *

import os


class AlunoModelTestCase(TestCase):

    def setUp(self):
        self.usuario = User.objects.create_user(
            username='andre@example.com',
            email='andre@example.com',
            password='1234'
        )
        self.aluno = Aluno.objects.create(
            matricula='121210210',
            nome='Andre Souza',
            email='andre@example.com',
            user=self.usuario
        )

    def test_aluno_creation(self):
        self.assertEqual(self.aluno.matricula, '121210210')
        self.assertEqual(self.aluno.nome, 'Andre Souza')
        self.assertEqual(self.aluno.email, 'andre@example.com')
        self.assertTrue(self.aluno.user.check_password('1234'))
        self.assertIsInstance(self.aluno, Aluno)

    def test_aluno_str(self):
        expected_str = (
            'matricula: 121210210\n'
            'nome: Andre Souza\n'
            'email: andre@example.com\n'
            'curriculo: None\n'
            'github: None\n'
            'linkedin: None'
        )
        self.assertEqual(str(self.aluno), expected_str)


class CriarAlunoViewTestCase(APITestCase):
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
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_criar_aluno_com_email_vazio(self):
        invalid_data = {
            "matricula": '121210410',
            "nome": "Gabriel Souza",
            "senha": "senha123"
        }
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_criar_aluno_com_senha_vazia(self):
        invalid_data = {
            "matricula": '121210410',
            "nome": "Gabriel Souza",
            "email": "joao.silva@example.com"
        }
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('senha', response.data)


class getAllAlunoViewTestCase(APITestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('get_all_alunos')
        usuarios = [
            User.objects.create_user(username='andre@example.com', email='andre@example.com', password='213'),
            User.objects.create_user(username='rian@example.com', email='rian@example.com', password='213'),
            User.objects.create_user(username='luana@example.com', email='luana@example.com', password='213')
        ]
        alunos = [
            Aluno.objects.create(matricula="121210110", nome="Andre", email="andre@example.com", user=usuarios[0]),
            Aluno.objects.create(matricula="121210210", nome="Rian", email="rian@example.com", user=usuarios[1]),
            Aluno.objects.create(matricula="121210310", nome="Luana", email="luana@example.com", user=usuarios[2])
        ]
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
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        

class getAlunoPorMatriculaTestCase(APITestCase):

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

    def test_get_aluno_by_matricula_sucesso1(self):
        url = reverse('get_by_matricula_aluno', kwargs={'matricula': self.aluno1.matricula})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nome'], self.aluno1.nome)
        self.assertEqual(response.data['email'], self.aluno1.email)
        
        
    def test_get_aluno_by_matricula_sucesso2(self):
        url = reverse('get_by_matricula_aluno', kwargs={'matricula': self.aluno1.matricula})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['matricula'], self.aluno1.matricula)

    def test_get_aluno_by_matricula_inexistente(self):
        url = reverse('get_by_matricula_aluno', kwargs={'matricula': 999999999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UploadHistoricoAcademicoViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.usuario = User.objects.create_user(
            username='joao.silva@example.com',
            email='joao.silva@example.com',
            password='senhaSegura'
        )
        self.aluno = Aluno.objects.create(
            matricula="123456789",
            nome="João da Silva",
            email="joao.silva@example.com",
            curriculo="Link do curriculo",
            github="https://github.com/joaosilva",
            linkedin="https://linkedin.com/in/joaosilva",
            user=self.usuario
        )
        self.url_upload = reverse('upload_historico')
        refresh = RefreshToken.for_user(self.usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        self.pdf_path = os.path.join(os.path.dirname(__file__), 'test_data', 'historico.pdf')

        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError(f"O arquivo PDF não foi encontrado em {self.pdf_path}")
        

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
                data={'historico_pdf': SimpleUploadedFile('historico.pdf', pdf_file.read())},
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
        user = User.objects.create_user(
            username='marco.silva@example.com',
            email='marco.silva@example.com',
            password='senhaSegura'
        )
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        with open(self.pdf_path, 'rb') as pdf_file:
            response = self.client.post(
                self.url_upload,
                data={'historico_pdf': SimpleUploadedFile('historico.pdf', pdf_file.read())},
                format='multipart'
            )
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_upload_pdf_vazio(self):
        empty_pdf = SimpleUploadedFile('historico.pdf', b'')
        response = self.client.post(
            self.url_upload,
            data={'historico_pdf': empty_pdf},
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

    def test_upload_historico_sendo_professor(self):
        professor_usuario = User.objects.create_user(
            username='professor@universidade.com',
            email='professor@universidade.com',
            password='senhaSegura'
        )
        refresh = RefreshToken.for_user(professor_usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        with open(self.pdf_path, 'rb') as pdf_file:
            response = self.client.post(
                self.url_upload,
                data={'historico_pdf': SimpleUploadedFile('historico.pdf', pdf_file.read())},
                format='multipart'
            )
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual("Acesso negado. Apenas alunos podem cadastrar históricos.", response.data['detail'])
        
    def test_upload_historico_com_token_tipo_errado(self):
        refresh = RefreshToken.for_user(self.usuario)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh}')        
        response = self.client.get(self.url_upload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['code'], "token_not_valid")
        self.assertEqual(response.data['messages'][0]['message'], "Token tem tipo errado")


class VisualizarHistoricoAcademicoViewTestCase(APITestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(
            username='joao.silva@example.com',
            email='joao.silva@example.com',
            password='senhaSegura'
        )
        self.aluno = Aluno.objects.create(
            matricula="123456789",
            nome="João da Silva",
            email="joao.silva@example.com",
            curriculo="Link do curriculo",
            github="https://github.com/joaosilva",
            linkedin="https://linkedin.com/in/joaosilva",
            user=self.usuario
        )
        self.url_upload = reverse('upload_historico')
        self.pdf_path = os.path.join(os.path.dirname(__file__), 'test_data', 'historico.pdf')

        if not os.path.exists(self.pdf_path):
            raise FileNotFoundError(f"O arquivo PDF não foi encontrado em {self.pdf_path}")

        self.url_visualizar = reverse('visualizar_historico', kwargs={'matricula': self.aluno.matricula})

    def test_upload_historico(self):
        self.client.force_authenticate(user=self.usuario)
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
        
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
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

class AlunoUpdateTests(APITestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(
            username='joao.silva@example.com',
            email='joao.silva@example.com',
            password='senhaSegura'
        )  
        self.aluno = Aluno.objects.create(
            matricula="123456789",
            nome="João da Silva",
            email="joao.silva@example.com",
            curriculo="Link do curriculo",
            github="https://github.com/joaosilva",
            linkedin="https://linkedin.com/in/joaosilva",
            user=self.usuario
        )
        self.url_editar = reverse('editar_perfil_aluno')
        self.client.force_authenticate(user=self.usuario)

        self.habilidade = Habilidade.objects.create(nome='Programação', grupo='Hard Skills')
        self.experiencia = Experiencia.objects.create(nome='Gestão de Projetos', grupo='Experiências')
        self.interesse = Interesse.objects.create(nome='Inteligência Artificial', grupo='Interesses')
        self.habilidade_nova1 = Habilidade.objects.create(nome='Banco de Dados', grupo='Hard Skills')
        self.habilidade_nova2 = Habilidade.objects.create(nome='Proatividade', grupo='Soft Skills')
        self.experiencia_nova1 = Experiencia.objects.create(nome='Migração de Sistemas', grupo='Experiências')
        self.experiencia_nova2 = Experiencia.objects.create(nome='APIs', grupo='Experiências')
        self.interesse_novo1 = Interesse.objects.create(nome='Cybersegurança', grupo='Interesses')
        self.interesse_novo2 = Interesse.objects.create(nome='Análise de Dados', grupo='Interesses')

        self.aluno.habilidades.add(self.habilidade)
        self.aluno.experiencias.add(self.experiencia)
        self.aluno.interesses.add(self.interesse)

        self.data = {
            'nome': 'Novo Nome', 
            'curriculo': 'Novo Currículo', 
            'email': 'newtestuser@example.com',
            'github': 'https://github.com/new', 
            'linkedin': 'https://linkedin.com/in/new', 
            'habilidades': [self.habilidade_nova1.id, 
                            self.habilidade_nova2.id], 
            'experiencias': [self.experiencia_nova1.id, 
                             self.experiencia_nova2.id], 
            'interesses': [self.interesse_novo1.id,
                           self.interesse_novo2.id]        
            }
        
    def test_editar_aluno_todas_as_informacoes(self):
        nome_antigo = self.aluno.nome
        email_antigo = self.aluno.email
        curriculo_antigo = self.aluno.curriculo
        github_antigo = self.aluno.github
        linkedin_antigo = self.aluno.linkedin

        habilidades_antigas = list(self.aluno.habilidades.all())
        experiencias_antigas = list(self.aluno.experiencias.all())
        interesses_antigos = list(self.aluno.interesses.all())

        response = self.client.put(self.url_editar, self.data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.aluno.refresh_from_db()

        self.assertNotEqual(self.aluno.nome, nome_antigo)
        self.assertNotEqual(self.aluno.email, email_antigo)
        self.assertNotEqual(self.aluno.curriculo, curriculo_antigo)
        self.assertNotEqual(self.aluno.github, github_antigo)
        self.assertNotEqual(self.aluno.linkedin, linkedin_antigo)

        self.assertEqual(self.aluno.nome, 'Novo Nome')
        self.assertEqual(self.aluno.email, 'newtestuser@example.com')
        self.assertEqual(self.aluno.curriculo, 'Novo Currículo')
        self.assertEqual(self.aluno.github, 'https://github.com/new')
        self.assertEqual(self.aluno.linkedin, 'https://linkedin.com/in/new')

        habilidades_novas = list(self.aluno.habilidades.all())
        experiencias_novas = list(self.aluno.experiencias.all())
        interesses_novos = list(self.aluno.interesses.all())

        self.assertNotEqual(habilidades_novas, habilidades_antigas)
        self.assertNotEqual(experiencias_novas, experiencias_antigas)
        self.assertNotEqual(interesses_novos, interesses_antigos)
    
    def test_editar_aluno_informacoes_especificas(self):
        nome_antigo = self.aluno.nome
        email_antigo = self.aluno.email
        curriculo_antigo = self.aluno.curriculo
        github_antigo = self.aluno.github
        linkedin_antigo = self.aluno.linkedin

        habilidades_antigas = list(self.aluno.habilidades.all())
        experiencias_antigas = list(self.aluno.experiencias.all())
        interesses_antigos = list(self.aluno.interesses.all())

        self.data['nome'] = self.aluno.nome
        self.data['email'] = self.aluno.email
        self.data['habilidades'] = [self.habilidade.id] 
        self.data['experiencias'] = [self.experiencia.id] 

        response = self.client.put(self.url_editar, self.data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.aluno.refresh_from_db()

        self.assertEqual(self.aluno.nome, nome_antigo)
        self.assertEqual(self.aluno.email, email_antigo)
        self.assertNotEqual(self.aluno.curriculo, curriculo_antigo)
        self.assertNotEqual(self.aluno.github, github_antigo)
        self.assertNotEqual(self.aluno.linkedin, linkedin_antigo)

        self.assertEqual(self.aluno.nome, 'João da Silva')
        self.assertEqual(self.aluno.email, 'joao.silva@example.com')
        self.assertEqual(self.aluno.curriculo, 'Novo Currículo')
        self.assertEqual(self.aluno.github, 'https://github.com/new')
        self.assertEqual(self.aluno.linkedin, 'https://linkedin.com/in/new')
        
        habilidades_novas = list(self.aluno.habilidades.all())
        experiencias_novas = list(self.aluno.experiencias.all())
        interesses_novos = list(self.aluno.interesses.all())

        self.assertEqual(habilidades_novas, habilidades_antigas)
        self.assertEqual(experiencias_novas, experiencias_antigas)
        self.assertNotEqual(interesses_novos, interesses_antigos)

    def test_editar_aluno_nao_existe(self):
        outro_usuario = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='senhaSegura'
        )
        self.client.force_authenticate(user=outro_usuario)
        self.aluno.delete()

        response = self.client.put(self.url_editar, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class AlunoVisualizarPerfilTests(APITestCase):
    def setUp(self):
        self.aluno_usuario = User.objects.create_user(
            username='joao.silva@example.com',
            email='joao.silva@example.com',
            password='senhaSegura'
        )
        self.aluno = Aluno.objects.create(
            matricula="123456789",
            nome="João da Silva",
            email="joao.silva@example.com",
            curriculo="Link do curriculo",
            github="https://github.com/joaosilva",
            linkedin="https://linkedin.com/in/joaosilva",
            user=self.aluno_usuario
        )

        self.habilidade = Habilidade.objects.create(nome='Programação', grupo='Hard Skills')
        self.experiencia = Experiencia.objects.create(nome='Gestão de Projetos', grupo='Experiências')
        self.interesse = Interesse.objects.create(nome='Inteligência Artificial', grupo='Interesses')
        self.habilidade2 = Habilidade.objects.create(nome='Proatividade', grupo='Soft Skills')

        self.aluno.habilidades.add(self.habilidade)
        self.aluno.experiencias.add(self.experiencia)
        self.aluno.interesses.add(self.interesse)
        self.aluno.habilidades.add(self.habilidade2)

        self.feedback = Feedback.objects.create(nome="Criativo", grupo="Feedbacks")

        self.professor_usuario = User.objects.create_user(
            username='professor@universidade.com',
            email='professor@universidade.com',
            password='senhaSegura'
        )
        self.professor = Professor.objects.create(
            user=self.professor_usuario,
            nome='Professor',
            email='professor@universidade.com'
        )
        self.avaliacao = Avaliacao.objects.create(
            id_professor=self.professor,
            id_aluno=self.aluno,
            comentario='Bom aluno.'
        )
        self.avaliacao.tags.add(self.feedback)

        self.data_aluno = {
            'matricula': '123456789',
            'nome': 'João da Silva',
            'email': 'joao.silva@example.com',
            'curriculo': 'Link do curriculo', 
            'github': 'https://github.com/joaosilva', 
            'linkedin': 'https://linkedin.com/in/joaosilva',
            'user': self.aluno.user,
            'habilidades': ['Programação', 'Proatividade'], 
            'experiencias': ['Gestão de Projetos'], 
            'interesses': ['Inteligência Artificial'],
        }

        self.data_professor = {
            'matricula': '123456789',
            'nome': 'João da Silva', 
            'email': 'joao.silva@example.com',
            'curriculo': 'Link do curriculo', 
            'github': 'https://github.com/joaosilva', 
            'linkedin': 'https://linkedin.com/in/joaosilva',
            'user': self.aluno.user,
            'habilidades': ['Programação', 'Proatividade'], 
            'experiencias': ['Gestão de Projetos'], 
            'interesses': ['Inteligência Artificial'],
            'avaliacao': [{'id_professor': self.professor.id, 'id_aluno': self.aluno.matricula, 
            'comentario': 'Bom aluno.', 'tags': [{'nome': 'Criativo', 'grupo': 'Feedbacks'}]}]
        }

        self.url_visualizar = reverse('visualizar_perfil_aluno', kwargs={'matricula': self.aluno.matricula})

    def test_visualizar_perfil_aluno_como_proprio_aluno(self):
        self.client.force_authenticate(user=self.aluno_usuario)
        response = self.client.get(self.url_visualizar)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_data = response.data
        self.assertEqual(response_data['matricula'], '123456789')
        self.assertEqual(response_data['nome'], 'João da Silva')
        self.assertEqual(response_data['email'], 'joao.silva@example.com')
        self.assertEqual(response_data['curriculo'], 'Link do curriculo')
        self.assertEqual(response_data['github'], 'https://github.com/joaosilva')
        self.assertEqual(response_data['linkedin'], 'https://linkedin.com/in/joaosilva')
        self.assertEqual(self.habilidade.id, response_data['habilidades'][0]['id'])
        self.assertEqual(self.habilidade2.id, response_data['habilidades'][1]['id'])
        self.assertEqual(self.experiencia.id, response_data['experiencias'][0]['id'])
        self.assertEqual(self.interesse.id, response_data['interesses'][0]['id'])
        self.assertNotIn('avaliacao', response_data)


    def test_visualizar_perfil_aluno_como_professor(self):
        self.client.force_authenticate(user=self.professor_usuario)
        response = self.client.get(self.url_visualizar)

        response_data = response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_data['matricula'], '123456789')
        self.assertEqual(response_data['nome'], 'João da Silva')
        self.assertEqual(response_data['email'], 'joao.silva@example.com')
        self.assertEqual(response_data['curriculo'], 'Link do curriculo')
        self.assertEqual(response_data['github'], 'https://github.com/joaosilva')
        self.assertEqual(response_data['linkedin'], 'https://linkedin.com/in/joaosilva')
        self.assertEqual(self.habilidade.id, response_data['habilidades'][0]['id'])
        self.assertEqual(self.habilidade2.id, response_data['habilidades'][1]['id'])
        self.assertEqual(self.experiencia.id, response_data['experiencias'][0]['id'])
        self.assertEqual(self.interesse.id, response_data['interesses'][0]['id'])
        self.assertEqual(response_data['avaliacao'], [{'id_professor': 2, 'id_aluno': '123456789', 'comentario': 'Bom aluno.', 'tags': [{'grupo': self.feedback.grupo, 'id': self.feedback.id, 'nome': self.feedback.nome}]}])

    def test_visualizar_perfil_aluno_como_outro_aluno(self):
        outro_usuario = User.objects.create_user(
            username='outro.aluno@example.com',
            email='outro.aluno@example.com',
            password='senhaSegura'
        )
        Aluno.objects.create(
            matricula="987654321",
            nome="Outro Aluno",
            email="outro.aluno@example.com",
            user=outro_usuario
        )
        self.client.force_authenticate(user=outro_usuario)
        response = self.client.get(self.url_visualizar)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_visualizar_perfil_aluno_nao_existe(self):
        url = reverse('visualizar_perfil_aluno', kwargs={'matricula': '999999999'})
        self.client.force_authenticate(user=self.aluno_usuario)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)