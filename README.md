
# 📝 FastAPI Notes API

API RESTful para gerenciamento de notas, desenvolvida com **FastAPI**, **Pydantic**, **SQLAlchemy**, e **SQLite**.  
Ideal para estudos e como base para projetos backend mais robustos.

---

## 🚀 Funcionalidades

- ✅ Criar uma nova nota (`POST /notes`)
- 📄 Listar todas as notas com paginação e ordenação (`GET /notes`)
- 🔍 Buscar nota por ID (`GET /notes/{id}`)
- ✏️ Atualizar uma nota por ID (`PATCH /notes/{id}`)
- ❌ Deletar nota por ID (`DELETE /notes/{id}`)
- 🔐 Criar conta de usuário (`POST /register`)
- 🔑 Autenticar e obter token JWT (`POST /token`)
- 🧪 Testes automatizados com `pytest` + `httpx`

---

## 📦 Requisitos

- Python 3.10 ou superior
- SQLite 
- Ambiente virtual com `venv`

---

## ⚙️ Instalação

```bash
# Clone o repositório
git clone https://github.com/BrunoAguiar-A/notes-API
cd fastapi-notes

# Crie e ative o ambiente virtual
python -m venv venv
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt
```

---

## ▶️ Executando a aplicação

```bash
uvicorn main:app --reload
```

Acesse em: [http://localhost:8000/docs](http://localhost:8000/docs) para visualizar a documentação interativa (Swagger).

---

## 📂 Estrutura do Projeto

```
.
├── main.py                 # Ponto de entrada da aplicação
├── auth/                   # Criação e validação de tokens JWT
├── alembic/                # Diretório de migrações do banco
├── models/                 # Modelos SQLAlchemy
├── schemas/                # Schemas Pydantic
├── services/               # Regras de negócio
├── routes/                 # Endpoints da API
├── tests/                  # Testes automatizados
├── database.py             # Configuração e conexão com o banco
├── pytest.ini              # Configurações do Pytest
├── alembic.ini             # Configurações do Alembic
├── requirements.txt        # Dependências do projeto
└── README.md               # Documentação
```

---

## 📬 Endpoints

| Método   | Rota        | Descrição                            |
|----------|-------------|----------------------------------------|
| POST     | /register   | Cria uma nova conta de usuário        |
| POST     | /token      | Gera token JWT para autenticação      |
| GET      | /notes      | Lista todas as notas                  |
| GET      | /notes/{id} | Retorna uma nota específica           |
| POST     | /notes      | Cria uma nova nota                    |
| PATCH    | /notes/{id} | Atualiza parcialmente uma nota        |
| DELETE   | /notes/{id} | Remove uma nota                       |

---

## 🧪 Rodando os Testes

```bash
pytest
```

Inclui testes de integração com `httpx.AsyncClient`, cobrindo autenticação, validações e operações CRUD.

---

## 🛠️ Tecnologias Utilizadas

- ⚡ **[FastAPI](https://fastapi.tiangolo.com/)** – Framework moderno para APIs REST
- 📦 **[Pydantic](https://docs.pydantic.dev/)** – Tipagem e validação de dados
- 🔒 **[Passlib](https://passlib.readthedocs.io/en/stable/)** – Hash de senhas com bcrypt
- 🧠 **[SQLAlchemy](https://www.sqlalchemy.org/)** – ORM para o banco de dados
- 🗃️ **[SQLite](https://www.sqlite.org/)** – Banco de dados leve
- 🔁 **[Alembic](https://alembic.sqlalchemy.org/)** – Controle de versão do schema do banco
- 🔐 **OAuth2 + JWT** – Autenticação baseada em token seguro
- 🧪 **[Pytest](https://docs.pytest.org/)** – Testes automatizados
- 🔗 **[httpx](https://www.python-httpx.org/)** – Cliente HTTP assíncrono para testes

---

## 📌 TODO

- [x] Conectar a banco de dados real (SQLite)
- [x] Implementar testes automatizados
- [x] Adicionar autenticação com tokens (OAuth2 ou JWT)
- [x] Criar uma documentação OpenAPI personalizada
- [ ] Deploy (Docker ou serviços como Railway/Render)
