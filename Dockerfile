FROM python:3.11

WORKDIR /projetin

COPY requirements/requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY api_aluno/ api_aluno/
COPY api_professor/ api_professor/
COPY api_projeto/ api_projeto/
COPY api_rest/ api_rest/
COPY backend/ backend/
COPY manage.py .

EXPOSE 8080

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
