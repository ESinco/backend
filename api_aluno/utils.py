import pdfplumber
from .models import Disciplina


def extrair_disciplinas_do_pdf(historico_academico, historico_pdf):
    total_creditos = 0
    soma_pontuada = 0

    with pdfplumber.open(historico_pdf) as pdf:
        for page in pdf.pages:
            # Extrai as linhas de texto da página
            lines = page.extract_text().splitlines()

            disciplinas = []
            i = 0
            while i < len(lines):
                line = lines[i].strip()

                # Verifica se a linha contém a palavra "Aprovado" ou "Em Curso"
                if "Aprovado" in line or "Em Curso" in line:
                    partes = line.split()
                    if len(partes) < 8:
                        i += 1
                        continue

                    codigo = partes[0]
                    periodo = partes[-1]
                    situacao = " ".join(partes[-2:-1])

                    aux = 0
                    if situacao == "Curso":
                        situacao = " ".join(partes[-3:-1])
                        aux = -1

                    nome = " ".join(partes[1:(-6 + aux)])
                    tipo = partes[(-6 + aux)]

                    try:
                        creditos = int(partes[(-5 + aux)])
                    except (ValueError, IndexError):
                        creditos = 0  # Atribuir valor padrão para evitar null

                    try:
                        carga_horaria = int(partes[(-4 + aux)])
                    except (ValueError, IndexError):
                        carga_horaria = 0  # Atribuir valor padrão para evitar null

                    try:
                        media_str = partes[(-3 + aux)]
                        media_str = media_str.replace(',', '.')
                        media = float(media_str)
                    except ValueError:
                        media = None


                    nomes_professores = []
                    i += 1

                    while i < len(lines):
                        line = lines[i].strip()

                        if not line or line[0].isdigit():
                            break

                        if line == "Integralização curricular":
                            break

                        if line:
                            nomes_professores.append(line)

                        i += 1

                    nome_professor = ", ".join(nomes_professores)

                    disciplina = Disciplina(
                        historico=historico_academico,
                        codigo=codigo,
                        nome=nome,
                        professor=nome_professor,
                        tipo=tipo,
                        creditos=creditos,
                        carga_horaria=carga_horaria,
                        media=media,
                        situacao=situacao,
                        periodo=periodo
                    )
                    disciplina.save()
                    disciplinas.append(disciplina)

                    if media is not None and creditos is not None:
                        total_creditos += creditos
                        soma_pontuada += media * creditos
                else:
                    i += 1

    if total_creditos > 0:
        cra = round(soma_pontuada / total_creditos, 2)
        historico_academico.cra = cra
        historico_academico.save()
