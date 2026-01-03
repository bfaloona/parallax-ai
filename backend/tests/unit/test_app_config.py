"""Unit tests for FastAPI app configuration.

Test Naming Convention:
    test_<functionality>_<condition>_<expected_result>

Example:
    test_cors_middleware_configured_allows_correct_origins()
"""

import pytest
from app.main import app


@pytest.mark.unit
def test_app_title_configured_correctly():
    """Test that FastAPI app has correct title."""
    assert app.title == "Parallax AI API"


@pytest.mark.unit
def test_cors_middleware_configured_exists():
    """Test that CORS middleware is configured."""
    # Check that CORSMiddleware is in the middleware stack
    middleware_classes = [m.cls.__name__ for m in app.user_middleware]
    assert "CORSMiddleware" in middleware_classes


@pytest.mark.unit
def test_app_routes_health_endpoint_exists():
    """Test that health endpoint is registered."""
    routes = [route.path for route in app.routes]
    assert "/health" in routes


@pytest.mark.unit
def test_app_routes_chat_endpoint_exists():
    """Test that chat endpoint is registered."""
    routes = [route.path for route in app.routes]
    assert "/api/chat" in routes


@pytest.mark.unit
def test_app_routes_chat_endpoint_method_is_post():
    """Test that chat endpoint accepts POST method."""
    chat_route = next((route for route in app.routes if route.path == "/api/chat"), None)
    assert chat_route is not None
    assert "POST" in chat_route.methods


@pytest.mark.unit
def test_app_routes_health_endpoint_method_is_get():
    """Test that health endpoint accepts GET method."""
    health_route = next((route for route in app.routes if route.path == "/health"), None)
    assert health_route is not None
    assert "GET" in health_route.methods
