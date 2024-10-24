import pytest
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from posts.models import Post
from ninja.testing import TestClient
from posts.api import router

client = TestClient(router)

@pytest.fixture
def create_user(db):
    user = User.objects.create_user(username="testuser", password="password123")
    return user

@pytest.fixture
def auth_token(create_user):
    refresh = RefreshToken.for_user(create_user)
    return {
        "Authorization": f"Bearer {str(refresh.access_token)}"
    }

def test_create_post(auth_token):
    payload = {
        "title": "Test Post",
        "content": "This is a test post content."
    }

    response = client.post("/posts/", json=payload, headers=auth_token)  # Убедитесь, что путь соответствует вашему API

    assert response.status_code == 201  # Ожидаем статус 201
    assert response.json()["message"] == "Ваш пост успешно размещен."
    assert Post.objects.filter(title="Test Post").exists()

def test_create_post_without_title(auth_token):
    payload = {
        "content": "This is a test post content."
    }

    response = client.post("/posts/", json=payload, headers=auth_token)

    assert response.status_code == 400  # Ожидаем статус 400
    assert "title" in response.json()["errors"]  # Убедитесь, что поле title обрабатывается как обязательное
