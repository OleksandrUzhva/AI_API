import pytest
from posts.models import Post, Comment
from django.utils.timezone import now, timedelta
from django.contrib.auth.models import User
from ninja.testing import TestClient
from posts.api import router

client = TestClient(router)

@pytest.fixture
def create_user(db):
    user = User.objects.create_user(username="testuser", password="password123")
    return user

@pytest.fixture
def create_post(create_user):
    post = Post.objects.create(
        user=create_user, 
        title="Test Post", 
        content="Test content"
    )
    return post

@pytest.fixture
def create_comments(create_post):
    today = now().date()
    Comment.objects.create(
        post=create_post, 
        user=create_post.user, 
        content="Test comment 1", 
        created_at=today - timedelta(days=2),
        is_blocked=False
    )
    Comment.objects.create(
        post=create_post, 
        user=create_post.user, 
        content="Test comment 2", 
        created_at=today - timedelta(days=1),
        is_blocked=True
    )

def test_comments_analytics(create_comments):
    response = client.get("/comments-daily-breakdown/", params={
        "date_from": (now() - timedelta(days=3)).date().isoformat(),
        "date_to": now().date().isoformat()
    })
    
    assert response.status_code == 200
    analytics = response.json()
    
    assert len(analytics) == 3  # 3 дня
    assert analytics[1]["total_comments"] == 1  # За день 2 комментария
    assert analytics[1]["blocked_comments"] == 1  # Один из них заблокирован