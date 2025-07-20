import sys, os, pytest_asyncio, uuid, pytest
from httpx import AsyncClient, ASGITransport
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from auth.users import pwd_context

# Fixture that provides an authenticated async client
@pytest_asyncio.fixture
async def async_client(auth_headers):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers=auth_headers
    ) as client:
        yield client

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

@pytest.fixture
def create_test_user():
    def _create():
        db: Session = next(get_db())
        username = "test_user"
        password = "test123"
        user = db.query(User).filter(User.username == username).first()
        if not user:
            user = User(username=username, hashed_password=pwd_context.hash(password))
            db.add(user)
            db.commit()
            db.refresh(user)
        return {"username": username, "password": password}
    return _create

@pytest_asyncio.fixture
async def auth_headers(create_test_user):
    credentials = create_test_user()
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        response = await client.post("/token", data={
            "username": credentials["username"],
            "password": credentials["password"]
        })
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
# Helper function to get valid authentication headers (Bearer token)
@pytest_asyncio.fixture
async def get_auth_headers(create_test_user):
    credentials = create_test_user() # Create user in BD
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/token", data={
            "username": credentials["username"],
            "password": credentials["password"]
        })
        token = response.json()["access_token"] # Extract the access token from the response
        return {"Authorization": f"Bearer {token}"}