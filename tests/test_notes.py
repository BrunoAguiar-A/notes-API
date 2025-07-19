import pytest, sys, os 
from httpx import AsyncClient, ASGITransport
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app


################################### CREATE TESTS - POST ###################################
# Test creating a new note successfully and then deletes it (cleanup)
@pytest.mark.asyncio
async def test_create_note(async_client):
    response = await async_client.post("/notes/", json={
        "title": "Minha Primeira Nota",
        "content": "Conteúdo de teste"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Minha Primeira Nota"
    assert data["content"] == "Conteúdo de teste"

    # Cleanup
    await async_client.delete(f"/notes/{data['id']}")

# Test creating a note with forbidden word in the title, expecting 400 bad request
@pytest.mark.asyncio
async def test_post_bad_request():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/notes/", json={
            "title": "forbidden word",
            "content": "Create Content"
        })

    assert response.status_code == 400

@pytest.mark.asyncio
async def test_create_note_empty_payload(async_client):
    response = await async_client.post("/notes/", json={})
    assert response.status_code == 422

# Test updating a note with invalid/missing fields, expecting validation error (422)
@pytest.mark.asyncio
async def test_create_note_with_missing_fields(async_client, create_temp_note):
    note = create_temp_note

    response = await async_client.put(f"/notes/{note['id']}", json={
        "title": "", # invalid
    })

    assert response.status_code == 422


################################### END CREATE TESTS - POST ###################################
################################### GET TESTS - GET ###########################################

# Test retrieving a note with a non-existent ID, expecting 404 not found
@pytest.mark.asyncio
async def test_get_nonexistent_note():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/notes/999999")  # ID provavelmente inexistente

    assert response.status_code == 404

# Test retrieving the list of all notes, expects a list response
@pytest.mark.asyncio
async def test_list_notes():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/notes/")
    assert response.status_code == 200
    assert isinstance(response.json(),list)

# Test retrieving a single note by its ID
@pytest.mark.asyncio
async def test_get_note_by_id(async_client, create_temp_note):
    note = create_temp_note
    #search for created note
    response = await async_client.get(f"/notes/{note['id']}")
    assert response.status_code == 200
    assert response.json()['id'] == note['id']

################################### END GET TESTS - GET #####################################
################################### UPDATE TESTS - UPDATE ###################################
# Test updating an existing note's title, content, and importance
@pytest.mark.asyncio
async def test_update_note(async_client, create_temp_note):
    note = create_temp_note

    update_response = await async_client.put(f"/notes/{note['id']}", json={
        "title": "Note Updated",
        "content": "Content Updated",
        "important": "False"
    })
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["title"] == "Note Updated"
    assert updated["content"] == "Content Updated"

# Test updating a note with a non-existent ID, expecting 404 not found
@pytest.mark.asyncio
async def test_update_nonexist_id():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.put("/notes/4256", json={ # ID not exist
            "title": "New Title Updated",
            "content": "New content Test"
        })
    assert response.status_code == 404

# Test updating a note with invalid/missing title field, expecting validation error (422)
@pytest.mark.asyncio
async def test_update_note_with_missing_fields(async_client, create_temp_note):
    note = create_temp_note

    #  Trying to update note with incorrect content (Ex. empty title)
    response = await async_client.put(f"/notes/{note['id']}", json={
        "title": "", #invalid
        "content": "Updated Content"
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_update_note_without_important(async_client, create_temp_note):
    note = create_temp_note

    update_data = {
        "title": "Parcial Update",
        "content": "Conteúdo atualizado parcialmente"
        #whidout important
    }

    response = await async_client.put(f"/notes/{note['id']}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["content"] == update_data["content"]
    assert "important" in data  # exist


################################### END UPDATE TESTS - UPDATE ###############################
################################### DELETE TESTS - DELETE ###################################
# Test deleting a note and confirming it no longer exists
@pytest.mark.asyncio
async def test_delete_notes(async_client, create_temp_note):
    note = create_temp_note

    delete_responde = await async_client.delete(f"/notes/{note['id']}")
    # DELETE note
    assert delete_responde.status_code == 204
    # Confirm note not exist
    get_response = await async_client.get(f"/notes/{note['id']}")
    assert get_response.status_code == 404


# Test deleting a note with a non-existent ID, expecting 404 not found
@pytest.mark.asyncio
async def test_delete_nonexistent_note():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.delete("/notes/999999")
    assert response.status_code == 404

# Test deleting a note with an invalid ID format, expecting 422 validation error
@pytest.mark.asyncio
async def test_delete_invalid_id():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.delete("/notes/abc")
    assert response.status_code == 422

################################### END DELETE TESTS - DELETE ###############################
