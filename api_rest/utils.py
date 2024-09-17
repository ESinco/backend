from .models import Disciplina

import requests

def atualizar_disciplinas():
    url = "https://eureca.sti.ufcg.edu.br/das/v2/curriculos/curriculo?curso=14102100&curriculo=2023"
    response = realizer_requisicao(url)
    if response:
        salvar_disciplinas(response["disciplinas_do_curriculo"])
    
    url = "https://eureca.sti.ufcg.edu.br/das/v2/curriculos/curriculo?curso=14102100&curriculo=2017"
    response = realizer_requisicao(url)
    if response:
        salvar_disciplinas(response["disciplinas_do_curriculo"])
    
def realizer_requisicao(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.RequestException as e:
        return None

def salvar_disciplinas(disciplinas):
    for disciplina in disciplinas:
        codigo_da_disciplina = disciplina['codigo_da_disciplina']
        existe_disciplina = Disciplina.objects.filter(pk=codigo_da_disciplina).exists()
        if not existe_disciplina:
            disciplinas_equivalentes = [eq['codigo_da_disciplina'] for eq in disciplina['disciplinas_equivalentes']]
            disciplina = Disciplina.objects.create(
                codigo=codigo_da_disciplina,
                nome=disciplina['nome_da_disciplina'],
                disciplinas_equivalentes=disciplinas_equivalentes
            )