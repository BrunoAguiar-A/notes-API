import sys, os, pytest_asyncio, uuid, pytest
from httpx import AsyncClient, ASGITransport
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app
from sqlalchemy.orm import Session
from database import SessionLocal, get_db
from models.user import User
from auth.users import pwd_context
from models.note import Notes
from auth.jwt_handler import decode_token

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
    def _create(username="test_user", password="test123"):
        db: Session = next(get_db())
        user = db.query(User).filter(User.username == username).first()
        if not user:
            user = User(username=username, hashed_password=pwd_context.hash(password))
            db.add(user)
            db.commit()
            db.refresh(user)
        return {"id": user.id, "username": user.username, "password": password}
    return _create

@pytest_asyncio.fixture
async def auth_headers(create_test_user):
    import uuid
    username = f"user_{uuid.uuid4()}"
    password = "test123"
    credentials = create_test_user(username=username, password=password)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/token", data={
            "username": credentials["username"],
            "password": credentials["password"]
        })
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
# Helper function to get valid authentication headers (Bearer token)
@pytest_asyncio.fixture
async def get_auth_headers():
    async def _get(username: str, password: str):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/token", data={
                "username": username,
                "password": password
            })
            token = response.json()["access_token"]
            return {"Authorization": f"Bearer {token}"}
    return _get

    
@pytest.fixture(autouse=True)
def clean_database():
    db: Session = next(get_db())
    from models.note import Notes, SharedNote
    from models.user import User

    db.query(SharedNote).delete()
    db.query(Notes).delete()
    db.query(User).delete()
    db.commit()
    yield
    db.query(SharedNote).delete()
    db.query(Notes).delete()
    db.query(User).delete()
    db.commit()

@pytest_asyncio.fixture
def get_user_by_token():
    def _get(token: str):
        payload = decode_token(token)
        username = payload["sub"]
        db = next(get_db())
        return db.query(User).filter(User.username == username).first()
    return _get

@pytest.fixture
def create_test_note():
    def _create(user_id: int, title=None, content="Test Content", important=False):
        db: Session = next(get_db())
        if not title:
            title = f"Test Note {uuid.uuid4()}"
        note = Notes(
            title=title,
            content=content,
            owner_id=user_id,
            important=important
        )
        db.add(note)
        db.commit()
        db.refresh(note)
        return note 
    return _create

@pytest_asyncio.fixture
async def auth_client_with_note(create_test_user):
    user_data = create_test_user(username="user1", password="pass1")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/token", data={
            "username": user_data["username"],
            "password": "pass1"
        })
        token = response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    db: Session = next(get_db())
    note = Notes(title="Test Note", content="Test Content", owner_id=user_data["id"])
    db.add(note)
    db.commit()
    db.refresh(note)

    async_client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers=headers)
    yield async_client, note
    await async_client.aclose()

@pytest.fixture
def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(autouse=True)
def override_dependency(override_get_db):
    app.dependency_overrides[get_db] = lambda: override_get_db
    yield
    app.dependency_overrides.clear()
