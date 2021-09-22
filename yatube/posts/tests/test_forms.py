import shutil
import tempfile

from django.test import Client, TestCase, override_settings
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from posts.forms import PostForm
from posts.models import Post
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()
        cls.user = User.objects.create_user(username='V.Pupkin')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Модуль shutil - библиотека Python с удобными инструментами
        # для управления файлами и директориями:
        # создание, удаление, копирование, перемещение, изменение папок
        # и файлов
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user_author = get_object_or_404(User, username='V.Pupkin')
        self.author = Client()
        self.author.force_login(self.user_author)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Новый пост',
            'image': uploaded,
        }
        response = self.author.post(
            reverse('posts:create_post'),
            data=form_data
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'V.Pupkin'})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Новый пост',
                image='posts/small.gif'
            ).exists()
        )
        self.post = Post.objects.get(text='Новый пост')
        # посмотреть что лежит в <image>
        # self.assertEqual(
        # Post.objects.filter(image='posts/small.gif'), self.post.image)

    def test_edit_post(self):
        """Происходит изменение поста с <post_id> в базе данных."""
        form_data = {
            'text': 'Редактируем пост',
        }
        self.author.post(
            reverse('posts:create_post'), args=('post_id',),
            data=form_data,
        )
        self.assertTrue(
            Post.objects.filter(
                text='Редактируем пост',
            ).exists()
        )
