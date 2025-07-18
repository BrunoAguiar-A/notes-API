# notes-API
API RESTful para gerenciamento de notas, construída com FastAPI. Python e versionamento de projeto backend.


# 📝 fastapi-notes

Uma API simples para gerenciamento de notas (CRUD) construída com [FastAPI].  
projeto RESTful e como base para APIs mais robustas.

---

## 🚀 Funcionalidades

- ✅ Criar uma nova nota (POST)
- 📄 Listar todas as notas (GET)
- 🔍 Obter nota por ID (GET)
- ✏️ Atualizar nota por ID (PUT e PATCH)
- ❌ Remover nota por ID (DELETE)

---

## 📦 Requisitos

- Python 3.10 ou superior
- `virtualenv` (opcional, mas recomendado)

---

## ⚙️ Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/fastapi-notes.git
cd fastapi-notes

# Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

▶️ Executando a aplicação
bash
Copiar
Editar
uvicorn main:app --reload
Acesse em: http://localhost:8000

🧪 Endpoints
Método	Rota	Descrição
GET	/notas	Lista todas as notas
GET	/notas/{id}	Retorna uma nota específica
POST	/notas	Cria uma nova nota
PUT	/notas/{id}	Atualiza totalmente a nota
PATCH	/notas/{id}	Atualização parcial
DELETE	/notas/{id}	Remove uma nota

📚 Tecnologias utilizadas
FastAPI

Pydantic

Uvicorn

(opcional) SQLite, SQLAlchemy, etc.

📌 TODOs
 Adicionar testes com pytest e httpx

 Implementar autenticação com token

 Conectar com banco de dados real

 Criar documentação OpenAPI personalizada
