from django.core.management.base import BaseCommand
from api_aluno.models import Experiencia, Habilidade, Interesse, Feedback


class Command(BaseCommand):
    help = 'Populate the Tags table with initial data'

    def handle(self, *args, **kwargs):
        tags_habilidades = [
            # Soft Skills
            ('Organização de Projetos', 'Soft Skills'),
            ('Resolução de Problemas', 'Soft Skills'),
            ('Trabalho em Equipe', 'Soft Skills'),
            ('Comunicação Eficaz', 'Soft Skills'),
            ('Adaptabilidade', 'Soft Skills'),
            ('Pensamento Criativo', 'Soft Skills'),
            ('Pensamento Analítico', 'Soft Skills'),
            ('Liderança', 'Soft Skills'),
            ('Negociação', 'Soft Skills'),
            ('Proatividade', 'Soft Skills'),

            # Hard Skills
            ('Programação', 'Hard Skills'),
            ('Banco de Dados', 'Hard Skills'),
            ('Análise de Dados', 'Hard Skills'),
            ('Cybersegurança', 'Hard Skills'),
            ('Infraestrutura', 'Hard Skills'),
            ('Inteligência Artificial', 'Hard Skills'),
            ('Aprendizado de Máquinas', 'Hard Skills'),
            ('Computação em Nuvem', 'Hard Skills'),
            ('DevOps', 'Hard Skills'),
            ('Desenvolvimento Mobile', 'Hard Skills'),
            ('Desenvolvimento Web', 'Hard Skills'),
            ('Desenvolvimento de Software', 'Hard Skills'),
            ('Testes', 'Hard Skills')
        ]

        tags_experiencias = [
            # Experiências
            ('Gestão de Equipes', 'Experiências'),
            ('Gestão de Projetos', 'Experiências'),
            ('Gestão de Infraestrutura', 'Experiências'),
            ('Design', 'Experiências'),
            ('Deploy', 'Experiências'),
            ('Implementação de Sistemas', 'Experiências'),
            ('Migração de Sistemas', 'Experiências'),
            ('Projetos de Aplicativos Móveis', 'Experiências'),
            ('Full Stack Developer', 'Experiências'),
            ('Backend Developer', 'Experiências'),
            ('Frontend Developer', 'Experiências'),
            ('Modelagem de Dados', 'Experiências'),
            ('Relatórios Analíticos', 'Experiências'),
            ('Suporte Técnico', 'Experiências'),
            ('Automação de Testes', 'Experiências'),
            ('APIs', 'Experiências'),
            ('Cloud', 'Experiências')
        ]

        tags_interesses = [
            # Interesses
            ('Banco de Dados', 'Interesses'),
            ('Análise de Dados', 'Interesses'),
            ('Cybersegurança', 'Interesses'),
            ('Infraestrutura', 'Interesses'),
            ('Inteligência Artificial', 'Interesses'),
            ('Aprendizado de Máquinas', 'Interesses'),
            ('Computação em Nuvem', 'Interesses'),
            ('DevOps', 'Interesses'),
            ('Desenvolvimento Mobile', 'Interesses'),
            ('Desenvolvimento Web', 'Interesses'),
            ('Desenvolvimento de Software', 'Interesses'),
            ('Testes', 'Interesses'),
            ('Gestão', 'Interesses')
        ]

        tags_feedbacks = [
            # Feedbacks
            ('Boa Comunicação', 'Feedbacks'),
            ('Proativo', 'Feedbacks'),
            ('Criativo', 'Feedbacks'),
            ('Bom Trabalho em Equipe', 'Feedbacks'),
            ('Responsável', 'Feedbacks'),
            ('Líder', 'Feedbacks'),
            ('Organizado', 'Feedbacks'),
            ('Boa Adaptação', 'Feedbacks'),
            ('Autônomo', 'Feedbacks'),
            ('Dedicado', 'Feedbacks'),
            ('Pensamento Crítico', 'Feedbacks'),
            ('Preciso', 'Feedbacks'),
            ('Empático', 'Feedbacks'),
            ('Boa Resolução de Problemas', 'Feedbacks'),
            ('Visão de Futuro', 'Feedbacks'),
            ('Detalhista', 'Feedbacks'),
            ('Resiliente', 'Feedbacks'),
            ('Engajado', 'Feedbacks'),
            ('Flexível', 'Feedbacks'),
        ]

        for nome, grupo in tags_habilidades:
            Habilidade.objects.create(nome=nome, grupo=grupo)

        for nome, grupo in tags_experiencias:
            Experiencia.objects.create(nome=nome, grupo=grupo)

        for nome, grupo in tags_interesses:
            Interesse.objects.create(nome=nome, grupo=grupo)

        for nome, grupo in tags_feedbacks:
            Feedback.objects.create(nome=nome, grupo=grupo)

        self.stdout.write(self.style.SUCCESS('Successfully populated the Tags table'))
