from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    summary = models.CharField(max_length=500, blank=True)
    content = models.TextField()
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL, related_name='articles')
    tags = models.ManyToManyField(Tag, blank=True, related_name='articles')
    author = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Избранное: ManyToMany к юзеру
    favorited_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='favorites', blank=True)
    # кто редактировал когда — ManyToMany пользователей, если нужно
    edited_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='edited_articles', blank=True)
    editors = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='can_edit_articles', blank=True)
    image = models.ImageField(upload_to='article_images/', null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:240]
            slug = base
            i = 1
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('kb:article_detail', args=[self.slug])


class ViewHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='view_history')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='view_history')
    ts = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-ts']
