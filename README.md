# ProjetIn

----
#### Para configurar o ambiente de trabalho pela primeira vez, rode os seguintes comandos:

### 1. Instalar o pacote do ambiente virtual
```
apt install python3.10-venv
```

### 2. Criar o ambiente virtual
```
python -m venv .venv
```

### 3. Ativar o ambiente virtual
#### No Windows:
```
.venv\Scripts\activate
```
#### No Unix ou MacOS:
```
source .venv/bin/activate
```
### 4. Instalar as dependências
```
pip install -r requirements.txt
```
----
####  Pull:
- Ao dar pull, refazer os passos 2 e 3.
####  Ambiente configurado anteriormente:
- Ao reiniciar o terminal, refazer o passo 2.

----
#### Antes de dar push, se foi adicionado alguma dependência, deve-se rodar os seguintes comandos:

### 1. Mostrar os pacotes utilizados
```
pip freeze
```
### 2. Copiar a lista de todos os pacotes utilizados que será mostrado no terminal após o comando do passo 1

### 3. Salvar os pacotes no arquivo requirements/requirements.txt

----

#### Para iniciar a aplicação, digitar:
```
python.\manage.py runserver
```
----