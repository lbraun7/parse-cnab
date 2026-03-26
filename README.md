# CNAB Importer

Aplicação web para importação e visualização de transações financeiras no formato CNAB.

## Funcionalidades

- Upload de arquivo CNAB `.txt` via drag-and-drop ou seleção
- Parser do formato CNAB
- Armazenamento das transações por usuário em PostgreSQL
- Listagem de lojas com saldo consolidado e tabela de transações expansível
- Autenticação via **OAuth 2.0 com Google**
- API REST documentada via Swagger (`/docs`) e ReDoc (`/redoc`)

## Stack

| Camada   | Tecnologia                             |
| -------- | -------------------------------------- |
| Backend  | FastAPI + SQLAlchemy (async) + Alembic |
| Banco    | PostgreSQL 15                          |
| Frontend | React 18 + Vite                        |
| Auth     | OAuth 2.0 Google + JWT                 |
| Infra    | Docker + Docker Compose                |

---

## Setup

### 1. Pré-requisitos

- Docker e Docker Compose instalados
- Conta no [Google Cloud Console](https://console.cloud.google.com) para criar as credenciais OAuth

### 2. Credenciais Google OAuth

1. Acesse o [Google Cloud Console](https://console.cloud.google.com)
2. Crie um projeto (ou selecione um existente)
3. Vá em **APIs & Services → Credentials → Create Credentials → OAuth client ID**
4. Tipo: **Web Application**
5. Adicione em **Authorized redirect URIs**:
   ```
   http://localhost:8000/api/auth/google/callback
   ```
6. Copie o **Client ID** e **Client Secret**

### 3. Variáveis de ambiente

```bash
cp .env.example .env
```

Edite `.env` e preencha:

```env
GOOGLE_CLIENT_ID=seu-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=seu-client-secret
SECRET_KEY=uma-chave-secreta-longa-e-aleatoria
```

### 4. Subir a aplicação

```bash
docker compose up --build
```

Aguarde os containers iniciarem. O backend executa `alembic upgrade head` automaticamente.

| Serviço     | URL                         |
| ----------- | --------------------------- |
| Frontend    | http://localhost:3000       |
| Backend API | http://localhost:8000       |
| Swagger UI  | http://localhost:8000/docs  |
| ReDoc       | http://localhost:8000/redoc |

---

## Uso

1. Acesse http://localhost:3000
2. Clique em **Entrar com Google** e autentique
3. Na tela principal, arraste ou selecione um arquivo CNAB `.txt`
4. As transações são importadas e exibidas agrupadas por loja
5. Clique em uma loja para expandir e ver todas as transações

---

## API — Endpoints

### Autenticação

| Método | Rota                        | Descrição                                |
| ------ | --------------------------- | ---------------------------------------- |
| `GET`  | `/api/auth/google/login`    | Redireciona para login Google            |
| `GET`  | `/api/auth/google/callback` | Callback OAuth, retorna JWT via redirect |
| `GET`  | `/api/auth/me`              | Retorna dados do usuário autenticado     |

**Header de autenticação:**

```
Authorization: Bearer <token>
```

### Transações

| Método | Rota                       | Descrição                          |
| ------ | -------------------------- | ---------------------------------- |
| `POST` | `/api/transactions/upload` | Upload do arquivo CNAB             |
| `GET`  | `/api/transactions/stores` | Lista lojas com saldo e transações |

#### `POST /api/transactions/upload`

- **Content-Type:** `multipart/form-data`
- **Campo:** `file` — arquivo `.txt` no formato CNAB

**Resposta de sucesso (200):**

```json
{
  "imported": 21,
  "errors": 0,
  "message": "21 transações importadas com sucesso."
}
```

#### `GET /api/v1/transactions/stores`

**Resposta de sucesso (200):**

```json
{
  "total_stores": 2,
  "stores": [
    {
      "store_name": "MERCADO DA AVENIDA",
      "store_owner": "JOSE COSTA",
      "balance": "152.00",
      "transactions": [
        {
          "id": 1,
          "transaction_type": 3,
          "description": "Financiamento",
          "nature": "saida",
          "occurred_at": "2019-03-01T15:47:02",
          "amount": "142.00",
          "cpf": "09620676017",
          "card": "4753830274CPF",
          "store_owner": "JOSE COSTA",
          "store_name": "MERCADO DA AVENIDA",
          "created_at": "2024-01-01T00:00:00"
        }
      ]
    }
  ]
}
```

---

## Testes

```bash
docker compose exec backend bash
pytest --cov=app --cov-report=term-missing
```

Ou localmente (com Python 3.11+ e dependências instaladas):

```bash
cd backend
pip install -r requirements.txt
pytest --cov=app --cov-report=term-missing
```

---

## Estrutura do projeto

```
cnab-challenge/
├── docker-compose.yml
├── .env.example
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   │       └── 0001_initial.py
│   └── app/
│       ├── main.py
│       ├── endpoints/
│       │   ├── auth.py
│       │   └── transactions.py
│       ├── core/
│       │   ├── config.py
│       │   ├── database.py
│       │   └── security.py
│       ├── models/
│       │   ├── users.py
│       │   ├── transactions.py
│       ├── schemas/
│       │   ├── auth.py
│       │   ├── transactions.py
│       ├── services/
│       │   ├── parser.py
│       │   ├── oauth.py
│       │   └── transactions.py
│       └── tests/
│           ├── conftest.py
│           ├── test_cnab_parser.py
│           └── test_transactions.py
└── frontend/
    ├── Dockerfile
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── App.jsx
        ├── main.jsx
        ├── context/AuthContext.jsx
        ├── services/api.js
        ├── hooks/useTransactions.js
        ├── components/
        │   ├── Navbar.jsx
        │   ├── UploadZone.jsx
        │   └── StoreCard.jsx
        ├── pages/
        │   ├── Login.jsx
        │   ├── AuthCallback.jsx
        │   └── Dashboard.jsx
        └── styles/global.css
```

---

## Documentação do CNAB

| Campo        | Início | Fim | Tamanho |
| ------------ | ------ | --- | ------- |
| Tipo         | 1      | 1   | 1       |
| Data         | 2      | 9   | 8       |
| Valor        | 10     | 19  | 10      |
| CPF          | 20     | 30  | 11      |
| Cartão       | 31     | 42  | 12      |
| Hora         | 43     | 48  | 6       |
| Dono da loja | 49     | 62  | 14      |
| Nome da loja | 63     | 81  | 19      |
