from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from api_aluno.views import *
from api_aluno.models import Aluno, HistoricoAcademico, Disciplina
from api_professor.models import Professor
from api_projeto.models import Projeto
from api_rest.models import *

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
        usuario = User.objects.create_user(
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
            user=usuario
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

        disciplinas = Disciplina.objects.filter(historico=historico)
        self.assertGreater(len(disciplinas), 0)
       
        
class LoginAlunoViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('login_aluno')
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
        self.login = {
            "email" : "andre@example.com",
            "senha" : "1234"
        }

    def test_login_aluno_sucesso(self):
        response = self.client.post(self.url, self.login, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)
        self.assertNotEqual(response.data['refresh'], '')
        self.assertNotEqual(response.data['access'], '')
        
    def test_login_aluno_com_email_vazio(self):
        invalid_data = {
            "email": "",
            "senha": "1234"
        }
        response = self.client.post(self.url, invalid_data, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('detail', response.data)
        self.assertEqual('Aluno não encontrado.', response.data['detail'])

    def test_login_aluno_com_senha_vazia(self):
        invalid_data = {
            "email": "andre@example.com",
            "senha": ""
        }
        response = self.client.post(self.url, invalid_data, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
        self.assertEqual('Senha incorreta.', response.data['detail'])

        
    def test_login_aluno_inexistente(self):
        invalid_data = {
            "email": "joao.silva@example.com",
            "senha": "senha123"
        }
        response = self.client.post(self.url, invalid_data, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('detail', response.data)
        self.assertEqual('Aluno não encontrado.', response.data['detail'])
        
    def test_login_aluno_senha_incorreta(self):
        invalid_data = {
            "email": "andre@example.com",
            "senha": "12345"
        }
        response = self.client.post(self.url, invalid_data, format='json')
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)
        self.assertEqual('Senha incorreta.', response.data['detail'])

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
            cra=9.3,
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
            'habilidades': [{"nome": self.habilidade_nova1.nome, "grupo": self.habilidade_nova1.grupo}, 
                            {"nome": self.habilidade_nova2.nome, "grupo": self.habilidade_nova2.grupo}], 
            'experiencias': [{"nome": self.experiencia_nova1.nome, "grupo": self.experiencia_nova1.grupo}, 
                             {"nome" : self.experiencia_nova2.nome, "grupo" : self.experiencia_nova2.grupo}], 
            'interesses': [{"nome": self.interesse_novo1.nome, "grupo": self.interesse_novo1.grupo}, 
                           {"nome": self.interesse_novo2.nome, "grupo": self.interesse_novo2.grupo}]        
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
        self.data['habilidades'] = [{"nome": self.habilidade.nome, "grupo": self.habilidade.grupo}] 
        self.data['experiencias'] = [{"nome": self.experiencia.nome, "grupo": self.experiencia.grupo}] 

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