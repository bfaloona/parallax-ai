"""Unit tests for health check endpoint.

Test Naming Convention:
    test_<functionality>_<condition>_<expected_result>

Example:
    test_health_endpoint_valid_request_returns_200()
"""

import pytest
from httpx import AsyncClient


@pytest.mark.unit
@pytest.mark.asyncio
async def test_health_endpoint_valid_request_returns_200(client: AsyncClient):
    """Test that health endpoint returns 200 on valid request."""
    response = await client.get("/health")

    assert response.status_code == 200


@pytest.mark.unit
@pytest.mark.asyncio
async def test_health_endpoint_valid_request_returns_correct_json_structure(client: AsyncClient):
    """Test that health endpoint returns correct JSON structure."""
    response = await client.get("/health")

    json_data = response.json()
    assert "status" in json_data
    assert isinstance(json_data["status"], str)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_health_endpoint_valid_request_returns_ok_status(client: AsyncClient):
    """Test that health endpoint returns 'ok' status."""
    response = await client.get("/health")

    json_data = response.json()
    assert json_data["status"] == "ok"
