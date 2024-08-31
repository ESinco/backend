from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from api_rest.models import Aluno, HistoricoAcademico, Disciplina
from django.core.files.uploadedfile import SimpleUploadedFile

import os


class HistoricoAcademicoTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        # Cria o aluno
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
        cls.url_upload = '/historico/upload/'

        # Caminho para o PDF de teste
        cls.pdf_path = os.path.join(os.path.dirname(__file__), 'test_data', 'historico.pdf')

        if not os.path.exists(cls.pdf_path):
            raise FileNotFoundError(f"O arquivo PDF não foi encontrado em {cls.pdf_path}")

        with open(cls.pdf_path, 'rb') as pdf_file:
            cls.historico_data = {
                "aluno": cls.aluno.matricula,
                "historico_pdf": SimpleUploadedFile("historico.pdf", pdf_file.read())
            }

        cls.url_visualizar = reverse('visualizar_historico', kwargs={'matricula': cls.aluno.matricula})

    def test_upload_historico(self):
        response = self.client.post(self.url_upload, data=self.historico_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_visualizar_historico(self):
        self.test_upload_historico()

        response = self.client.get(self.url_visualizar)
        assert response.status_code == status.HTTP_200_OK

    def test_visualizar_historico_aluno_nao_existe(self):
        url = reverse('visualizar_historico', kwargs={'matricula': '999999999'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_visualizar_historico_sem_historico(self):
        aluno_sem_historico = Aluno.objects.create(
            matricula="987654321",
            nome="Maria Oliveira",
            email="maria.oliveira@example.com",
            curriculo="Link do curriculo",
            github="https://github.com/mariaoliveira",
            linkedin="https://linkedin.com/in/mariaoliveira",
            cra=0.0,
            senha="senhaSegura"
        )
        url = reverse('visualizar_historico', kwargs={'matricula': aluno_sem_historico.matricula})
        response = self.client.get(url)
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

