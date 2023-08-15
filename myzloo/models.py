from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.crypto import get_random_string
from django.core.validators import URLValidator
from django_filters import rest_framework as filters


class Genre(models.Model):
    genre = models.CharField(max_length=100)

    def __str__(self):
        return self.genre

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

class MusicTrack(models.Model):
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=100)
    album = models.CharField(max_length=100)
    # genre = models.CharField(max_length=50)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    release_year = models.PositiveIntegerField()
    duration_seconds = models.PositiveIntegerField(blank=False, default=0)
    cover_image_url = models.URLField(
        validators=[URLValidator()],  # Валидатор для проверки корректности URL
        null=True,  # Разрешить NULL значения
        blank=True   # Разрешить пустые значения
    )
    audio_file = models.URLField()

    def __str__(self):
        return self.title

class UserManage(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **kwargs):
        if not email:
            raise ValueError('Email должен быть обязательно передан')
        email = self.normalize_email(email=email)
        user = self.model(email=email, **kwargs)
        user.create_activation_code()
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email, password, **kwargs):
        kwargs.setdefault('is_staff', False)
        kwargs.setdefault('is_superuser', False)
        kwargs.setdefault('is_private', False)
        kwargs.setdefault('is_premium', False)
        return self._create_user(email, password, **kwargs)

    def create_superuser(self, email, password, **kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)
        kwargs.setdefault('is_active', True)
        kwargs.setdefault('is_private', True)
        kwargs.setdefault('is_premium', True)
        if kwargs.get('is_staff') is not True:
            raise ValueError('У супер юзера должно быть поле is_staff=True')
        if kwargs.get('is_superuser') is not True:
            raise ValueError('У супер юзера должно быть поле is_superuser=True')
        if kwargs.get('is_private') is not True:
            raise ValueError('У супер юзера должно быть поле is_private=True')
        if kwargs.get('is_premium') is not True:
            raise ValueError('У супер юзера должно быть поле is_premium=True')
        return self._create_user(email, password, **kwargs)

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    activation_code = models.CharField(max_length=255, blank=True)
    avatar = models.ImageField(upload_to='avatars', blank=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    objects = UserManage()
    favorites = models.ManyToManyField(MusicTrack, through='myzloo_favorites', related_name='users_favorite')

    def create_activation_code(self):
        code = get_random_string(6, allowed_chars='123456789')
        self.activation_code = code
        return code

class myzloo_favorites(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='favorites_tracks')
    track = models.ForeignKey(MusicTrack, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'track')


class ModelFilter(filters.FilterSet):
    # artist = filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = MusicTrack
        fields = ['artist']
class ModelSearch(filters.FilterSet):
    attribute = filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = MusicTrack
        fields = ['attribute']