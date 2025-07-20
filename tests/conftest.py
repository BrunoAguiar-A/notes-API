import sys, os, pytest_asyncio, uuid
from httpx import AsyncClient, ASGITransport
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app

# Fixture that provides an authenticated async client
@pytest_asyncio.fixture
async def async_client():
    headers = await get_auth_headers()
    # Create the test client with token headers
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers=headers) as client:
       yield client # Provide client to tests

# Fixture that creates a temporary note before a test and deletes it afterward
@pytest_asyncio.fixture
async def create_temp_note(async_client):
    unique_title = f"Nota Temporária {uuid.uuid4()}"
    response = await async_client.post("/notes/", json={
        "title": unique_title,
        "content": "Conteúdo Temporário"
    })
    assert response.status_code == 201
    return response.json()

# Helper function to get valid authentication headers (Bearer token)
async def get_auth_headers():
    async with AsyncClient(transport= ASGITransport(app=app), base_url="http://test") as client:
        # Make a login request using username and password (plaintext)
        response = await client.post("/token", data={
            "username": "bruno",  #valid user
            "password": "123456"
        })
        # Extract the access token from the response
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}