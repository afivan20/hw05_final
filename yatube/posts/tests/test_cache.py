from django.test import TestCase
from posts.models import Post
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='User')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Cached',
        )

    def test_cache_index(self):
        """Кеширования главной страницы."""
        response_initial = self.client.get(reverse('posts:index'))
        index_initial = response_initial.content
        post = Post.objects.get(text='Cached')
        post.delete()
        response_cached = self.client.get(reverse('posts:index'))
        index_cached = response_cached.content
        self.assertEqual(index_initial, index_cached)
