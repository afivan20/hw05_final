import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms
from posts.models import Post, Group, Follow
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Group.objects.create(
            title='Заголовок',
            slug='test-slug',
        )
        cls.user = User.objects.create_user(username='V.Pupkin')
        cls.follower = User.objects.create_user(username='Follower')
        cls.not_follower = User.objects.create_user(username='NotFollower')
        cls.group = get_object_or_404(Group, slug='test-slug')
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif')
        cls.post = Post.objects.create(
            author=cls.user,
            pk=999,
            group=cls.group,
            text='test_text',
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user_author = get_object_or_404(User, username='V.Pupkin')
        self.author = Client()
        self.author.force_login(self.user_author)

    def test_pages_uses_correct_template(self):
        """URL-ссылка использует соответствующий шаблон."""
        cache.clear()
        templates_pages_names = {
            1: ('posts/index.html', reverse('posts:index')),
            2: (
                'posts/group_list.html',
                reverse('posts:group_list', kwargs={'slug': 'test-slug'})
            ),
            3: (
                'posts/profile.html',
                reverse('posts:profile', kwargs={'username': 'V.Pupkin'})
            ),
            4: (
                'posts/post_detail.html',
                reverse('posts:post_detail', kwargs={'post_id': 999})
            ),
            5: (
                'posts/create_post.html',
                reverse('posts:post_edit', kwargs={'post_id': 999})
            ),
            6: ('posts/create_post.html', reverse('posts:create_post'))
        }
        for key in templates_pages_names.keys():
            template, reverse_name = templates_pages_names[key]
            with self.subTest(reverse_name=reverse_name):
                response = self.author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def post_check_fields(self, post):
        self.assertEqual(
            post.author.username,
            PostsPagesTests.post.author.username
        )
        self.assertEqual(post.text, PostsPagesTests.post.text)
        self.assertEqual(post.group.title, PostsPagesTests.post.group.title)
        self.assertEqual(post.image, PostsPagesTests.post.image)
        self.assertIsNotNone(post.pub_date)

    def test_post_lists_context(self):
        """Шаблоны index, group_list, profile
         сформированы с правильным контекстом."""
        cache.clear()
        arguments = {
            'posts:index': None,
            'posts:group_list': {'slug': 'test-slug'},
            'posts:profile': {'username': 'V.Pupkin'},
        }
        for url, kwargs in arguments.items():
            with self.subTest(url=url, kwargs=kwargs):
                response = self.author.get(reverse(url, kwargs=kwargs))
                first_object = response.context.get('page_obj')[0]
                self.post_check_fields(first_object)

    def test_post_detail_context(self):
        """ Правильный контекст переданный в post_detail"""
        response = self.author.get(reverse(
            'posts:post_detail', kwargs={'post_id': '999'}
        ))
        first_object = response.context.get('post')
        self.post_check_fields(first_object)

    def test_post_create_context(self):
        """ Форма создания поста передана в контекст."""
        response = self.author.get(reverse('posts:create_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_context(self):
        """ В шаблон редактирования поста передан правильный контекст."""
        postd_id = PostsPagesTests.post.pk
        response = self.author.get(reverse('posts:post_edit', args=[postd_id]))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_follower(self):
        """Авторизованный пользователь может
        подписываться на других пользователей и удалять их из подписок."""
        self.follower = get_object_or_404(User, username='Follower')
        self.user_authorized = Client()
        self.user_authorized.force_login(self.follower)
        response = self.user_authorized.get(reverse(
            'posts:profile_follow', kwargs={'username': 'V.Pupkin'}
        ))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Follow.objects.filter(author__username='V.Pupkin').exists()
        )

    def test_unfollower(self):
        """Авторизованный пользователь может удалять
        авторов из подписок."""
        self.follower = get_object_or_404(User, username='Follower')
        Follow.objects.create(author=PostsPagesTests.user, user=self.follower)
        self.user_authorized = Client()
        self.user_authorized.force_login(self.follower)
        response_unfollow = self.user_authorized.get(reverse(
            'posts:profile_unfollow', kwargs={'username': 'V.Pupkin'}
        ))
        self.assertEqual(response_unfollow.status_code, 302)
        self.assertFalse(
            Follow.objects.filter(author__username='V.Pupkin').exists()
        )

    def test_following_context(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех, кто не подписан."""
        self.follower = get_object_or_404(User, username='Follower')
        self.user_authorized = Client()
        self.user_authorized.force_login(self.follower)
        self.response_to_follow = self.user_authorized.get(reverse(
            'posts:profile_follow', kwargs={'username': 'V.Pupkin'}
        ))
        response_follower = self.user_authorized.get(reverse(
            'posts:follow_index', kwargs=None
        ))
        post_expected = PostsPagesTests.post
        self.user_following_context = response_follower.context.get(
            'page_obj'
        )[0]
        self.user_authorized_not_follower = Client()
        self.not_follower = get_object_or_404(User, username='NotFollower')
        self.user_authorized_not_follower.force_login(self.not_follower)
        self.assertEqual(self.user_following_context.text, post_expected.text)
        response_not_follower = self.user_authorized_not_follower.get(
            reverse('posts:follow_index', kwargs=None)
        )
        self.assertEqual(len(response_not_follower.context['page_obj']), 0)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Group.objects.create(
            title='Заголовок',
            slug='test-slug',
        )
        cls.user = User.objects.create_user(username='V.Pupkin')
        cls.group = get_object_or_404(Group, slug='test-slug')
        pk = list(range(1, 14))
        posts = [Post(author=cls.user, group=cls.group, pk=pk) for pk in pk]
        Post.objects.bulk_create(posts)

    def test_first_page_contains_ten_records(self):
        """Пагинатор первая страница 10 постов."""
        cache.clear()
        arguments = {
            'posts:index': None,
            'posts:group_list': {'slug': 'test-slug'},
            'posts:profile': {'username': 'V.Pupkin'},
        }

        for url, kwargs in arguments.items():
            with self.subTest(url=url, kwargs=kwargs):
                response = self.client.get(reverse(url, kwargs=kwargs))
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        """Пагинатор вторая страница 3 поста."""
        arguments = {
            'posts:index': None,
            'posts:group_list': {'slug': 'test-slug'},
            'posts:profile': {'username': 'V.Pupkin'},
        }

        for url, kwargs in arguments.items():
            with self.subTest(url=url, kwargs=kwargs):
                response = self.client.get(
                    reverse(url, kwargs=kwargs) + '?page=2'
                )
                self.assertEqual(len(response.context['page_obj']), 3)
