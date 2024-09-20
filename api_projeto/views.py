from django.http import JsonResponse
from django.contrib.auth.models import User
from django.utils import timezone

from allauth.account.models import EmailAddress
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status

from .models import *
from .serializers import *
from .utils import *

from io import StringIO

import csv


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def criar_projeto(request):
    try:
        professor_autenticado = Professor.objects.get(user=request.user)
    except Professor.DoesNotExist:
        return Response({"detail": "Acesso negado. Apenas professores podem criar projetos."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'POST':
        serializer = ProjetoInformacoesSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = request.data.copy()
        data['responsavel'] = professor_autenticado.id
        
        data['data_de_criacao'] = timezone.now()
        
        serializer = ProjetoSemIdSerializer(data=data)
        if serializer.is_valid():
            projeto = serializer.save()
            response_serializer = ProjetoSerializer(projeto)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def criar_projeto_csv(request):
    try:
        professor_autenticado = Professor.objects.get(user=request.user)
    except Professor.DoesNotExist:
        return Response({"detail": "Acesso negado. Apenas professores podem criar projetos."}, status=status.HTTP_403_FORBIDDEN)
    
    if 'file' not in request.data:
        return Response({'detail':'Arquivo não encontrado.'}, status=status.HTTP_400_BAD_REQUEST)
    
    csv_file = request.data['file']

    if not csv_file.name.endswith('.csv'):
        return Response({'detail':'O arquivo não é CSV.'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Simulação de leitura do arquivo CSV
        csv_content = csv_file.read().decode('utf-8')
        csv_io = StringIO(csv_content)
        csv_reader = csv.DictReader(csv_io)
        
        if len(csv_content.splitlines()) < 2:
            return Response({'detail': 'O arquivo CSV está vazio.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({'detail': f'Erro ao processar CSV: {str(e)}'}, status=500)
    
    projeto = Projeto.objects.create(
            nome="Projeto Novo",
            data_de_criacao=timezone.now(),
            responsavel=professor_autenticado
        )
    matricula_inexistente = []
        
    for linha in csv_reader:
        matricula = linha.get('Matricula')
        if matricula:
            try:
                aluno = Aluno.objects.get(pk=matricula)
                if not EmailAddress.objects.filter(user=aluno.user, verified=True).exists():
                    matricula_inexistente.append(matricula)
                else:
                    Associacao.objects.create(projeto_id=projeto.id_projeto, aluno_id=aluno.matricula, status=None)
            except Aluno.DoesNotExist:
                matricula_inexistente.append(matricula)
    
    return JsonResponse({'id_projeto': projeto.id_projeto,'matriculas_inexistente': matricula_inexistente}, status=201)           
   
@api_view(['GET'])
def get_projetos(request):
    if request.method == 'GET':
        projetos = Projeto.objects.all()
        serializer = ProjetoSerializer(projetos, many=True)
        data = serializer.data
        resultados = [{
                **item,
                'quantidade_de_inscritos': Associacao.objects.filter(projeto=item['id_projeto']).count()
            }
            for item in data
        ]
        return Response(resultados)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_by_id_projeto(request, id_projeto):
    if request.method == 'GET':
        try:
            projeto = Projeto.objects.get(pk=id_projeto)
            serializer = ProjetoSerializer(projeto)
        except Projeto.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND) 
        try:
            professor = Professor.objects.get(user=request.user)
        except Professor.DoesNotExist:
            professor = None
            
        data = serializer.data
        associacoes = Associacao.objects.filter(projeto=projeto)
        colaborador = Colaborador.objects.filter(projeto=projeto, professor=professor)
        if professor and (projeto.responsavel == professor or colaborador.exists()):    
            listas_de_filtros = Lista_Filtragem.objects.filter(id_projeto=projeto)
            data['listas_com_filtros'] = ListaFiltragemInfoSerializer(listas_de_filtros, many=True).data
            
            data['candidatos'] = AssociacaoInfoSerializer(associacoes, many=True).data
        
        data['quantidade_de_inscritos'] = associacoes.count()
        return Response(data)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
def get_all_projetos_by_professor(request):
    if request.method == 'GET':
        try:
            responsavel_id = request.GET.get('responsavel')
            responsavel = Professor.objects.get(pk=responsavel_id)
        except:
            return Response({"detail": "O parâmetro 'responsavel' é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            projetos = Projeto.objects.filter(responsavel=responsavel)
            serializer = ProjetoSerializer(projetos, many=True)
            data = serializer.data
            resultados = [{
                    **item,
                'quantidade_de_inscritos': Associacao.objects.filter(projeto=item['id_projeto']).count()
                }
                for item in data
            ]
            return Response(resultados)
        except Projeto.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_projetos_by_aluno(request):
    if request.method == 'GET':
        try:
            aluno_autenticado = Aluno.objects.get(user=request.user)
        except Aluno.DoesNotExist:
            return Response({"detail": "Acesso negado. Apenas alunos podem ver seus próprios projetos inscritos."},
                status=status.HTTP_403_FORBIDDEN)
        
        associacoes = Associacao.objects.filter(aluno=aluno_autenticado.matricula)
        projetos_com_status = []
        for associacao in associacoes:
            try:
                projeto = Projeto.objects.get(pk=associacao.projeto.id_projeto)
                projeto_dados = ProjetoSerializer(projeto).data
                projeto_dados['status'] = associacao.status
                projetos_com_status.append(projeto_dados)
            except Projeto.DoesNotExist:
                continue
        
        if not projetos_com_status:
            return Response({"detail": "Nenhum projeto encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
        return Response(projetos_com_status, status=status.HTTP_200_OK)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def editar_projeto(request, id_projeto):
    try:
        professor_autenticado = Professor.objects.get(user=request.user)
    except Professor.DoesNotExist:
        return Response({"detail": "Acesso negado. Apenas professores podem editar projetos."}, status=status.HTTP_403_FORBIDDEN)

    try:
        projeto = Projeto.objects.get(pk=id_projeto)
    except Projeto.DoesNotExist:
        return Response({"detail": "Projeto não encontrado."}, status=status.HTTP_404_NOT_FOUND)
    
    if projeto.responsavel != professor_autenticado:
        return Response({"detail": "Você não tem permissão para editar este projeto."}, status=status.HTTP_403_FORBIDDEN)

    if request.method in ['PUT', 'PATCH']:
        serializer = ProjetoInformacoesSerializer(projeto, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def salvar_filtragem(request):
    if request.method == 'POST':
        try:
            professor = Professor.objects.get(user=request.user)
        except Professor.DoesNotExist:
            return Response({"detail": "Acesso negado. Apenas professores podem cadastrar listas."}, status=status.HTTP_403_FORBIDDEN)
        
        entradas = ListaFiltragemPostSerializer(data=request.data)
        if not entradas.is_valid():
            return Response(entradas.errors, status=status.HTTP_400_BAD_REQUEST)
        
        id_projeto = entradas.data['id_projeto']
        projeto = Projeto.objects.get(pk=id_projeto)
        colaborador = Colaborador.objects.filter(projeto=projeto, professor=professor)
        if projeto.responsavel.id != professor.id and not colaborador.exists():
            return Response({"detail": "Apenas responsáveis ou colaboradores do projeto podem criar filtros."}, status=status.HTTP_403_FORBIDDEN)

        data = entradas.data.copy()
        data['id_professor'] = professor.id
        serializer = ListaFiltragemSemIdSerializer(data=data)
        if serializer.is_valid():
            lista_filtros = serializer.save()
            response_serializer = ListaFiltragemSerializer(lista_filtros)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)


    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def editar_filtragem(request, id_lista):
    if request.method == 'PUT':
        try:
            professor = Professor.objects.get(user=request.user)
        except Professor.DoesNotExist:
            return Response({"detail": "Acesso negado. Apenas professores podem cadastrar listas."}, status=status.HTTP_403_FORBIDDEN)
        
        entradas = ListaFiltragemPutSerializer(data=request.data)
        if not entradas.is_valid():
            return Response(entradas.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            lista = Lista_Filtragem.objects.get(pk=id_lista)
        except Lista_Filtragem.DoesNotExist:
            return Response({"detail": "Lista não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        if lista.id_professor.id != professor.id:
            return Response({"detail": "Apenas o dono da lista pode alterá-la."}, status=status.HTTP_403_FORBIDDEN)

        lista.titulo = entradas.data['titulo']
        lista.filtro_habilidades.set(entradas.data.get('filtro_habilidades', lista.filtro_habilidades.all()))
        lista.filtro_experiencias.set(entradas.data.get('filtro_experiencias', lista.filtro_experiencias.all()))
        lista.filtro_interesses.set(entradas.data.get('filtro_interesses', lista.filtro_interesses.all()))
        lista.filtro_cra = entradas.data.get('filtro_cra', lista.filtro_cra)
        lista.filtro_disciplinas = entradas.data.get('filtro_disciplinas', lista.filtro_disciplinas)

        lista.save()
        response_serializer = ListaFiltragemSerializer(lista)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cadastrar_colaborador(request, id_projeto, email_colaborador):
    try:
        professor = Professor.objects.get(user=request.user)
    except Professor.DoesNotExist:
        return Response({"detail": "Acesso negado. Apenas professores podem cadastrar colaboradores."}, status=status.HTTP_403_FORBIDDEN)

    try:
        projeto = Projeto.objects.get(pk=id_projeto)
    except:
        return Response({"detail": "Projeto não encontrado."}, status=status.HTTP_404_NOT_FOUND)
    
    if(projeto.responsavel.id != professor.id):
        return Response({"detail": "Acesso negado. Apenas o responsavel do projeto pode cadastrar um colaborador."}, status=status.HTTP_403_FORBIDDEN)

    try:
        colaborador = Professor.objects.get(email=email_colaborador)
    except Professor.DoesNotExist:
        return Response({"detail": "Professor colaborador não encontrado."}, status=status.HTTP_404_NOT_FOUND)
    
    associacao, criado = Colaborador.objects.get_or_create(professor_id=colaborador.id, projeto_id=id_projeto)

    if criado:
        return Response({"detail": "Associação criada com sucesso."}, status=status.HTTP_201_CREATED)
    else:
        return Response({"detail": "Professor ja é colaborador desse projeto."}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_lista_by_id(request, id_lista):
    if request.method == 'GET':
        try:
            professor = Professor.objects.get(user=request.user)
        except Professor.DoesNotExist:
            return Response({"detail": "Acesso negado. Apenas professores podem acessar listas de filtragens."}, status=status.HTTP_403_FORBIDDEN)

        try:
            lista = Lista_Filtragem.objects.get(pk=id_lista)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if lista.id_professor != professor:
            return Response({"detail": "Apenas o dono da lista pode visualizá-la"}, status=status.HTTP_403_FORBIDDEN)

        serializer = ListaFiltragemSerializer(lista)
        return Response(serializer.data)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def deletar_lista_filtragem(request, id_lista):
    if request.method == 'DELETE':
        try:
            professor = Professor.objects.get(user=request.user)
        except Professor.DoesNotExist:
            return Response({"detail": "Acesso negado. Apenas professores podem apagar listas."}, status=status.HTTP_403_FORBIDDEN)

        try:
            lista = Lista_Filtragem.objects.get(pk=id_lista)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if lista.id_professor != professor:
            return Response({"detail": "Apenas o dono da lista pode apagá-la"}, status=status.HTTP_403_FORBIDDEN)

        lista.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def gerenciar_inscricao(request, id_projeto, id_aluno):
    if request.method == 'POST':
        try:
            professor = Professor.objects.get(user=request.user)
        except Professor.DoesNotExist:
            return Response({"detail": "Acesso negado. Apenas professores podem gerenciar inscrições."}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            projeto = Projeto.objects.get(pk=id_projeto)
        except:
            return Response({"detail": "Projeto não encontrado."}, status=status.HTTP_404_NOT_FOUND)

        colaborador = Colaborador.objects.filter(projeto=projeto, professor=professor)
        if projeto.responsavel != professor and not colaborador.exists():
            return Response({"detail": "Apenas responsáveis ou colaboradores do projeto podem gerenciar inscrições."}, status=status.HTTP_403_FORBIDDEN)

        try:
            aluno = Aluno.objects.get(pk=id_aluno)
        except Aluno.DoesNotExist:
            return Response({"detail": "Aluno não encontrado."},
                status=status.HTTP_404_NOT_FOUND)
            
        try:
            associacao = Associacao.objects.get(aluno=aluno, projeto=projeto)
        except Associacao.DoesNotExist:
            return Response({"detail": "Essa inscrição não existe."}, status=status.HTTP_404_NOT_FOUND)
        
        novo_status = request.data['status']
        if not novo_status and not isinstance(novo_status, bool):
            return Response({"detail": "É necessário enviar um status como parâmetro com o seguinte formato: 'True' ou 'False'"}, status=status.HTTP_400_BAD_REQUEST)
        
        enviar_email = request.data['enviar_email']
        if not enviar_email and not isinstance(enviar_email, bool):
            return Response({"detail": "É necessário decidir se deve enviar um e-mail, através do parâmetro enviar_email: 'True' ou 'False'"}, status=status.HTTP_400_BAD_REQUEST)
        
        associacao.status = novo_status
        associacao.save()
        response = AssociacaoInfoSerializer(associacao).data
        response['email_enviado'] = False
        
        if enviar_email:
            encaminhar_email(aluno, projeto, novo_status)
            response['email_enviado'] = True
        
        return Response(response, status=status.HTTP_200_OK)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
