from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from posts.models import Post, Group

User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Group.objects.create(
            title='Заголовок',
            slug='test-slug',
        )
        cls.user = User.objects.create_user(username='V.Pupkin')
        cls.group = get_object_or_404(Group, slug='test-slug')
        cls.post = Post.objects.create(
            author=cls.user,
            pk=999,
            group=cls.group,
            text='test_text',
            
        )

    def setUp(self):
        self.user_author = get_object_or_404(User, username='V.Pupkin')
        self.author = Client()
        self.author.force_login(self.user_author)

    def test_pages_uses_correct_template(self):
        """URL-ссылка использует соответствующий шаблон."""
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
        post_expected = PostsPagesTests.post
        self.post_author_0 = post.author.username
        self.post_text_0 = post.text
        self.post_group_0 = post.group.title
        self.post_date_0 = post.pub_date
        self.image = post.image
        self.assertEqual(self.post_author_0, post_expected.author.username)
        self.assertEqual(self.post_text_0, post_expected.text)
        self.assertEqual(self.post_group_0, post_expected.group.title)
        self.assertEqual(self.image, post_expected.image)
        self.assertIsNotNone(self.post_date_0)

    def test_post_lists_context(self):
        """Шаблоны index, group_list, profile
         сформированы с правильным контекстом."""
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
