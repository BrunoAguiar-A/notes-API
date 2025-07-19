import sys, os, pytest_asyncio
from httpx import AsyncClient, ASGITransport
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app

@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

@pytest_asyncio.fixture
async def create_temp_note(async_client):
    # Cria nota temporária antes do teste
    response = await async_client.post("/notes/", json={
        "title": "Nota Temporária",
        "content": "Conteúdo Temporário"
    })
    assert response.status_code == 201
    note = response.json()

    yield note  # Disponibiliza a nota para o teste

    # Apaga após o teste
    await async_client.delete(f"/notes/{note['id']}")
