from rest_framework import serializers
from django.contrib.auth.models import User  # если кастомная модель – импортируйте её
from .models import Category, Tag, Article, ViewHistory

# Вспомогательные сериализаторы
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff']  # никогда не включайте password

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']
        read_only_fields = ['slug']
    
    def validate_name(self, value):
        if Tag.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("Тег с таким названием уже существует")
        return value
    
# Основной сериализатор статьи (для чтения списка/детализации)
class ArticleSerializer(serializers.ModelSerializer):
    category_detail = CategorySerializer(source='category', read_only=True)
    tags_detail = TagSerializer(source='tags', many=True, read_only=True)
    author_detail = UserSerializer(source='author', read_only=True)
    favorites_count = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'summary', 'content',
            'category', 'category_detail',
            'tags', 'tags_detail',
            'author', 'author_detail',
            'is_published', 'created_at', 'updated_at',
            'image',
            'editors',  # id списки
            'favorited_by',
            'favorites_count', 'is_favorited',
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at', 'author']

    def get_favorites_count(self, obj):
        return obj.favorited_by.count()

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorited_by.filter(id=request.user.id).exists()
        return False

# Отдельный сериализатор для создания/редактирования статьи (пишемые m2m поля)
class ArticleWriteSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True, required=False)
    editors = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, required=False)
    favorited_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, required=False)

    class Meta:
        model = Article
        fields = [
            'title', 'slug', 'summary', 'content',
            'category', 'tags', 'is_published',
            'editors', 'favorited_by', 'image',
        ]