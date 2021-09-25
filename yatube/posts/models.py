from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Введите название для группы'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='slug',
        help_text='Имя группы'
    )
    description = models.TextField(
        null=True,
        verbose_name='Описание',
        help_text='Краткое описание для кого это группа'
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст',
        help_text='Введите текст'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='автор',
        help_text='Изменить авторство'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Выберите группу'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        related_name='comments',
        on_delete=models.CASCADE,
        verbose_name='Пост',
        help_text='Выберите пост',
    )
    author = models.ForeignKey(
        User,
        related_name='comments',
        on_delete=models.CASCADE,
        verbose_name='Автор',
        help_text='Выберите автора',
    )
    text = models.TextField(
        null=True,
        verbose_name='Комментарий',
        help_text='Напишите ваш комментарий...',
    )
    created = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.SET_NULL,
        null=True,
        help_text='Выберите пользователя',
        verbose_name='Пользователь',
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Подписчик',
        help_text='Выберите на кого подписан пользователь',
    )

    class Meta():
        constraints = (models.UniqueConstraint(
            fields=('user', 'author'),
            name='unique-in-module'
        ),)

    def __str__(self):
        return self.user.username
