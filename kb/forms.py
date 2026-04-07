from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import RegexValidator, EmailValidator

from .models import Article, Tag, Category

User = get_user_model()

# Валидатор для текста: только буквы, цифры и пробелы
alnum_validator = RegexValidator(
    regex=r'^[A-Za-z0-9\s]+$',
    message='Можно использовать только буквы, цифры и пробелы.'
)


class RegisterForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        validators=[alnum_validator],
        help_text="Используйте только буквы и цифры."
    )
    email = forms.EmailField(
        required=False,
        validators=[EmailValidator(message="Введите корректный email.")]
    )
    password1 = forms.CharField(
        label="Пароль",
        strip=False,
        min_length=6,
        widget=forms.PasswordInput,
        help_text="Пароль должен содержать хотя бы одну букву и одну цифру.",
        validators=[
            RegexValidator(
                regex=r'^(?=.*[A-Za-z])(?=.*\d).+$',
                message='Пароль должен содержать хотя бы одну букву и одну цифру.'
            )
        ]
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        strip=False,
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, min_length=6, required=True)


class ArticleForm(forms.ModelForm):
    title = forms.CharField(
        max_length=255,
        label="Заголовок",
        widget=forms.TextInput(attrs={'placeholder': 'Название статьи'})
    )

    summary = forms.CharField(
        label="Краткое описание",
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False
    )

    content = forms.CharField(
        required=True,
        min_length=20,
        widget=forms.Textarea(attrs={'rows': 12, 'placeholder': 'Текст статьи (минимум 20 символов)'}),
        label="Текст статьи"
    )

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label="Категория"
    )

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        label="Теги"
    )

    is_published = forms.BooleanField(
        required=False,
        label="Опубликовать статью"
    )

    class Meta:
        model = Article
        fields = ['title', 'category', 'tags', 'summary', 'content', 'image', 'is_published']