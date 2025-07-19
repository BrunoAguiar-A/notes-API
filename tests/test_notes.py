import pytest, sys, os 
from httpx import AsyncClient, ASGITransport
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app  

@pytest.mark.asyncio
async def test_create_note():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/notes/", json={
            "title": "Minha Primeira Nota",
            "content": "Conteúdo de teste"
        })

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Minha Primeira Nota"
    assert data["content"] == "Conteúdo de teste"

@pytest.mark.asyncio
async def test_list_notes():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/notes/")
    assert response.status_code == 200
    assert isinstance(response.json(),list)


@pytest.mark.asyncio
async def test_get_note_by_id():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create new note for GET
        create_response = await client.post("/notes/", json={
            "title": "Note For search",
            "content": "Content"
        })
        note_id = create_response.json()["id"]
        #search for created note
        response = await client.get(f"/notes/{note_id}")
   
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == note_id
    assert data["title"] == "Note For search"


@pytest.mark.asyncio
async def test_update_note():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create new note for UPDATE
        create_response = await client.post("/notes/", json={
            "title": "Note for update",
            "content": "Content for update"
        })
        note_id = create_response.json()["id"]
        # UPDATE note
        update_response = await client.put(f"/notes/{note_id}", json={
            "title": "Note Updated",
            "content": "Content Updated"
        })

    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["title"] == "Note Updated"
    assert updated["content"] == "Content Updated"


@pytest.mark.asyncio
async def test_update_note():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create new note for DELETE
        create_response = await client.post("/notes/", json={
            "title": "Note for DELETE",
            "content": "Content for DELETE"
        })
        note_id = create_response.json()["id"]
        delete_responde = await client.delete(f"/notes/{note_id}")
        # DELETE note
        assert delete_responde.status_code == 204

        # Confirm note don't exist 
        get_response = await client.get(f"/notes/{note_id}")
        assert get_response.status_code == 404


