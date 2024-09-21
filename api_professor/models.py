from django.db import models
from django.contrib.auth.models import User


class Professor(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
    nome = models.TextField(null=False)
    email = models.TextField(null=False, unique=True)

    def __str__(self):
        return (f'nome: {self.nome}\n'
                f'email: {self.email}')
