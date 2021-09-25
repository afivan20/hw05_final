from django.contrib.auth import get_user_model
from django.test import TestCase
from ..models import Group, Post, Comment, Follow

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.author = User.objects.create_user(username='FollowMe')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа123',
        )

    def test_post_model_have_correct_object_name(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        post = PostModelTest.post
        post_obj_name = post.text[:15]
        self.assertEqual(post_obj_name, str(post))

    def test_post_verbose_name(self):
        """verbose_name модели Post совпадает с ожидаемыми."""
        post = PostModelTest.post
        verbose_text = post._meta.get_field('text').verbose_name
        verbose_date = post._meta.get_field('pub_date').verbose_name
        verbose_author = post._meta.get_field('author').verbose_name
        verbose_group = post._meta.get_field('group').verbose_name
        self.assertEqual(verbose_text, 'Текст')
        self.assertEqual(verbose_date, 'Дата публикации')
        self.assertEqual(verbose_author, 'автор')
        self.assertEqual(verbose_group, 'Группа')

    def test_post_help_text(self):
        """help_text модели Post совпадает с ожидаемыми."""
        post = PostModelTest.post
        help_text = post._meta.get_field('text').help_text
        help_author = post._meta.get_field('author').help_text
        help_group = post._meta.get_field('group').help_text
        self.assertEqual(help_text, 'Введите текст')
        self.assertEqual(help_author, 'Изменить авторство')
        self.assertEqual(help_group, 'Выберите группу')


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_group_model_have_correct_object_name(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_group_verbose_name(self):
        """verbose_name модели Group совпадает с ожидаемыми."""
        group = GroupModelTest.group
        verbose_names = {
            'title': 'Название',
            'slug': 'slug',
            'description': 'Описание',
        }
        for field, verbose_name in verbose_names.items():
            with self.subTest(verbose_name=verbose_name, field=field):
                verbose_name = group._meta.get_field(field).verbose_name
                self.assertEqual(verbose_name, verbose_name)

    def test_group_help_text(self):
        """help_text модели Group совпадает с ожидаемыми."""
        group = GroupModelTest.group
        help_texts = {
            'title': 'Введите название группы',
            'slug': 'Имя группы',
            'description': 'Краткое описание для кого эта группа'
        }
        for field, help_text in help_texts.items():
            with self.subTest(help_text=help_text, field=field):
                help_text = group._meta.get_field(field).help_text
                self.assertEqual(help_text, help_text)


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.author = User.objects.create_user(username='FollowMe')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа123',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Comment'
        )

    def test_comment_model_have_correct_object_name(self):
        """Проверяем, что у модели Comment корректно работает __str__."""
        comment = CommentModelTest.comment
        expected_str = comment.text[:15]
        self.assertEqual(expected_str, str(comment))

    def test_comment_verbose_name(self):
        """verbose_name модели Comment совпадает с ожидаемыми."""
        comment = CommentModelTest.comment
        verbose_names = {
            'post': 'Пост',
            'author': 'Автор',
            'text': 'Комментарий',
        }
        for field, verbose_name in verbose_names.items():
            with self.subTest(verbose_name=verbose_name, field=field):
                verbose_name = comment._meta.get_field(field).verbose_name
                self.assertEqual(verbose_name, verbose_name)

    def test_comment_help_text(self):
        """help_text модели Comment совпадает с ожидаемыми."""
        comment = CommentModelTest.comment
        help_texts = {
            'post': 'Выберите пост',
            'author': 'Выберите автора',
            'text': 'Напишите ваш комментарий...'
        }
        for field, help_text in help_texts.items():
            with self.subTest(help_text=help_text, field=field):
                help_text = comment._meta.get_field(field).help_text
                self.assertEqual(help_text, help_text)


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='User')
        cls.author = User.objects.create_user(username='Author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовая группа123',
        )
        cls.follow = Follow.objects.create(
            author=cls.author,
            user=cls.user
        )

    def test_follow_model_have_correct_object_name(self):
        """Проверяем, что у модели Comment корректно работает __str__."""
        follow = FollowModelTest.follow
        expected_str = follow.user.username
        self.assertEqual(expected_str, str(follow))

    def test_follow_verbose_name(self):
        """verbose_name модели Follow совпадает с ожидаемыми."""
        follow = FollowModelTest.follow
        verbose_names = {
            'user': 'Пользователь',
            'author': 'Подписчик',
        }
        for field, verbose_name in verbose_names.items():
            with self.subTest(verbose_name=verbose_name, field=field):
                verbose_name = follow._meta.get_field(field).verbose_name
                self.assertEqual(verbose_name, verbose_name)

    def test_follow_help_text(self):
        """help_text модели Follow совпадает с ожидаемыми."""
        follow = FollowModelTest.follow
        help_texts = {
            'user': 'Выберите пользователя',
            'author': 'Выберите на кого подписан пользователь',
        }
        for field, help_text in help_texts.items():
            with self.subTest(help_text=help_text, field=field):
                help_text = follow._meta.get_field(field).help_text
                self.assertEqual(help_text, help_text)
