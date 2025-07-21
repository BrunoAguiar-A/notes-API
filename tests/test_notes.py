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
async def test_post_bad_request(auth_headers):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers= auth_headers
    ) as client:
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
async def test_get_nonexistent_note(auth_headers):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers=auth_headers) as client:
        response = await client.get("/notes/999999")  # ID provavelmente inexistente

    assert response.status_code == 404

# Test retrieving the list of all notes, expects a list response
@pytest.mark.asyncio
async def test_list_notes(auth_headers):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers= auth_headers
    ) as client:
        response = await client.get("/notes/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["data"],list)

# Test retrieving a single note by its ID
@pytest.mark.asyncio
async def test_get_note_by_id(async_client, create_temp_note):
    note = create_temp_note
    #search for created note
    response = await async_client.get(f"/notes/{note['id']}")
    assert response.status_code == 200
    assert response.json()['id'] == note['id']

@pytest.mark.asyncio
async def test_list_notes_paginated_and_ordered(auth_headers):
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers = auth_headers
    ) as client:
        response = await client.get("/notes/?limit=5&offset=0&order_by=title&sort=asc")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)
        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) <= 5

        titles = [note["title"] for note in data["data"]]
        assert titles == sorted(titles)

@pytest.mark.asyncio
async def test_invalid_limit_and_offset(auth_headers):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers=auth_headers
    ) as client:
        response = await client.get("/notes/?limit=-1&offset=-5")
        assert response.status_code == 422

@pytest.mark.asyncio
async def test_invalid_order_by_field(auth_headers):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers=auth_headers) as client:
        response = await client.get("/notes/?order_by=invalid_field")
        assert response.status_code == 422

@pytest.mark.asyncio
async def test_search_query_param(auth_headers):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers=auth_headers) as client:
        response = await client.get("/notes/?q=Temporário")
        assert response.status_code == 200
        data = response.json()
        assert all("Temporário" in note["title"] or "Temporário" in note["content"] for note in data["data"])

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
async def test_update_nonexist_id(auth_headers):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers=auth_headers) as client:
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
async def test_delete_nonexistent_note(auth_headers):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers=auth_headers) as client:
        response = await client.delete("/notes/999999")
    assert response.status_code == 404

# Test deleting a note with an invalid ID format, expecting 422 validation error
@pytest.mark.asyncio
async def test_delete_invalid_id(auth_headers):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers=auth_headers) as client:
        response = await client.delete("/notes/abc")
    assert response.status_code == 422

################################### END DELETE TESTS - DELETE ###############################
################################### ACCESS TOKEN TESTS  #####################################
@pytest.mark.asyncio
async def test_login_success(async_client):
    response = await async_client.post("/token", data={
        "username": "test_user",
        "password": "test123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

@pytest.mark.asyncio
async def test_protected_route_without_token():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/notes/")
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_protected_route_with_token(async_client):
    # Token access
    login_response = await async_client.post("/token", data={
        "username": "test_user",
        "password": "test123"
    })
    token_data = login_response.json()
    access_token = token_data["access_token"]

    # Use token on header Authorization
    headers = {"Authorization": f"Bearer {access_token}"}
    response = await async_client.get("/notes/", headers=headers)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_login_invalid_credentials(async_client):
    response = await async_client.post("/token", data={
        "username": "usuario_invalido",
        "password": "senhaerrada"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid Credentials"

@pytest.mark.asyncio
async def test_protected_route_with_invalid_token():
    headers = {"Authorization": "Bearer token_invalido_aqui"}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/notes/", headers=headers)
        assert response.status_code == 401
        assert response.json()["detail"] == "Could not validate credentials"
        
@pytest.mark.asyncio
async def test_protected_route_missing_bearer_prefix(get_auth_headers):
    # The token is valid, but it is poorly shaped no "Bearer"
    valid_token = get_auth_headers["Authorization"].replace("Bearer ", "")
    headers = {"Authorization": valid_token}
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/notes/", headers=headers)
        assert response.status_code == 401
        assert "Not authenticated" in response.text or "Could not validate credentials" in response.text

################################### END ACCESS TOKEN TESTS  #################################
################################### REGISTER TESTS ##########################################

@pytest.mark.asyncio
async def test_register_success(async_client,):
    response = await async_client.post("/register", json={
        "username": "newuser",
        "password": "Strongpass123"
    })
    assert response.status_code == 201
    data = response.json()
    assert "message" in data
    assert data["username"] == "newuser"
    assert "user_id" in data


@pytest.mark.asyncio
async def test_register_missing_fields(async_client):
    response = await async_client.post("/register", json={
        "password": "1234"
    })
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_register_existing_username(async_client):
    # Cria usuário inicial
    await async_client.post("/register", json={
        "username": "dupuser",
        "password": "StrongPass123"
    })
    # Tenta criar com username repetido
    response = await async_client.post("/register", json={
        "username": "dupuser",
        "password": "StrongPass123"
    })
    assert response.status_code in (400, 409)

@pytest.mark.asyncio
async def test_register_weak_password(async_client):
    response = await async_client.post("/register", json={
        "username": "user3",
        "password": "123" 
    })
    assert response.status_code == 422

################################### END REGISTER TESTS ######################################