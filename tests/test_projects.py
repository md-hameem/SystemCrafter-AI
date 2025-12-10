"""
Tests for Projects API
"""
import pytest
from httpx import AsyncClient


async def get_auth_token(client: AsyncClient) -> str:
    """Helper to register user and get auth token."""
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "project@example.com",
            "password": "testpassword123",
        },
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "project@example.com",
            "password": "testpassword123",
        },
    )
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_create_project(client: AsyncClient):
    """Test project creation."""
    token = await get_auth_token(client)
    
    response = await client.post(
        "/api/v1/projects/",
        json={
            "name": "Test Project",
            "description": "A test project for a SaaS application that manages user subscriptions.",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_list_projects(client: AsyncClient):
    """Test listing projects."""
    token = await get_auth_token(client)
    
    # Create a project first
    await client.post(
        "/api/v1/projects/",
        json={
            "name": "Project 1",
            "description": "First test project for the system.",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    
    # List projects
    response = await client.get(
        "/api/v1/projects/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_get_project(client: AsyncClient):
    """Test getting a single project."""
    token = await get_auth_token(client)
    
    # Create project
    create_response = await client.post(
        "/api/v1/projects/",
        json={
            "name": "Get Test Project",
            "description": "A project to test the get endpoint.",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    project_id = create_response.json()["id"]
    
    # Get project
    response = await client.get(
        f"/api/v1/projects/{project_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Get Test Project"


@pytest.mark.asyncio
async def test_delete_project(client: AsyncClient):
    """Test deleting a project."""
    token = await get_auth_token(client)
    
    # Create project
    create_response = await client.post(
        "/api/v1/projects/",
        json={
            "name": "Delete Test Project",
            "description": "A project to test deletion.",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    project_id = create_response.json()["id"]
    
    # Delete project
    response = await client.delete(
        f"/api/v1/projects/{project_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 204
    
    # Verify deletion
    get_response = await client.get(
        f"/api/v1/projects/{project_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_response.status_code == 404
