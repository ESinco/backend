from django.core.mail import send_mail


def encaminhar_email(aluno, projeto, aceito):
    try:
        if aceito:
            assunto = "Resposta de Inscrição no Projeto"
            mensagem = (
                f"Olá {aluno.nome},\n\n"
                f"Agradecemos o seu interesse no projeto {projeto.nome}. "
                "Infelizmente, você não passou para a próxima etapa.\n\n"
                "Esperamos vê-lo em outro processo de seleção no futuro!\n\n"
                "Atenciosamente,\nEquipe do ProjetIn."
            )
            destinatario = [aluno.email]

            send_mail(
                assunto,
                mensagem,
                'projetinufcg@gmail.com',
                destinatario,
                fail_silently=False,
            )

        else:
            assunto = "Resposta de Inscrição no Projeto"
            mensagem = (
                f"Olá {aluno.nome},\n\n"
                f"Agradecemos o seu interesse no projeto {projeto.nome}. "
                "Felizmente, você passou para a próxima etapa.\n\n"
                "Atenciosamente,\nEquipe do ProjetIn."
            )
            destinatario = [aluno.email]

            send_mail(
                assunto,
                mensagem,
                'projetinufcg@gmail.com',
                destinatario,
                fail_silently=False,
            )
    except BaseException:
        return None
