from django.test import Client, TestCase
from posts.models import Follow, Post
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.urls import reverse

User = get_user_model()


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Follower')
        cls.user = User.objects.create_user(username='NotFollower')
        cls.author = User.objects.create_user(username='Author')
        cls.post = Post.objects.create(
            author=cls.author,
            text='Follow me!!!',
        )

    def setUp(self):
        cache.clear()
        self.user = get_object_or_404(User, username='Follower')
        self.not_follower = get_object_or_404(User, username='NotFollower')
        self.user_authorized = Client()
        self.user_authorized.force_login(self.user)
        self.user_authorized_not_follower = Client()
        self.user_authorized_not_follower.force_login(self.not_follower)

    def test_follower(self):
        """Авторизованный пользователь может
        подписываться на других пользователей и удалять их из подписок."""
        response = self.user_authorized.get(reverse(
            'posts:profile_follow', kwargs={'username': 'Author'}
        ))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Follow.objects.filter(author__username='Author').exists()
        )
        response_unfollow = self.user_authorized.get(reverse(
            'posts:profile_unfollow', kwargs={'username': 'Author'}
        ))
        self.assertEqual(response_unfollow.status_code, 302)
        self.assertFalse(
            Follow.objects.filter(author__username='Author').exists()
        )

    def test_following_context(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех, кто не подписан."""
        self.response_to_follow = self.user_authorized.get(reverse(
            'posts:profile_follow', kwargs={'username': 'Author'}
        ))
        response_follower = self.user_authorized.get(reverse(
            'posts:follow_index', kwargs=None
        ))
        post_expected = FollowTests.post
        self.user_following_context = response_follower.context.get(
            'page_obj'
        )[0]
        self.assertEqual(self.user_following_context.text, post_expected.text)
        response_not_follower = self.user_authorized_not_follower.get(
            reverse('posts:follow_index', kwargs=None)
        )
        self.assertEqual(len(response_not_follower.context['page_obj']), 0)
