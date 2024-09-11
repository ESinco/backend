from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from .models import Habilidade, Experiencia, Interesse, Feedback

class TagTests(APITestCase):
    def setUp(self):
        Habilidade.objects.create(nome='Programação', grupo='Hard Skills')
        Experiencia.objects.create(nome='Gestão de Projetos', grupo='Experiências')
        Interesse.objects.create(nome='Inteligência Artificial', grupo='Interesses')
        Feedback.objects.create(nome='Boa Comunicação', grupo='Feedbacks')

    def test_get_habilidades(self):
        url = reverse('get_all_habilidades')
        response = self.client.get(url)
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nome'], 'Programação')
        self.assertEqual(response.data[0]['grupo'], 'Hard Skills')

    def test_get_experiencias(self):
        url = reverse('get_all_experiencias')
        response = self.client.get(url)
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nome'], 'Gestão de Projetos')
        self.assertEqual(response.data[0]['grupo'], 'Experiências')

    def test_get_interesses(self):
        url = reverse('get_all_interesses')
        response = self.client.get(url)
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nome'], 'Inteligência Artificial')
        self.assertEqual(response.data[0]['grupo'], 'Interesses')

    def test_get_feedbacks(self):
        url = reverse('get_all_feedbacks')
        response = self.client.get(url)
        
        #Asserts
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['nome'], 'Boa Comunicação')
        self.assertEqual(response.data[0]['grupo'], 'Feedbacks')
