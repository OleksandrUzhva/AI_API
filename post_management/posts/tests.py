from django.test import TestCase
from django.contrib.auth.models import User
from .models import Post, Comment

class PostTests(TestCase):
    def test_create_post(self):
        user = User.objects.create_user(username="testuser", password="testpassword")
        post = Post.objects.create(user=user, title="Test Post", content="Test content")
        self.assertEqual(post.title, "Test Post")

