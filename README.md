<h1 align="center">ProjetIn :computer: :link:</h1>

## Índice 

* [Instalações prévias](#Instalações-prévias-necessárias)
* [Configuração do ambiente de trabalho](#Configurar-o-ambiente-de-trabalho)
* [Pull](#Pull)
* [Ambiente previamente configurado](#Ambiente-configurado-anteriormente)
* [Push](#Push)
* [Inicialização da aplicação](#Iniciar-a-aplicação)
* [Status do Projeto](#status-do-Projeto)

----
#### Instalações prévias necessárias:
- PostegreSQL

----
#### Configurar o ambiente de trabalho

- Para configurar o ambiente de trabalho pela primeira vez, utilizar os seguintes comandos:

```
# 1. Instalar o pacote do ambiente virtual

 - No Unix
apt install python3.10-venv


# 2. Criar o ambiente virtual

python -m venv .venv


# 3. Ativar o ambiente virtual
 
 - No Windows:
.venv\Scripts\activate

 - No Unix ou MacOS:
source .venv/bin/activate


# 4. Instalar as dependências

pip install -r requirements/requirements.txt
````
----
####  Pull
- Ao dar pull, refazer os passos 3 e 4.

----
####  Ambiente configurado anteriormente
- Ao reiniciar o terminal, refazer o passo 3.

----
#### Push
- Antes de dar push, se foi adicionado alguma dependência, deve-se usar o seguinte comando:
```
pip freeze > requirements/requirements.txt
```
----

#### Iniciar a aplicação
- Para iniciar a aplicação, usar os seguintes comandos:
```
python.\manage.py runserver
```
```
python. \manage.py migration
```
```
python. \manage.py migrate
```
----
#### Status do Projeto
<h4 align="center"> 
    :construction:  Projeto em construção  :construction:
</h4>

----