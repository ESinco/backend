# ProjetIn :computer: :link:

----
##### Instalações prévias necessárias:
 - PostegreSQL

----
#### Para configurar o ambiente de trabalho pela primeira vez, utilizar os seguintes comandos:
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
####  Pull:
- Ao dar pull, refazer os passos 3 e 4.
####  Ambiente configurado anteriormente:
- Ao reiniciar o terminal, refazer o passo 3.

----
#### Antes de dar push, se foi adicionado alguma dependência, deve-se usar o seguinte comando:
```
pip freeze > requirements/requirements.txt
```
----

#### Para iniciar a aplicação, usar os seguintes comandos:
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