# 🧪 TCC DevSecOps — Microserviço FastAPI (SUT)

> **Etapa 2 — Finalizar microserviço FastAPI**
> Repositório: [r2WillDev/tcc-devsecops-pipeline](https://github.com/r2WillDev/tcc-devsecops-pipeline) · Branch: `feature/app-fastapi-tests`

---

## 📌 Descrição

Este diretório contém o microserviço FastAPI desenvolvido como parte do Trabalho de Conclusão de Curso:

> **"Avaliação Experimental do Impacto de Práticas DevSecOps no Lead Time de Pipelines CI/CD"**

O objetivo desta etapa é construir uma aplicação simples, funcional e bem documentada que servirá como **System Under Test (SUT)** — ou seja, o sistema alvo de todas as análises e experimentos do estudo.

---

## 🔬 O que é o SUT neste projeto?

O **SUT (System Under Test)** é a aplicação que será submetida a todas as ferramentas e etapas do pipeline DevSecOps experimental. Neste projeto, o SUT é este microserviço FastAPI, que futuramente passará por:

- ✅ Testes automatizados com **Pytest**
- 🐳 Build e execução em **container Docker**
- 🚀 Deploy local via **Docker Compose**
- 🔁 Execução em **pipeline CI/CD** (GitHub Actions)
- 🔍 Análise estática de código — **SAST** com SonarQube
- 📦 Análise de dependências e imagem — **SCA/Container** com Trivy
- 🌐 Análise de segurança em execução — **DAST** com OWASP ZAP

A simplicidade da aplicação é **intencional**: quanto menos complexidade funcional, mais isolado e preciso é o impacto medido nas ferramentas de segurança do pipeline.

---

## 🛠️ Tecnologias utilizadas

| Tecnologia | Versão   | Finalidade                          |
|------------|----------|--------------------------------------|
| Python     | 3.11+    | Linguagem principal                  |
| FastAPI    | 0.111.0  | Framework web para a API REST        |
| Uvicorn    | 0.30.1   | Servidor ASGI para execução local    |
| Pytest     | 8.2.2    | Framework de testes automatizados    |
| HTTPX      | 0.27.0   | Cliente HTTP assíncrono para testes  |

---

## 📁 Estrutura da pasta

```
app/
├── main.py           # Código principal da API FastAPI
├── test_main.py      # Testes automatizados com Pytest
├── requirements.txt  # Dependências do projeto
└── README.md         # Esta documentação
```

---

## 🔗 Endpoints disponíveis

| Método | Rota      | Descrição                                      |
|--------|-----------|------------------------------------------------|
| GET    | `/`       | Mensagem de boas-vindas da API                 |
| GET    | `/health` | Verifica se a aplicação está saudável          |
| GET    | `/items`  | Retorna a lista de itens armazenados em memória|
| POST   | `/items`  | Cria um novo item e armazena em memória        |

---

## 📦 Exemplos de respostas JSON

**`GET /`**
```json
{
  "message": "TCC DevSecOps API"
}
```

**`GET /health`**
```json
{
  "status": "ok"
}
```

**`GET /items`**
```json
[
  {
    "id": 1,
    "name": "Item exemplo",
    "description": "Item usado no experimento"
  }
]
```

**`POST /items`** — corpo da requisição:
```json
{
  "name": "Novo item",
  "description": "Item criado para teste"
}
```
Resposta:
```json
{
  "id": 2,
  "name": "Novo item",
  "description": "Item criado para teste"
}
```

---

## ⚙️ Como instalar as dependências

Com o ambiente virtual ativado (recomendado), execute dentro da pasta `app/`:

```bash
pip install -r requirements.txt
```

---

## ▶️ Como rodar a aplicação localmente

```bash
python -m uvicorn main:app --reload
```

A API estará disponível em:

```
http://127.0.0.1:8000
```

---

## 📖 Como acessar a documentação automática do FastAPI

Com a aplicação em execução, acesse no navegador:

| Interface     | URL                              |
|---------------|----------------------------------|
| Swagger UI    | http://127.0.0.1:8000/docs       |
| ReDoc         | http://127.0.0.1:8000/redoc      |

A documentação é gerada automaticamente pelo FastAPI com base nos endpoints definidos em `main.py`.

---

## 🧩 Como testar os endpoints manualmente

### PowerShell — `Invoke-RestMethod`

```powershell
# GET /
Invoke-RestMethod -Uri http://127.0.0.1:8000/ -Method GET

# GET /health
Invoke-RestMethod -Uri http://127.0.0.1:8000/health -Method GET

# GET /items
Invoke-RestMethod -Uri http://127.0.0.1:8000/items -Method GET

# POST /items
$body = '{"name": "Novo item", "description": "Item criado para teste"}'
Invoke-RestMethod -Uri http://127.0.0.1:8000/items -Method POST `
  -ContentType "application/json" -Body $body
```

### curl (PowerShell / terminal)

```bash
# GET /
curl.exe http://127.0.0.1:8000/

# GET /health
curl.exe http://127.0.0.1:8000/health

# GET /items
curl.exe http://127.0.0.1:8000/items

# POST /items
curl.exe -X POST http://127.0.0.1:8000/items `
  -H "Content-Type: application/json" `
  -d "{\"name\": \"Novo item\", \"description\": \"Item criado para teste\"}"
```

---

## 🧪 Como executar os testes automatizados

Dentro da pasta `app/`, execute:

```bash
python -m pytest -v
```

---

## ✅ Resultado esperado dos testes

```
collected 4 items

test_main.py::test_root          PASSED
test_main.py::test_health        PASSED
test_main.py::test_get_items     PASSED
test_main.py::test_post_item     PASSED

====== 4 passed in X.XXs ======
```

Todos os 4 testes devem passar sem erros ou avisos.

---
## 🎯 Decisões de escopo

Esta aplicação foi desenvolvida com escopo **deliberadamente reduzido**. As decisões abaixo são parte do design experimental do TCC:

| Decisão                             | Justificativa                                                                 |
|-------------------------------------|-------------------------------------------------------------------------------|
| ❌ Sem banco de dados               | Dados em memória eliminam variáveis externas na medição do pipeline            |
| ❌ Sem autenticação                 | Reduz complexidade e isola o impacto das ferramentas SAST/DAST                |
| ❌ Sem múltiplos microserviços      | Um único SUT garante experimentos controlados e reproduzíveis                 |
| ❌ Sem lógica de negócio complexa   | O foco é o pipeline, não a aplicação em si                                    |
| ✅ API REST simples e documentada   | Suficiente para ser analisada por SonarQube, Trivy e OWASP ZAP               |

> A simplicidade é um requisito metodológico, não uma limitação técnica.

---

*Documentação referente à Etapa 2 do experimento DevSecOps.*
