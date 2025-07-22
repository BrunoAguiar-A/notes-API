import pytest, sys, os 
from httpx import AsyncClient, ASGITransport

from models.note import Notes
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app
from models.user import User
from database import get_db
from auth.users import get_password_hash


################################### CREATE TESTS - POST #######################################
# Test creating a new note successfully and then deletes it (cleanup)
@pytest.mark.asyncio
async def test_create_note(async_client, auth_headers):
    response = await async_client.post("/notes/", json={
        "title": "My first Note",
        "content": "Test content"
    }, headers=auth_headers)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My first Note"
    assert data["content"] == "Test content"

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
async def test_get_note_by_id(async_client, create_temp_note, auth_headers):
    note = create_temp_note
    response = await async_client.get(f"/notes/{note['id']}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == note["id"]

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

################################### END GET TESTS - GET ######################################
################################### UPDATE TESTS - UPDATE ####################################
# Test updating an existing note's title, content, and importance
@pytest.mark.asyncio
async def test_update_note(create_test_user, create_test_note, get_auth_headers):
    user_data = create_test_user(username="user_update", password="senha123")
    headers = await get_auth_headers(user_data["username"], user_data["password"])

    note = create_test_note(user_id=user_data["id"], title="Nota antiga")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", headers=headers) as client:
        response = await client.put(f"/notes/{note.id}", json={
            "title": "Note Updated",
            "content": "Content Updated",
            "important": False
        })
        assert response.status_code == 200
        updated_note = response.json()
        assert updated_note["title"] == "Note Updated"

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
async def test_update_note_without_important(auth_client_with_note):
    async_client, note = auth_client_with_note

    update_data = {
        "title": "Parcial Update",
        "content": "Partially updated content"
    }

    response = await async_client.put(f"/notes/{note.id}", json=update_data)
    assert response.status_code == 200



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
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test", 
        headers=auth_headers
    ) as client:
        response = await client.delete("/notes/999999")
    assert response.status_code == 404

# Test deleting a note with an invalid ID format, expecting 422 validation error
@pytest.mark.asyncio
async def test_delete_invalid_id(auth_headers):
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test", 
        headers=auth_headers
    ) as client:
        response = await client.delete("/notes/abc")
    assert response.status_code == 422

################################### END DELETE TESTS - DELETE ###############################
################################### ACCESS TOKEN TESTS  #####################################
@pytest.mark.asyncio
async def test_login_success(create_test_user):
    # Create user
    credentials = create_test_user(username="test_user", password="test123")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/token", data={
            "username": credentials["username"],
            "password": credentials["password"]
        })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

@pytest.mark.asyncio
async def test_protected_route_without_token():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/notes/")
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_protected_route_with_token(create_test_user):
    # Create user
    credentials = create_test_user(username="test_user", password="test123")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        login_response = await client.post("/token", data={
            "username": credentials["username"],
            "password": credentials["password"]
        })
        assert login_response.status_code == 200, f"Login falhou: {login_response.text}"
        
        token_data = login_response.json()
        assert "access_token" in token_data, f"access_token não encontrado: {token_data}"

        access_token = token_data["access_token"]

        # Use token to access protected route
        headers = {"Authorization": f"Bearer {access_token}"}
        protected_response = await client.get("/notes/", headers=headers)
        assert protected_response.status_code == 200


@pytest.mark.asyncio
async def test_login_invalid_credentials(async_client):
    response = await async_client.post("/token", data={
        "username": "invalid_user",
        "password": "invalid_psw"
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
async def test_protected_route_missing_bearer_prefix(get_auth_headers,create_test_user):
    user_data = create_test_user(username="user_update", password="senha123")
    headers = await get_auth_headers(user_data["username"], user_data["password"])
    # Remove "Bearer " on header
    valid_token = headers["Authorization"].replace("Bearer ", "")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(
            "/notes/",
            headers={"Authorization": valid_token} 
        )
    assert response.status_code == 401

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
################################### SHARED NOTES TESTS ######################################
@pytest.mark.asyncio
async def test_share_note_success(
    async_client, 
    get_auth_headers,
    create_test_user,
    get_user_by_token,
    create_test_note,
    override_get_db  
):
    db = override_get_db  

    # Creating the sender
    sender_credentials = create_test_user(username="test_user", password="test123")
    sender_headers = await get_auth_headers(sender_credentials["username"], sender_credentials["password"])
    sender_token = sender_headers["Authorization"].split(" ")[1]
    sender_user = get_user_by_token(sender_token)

    # Create note
    note = create_test_note(user_id=sender_user.id)

    # Recipient creation using the same session
    recipient_username = "recipient"
    recipient_password = "psw123"
    recipient = User(username=recipient_username, hashed_password=get_password_hash(recipient_password))
    db.add(recipient)
    db.commit()
    db.refresh(recipient)

    # Send request to share
    response = await async_client.post(f"/notes/{note.id}/share",json={
        "recipient_username": recipient_username,
        "can_edit": True
    },
    headers=sender_headers
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Note shared successfully"
################################### END SHARED NOTES TESTS ##################################