from django.contrib import admin
from .models import Category, Tag, Article, ViewHistory
from django.contrib.auth import get_user_model

User = get_user_model()

# ===========================
# Category
# ===========================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ('name',)
    search_fields = ('name',)


# ===========================
# Tag
# ===========================
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ('name',)
    search_fields = ('name',)


# ===========================
# Article
# ===========================
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'is_published', 'created_at')
    list_filter = ('is_published', 'category', 'tags')
    search_fields = ('title', 'summary', 'content')
    prepopulated_fields = {"slug": ("title",)}
    
    # Удобный выбор нескольких элементов
    filter_horizontal = ('tags', 'favorited_by', 'editors')
    
    # Логическая группировка полей
    fieldsets = (
        ("Основное", {
            'fields': ('title', 'slug', 'summary', 'content', 'category', 'tags')
        }),
        ("Автор и статус публикации", {
            'fields': ('author', 'is_published')
        }),
        ("Редакторы", {
            'fields': ('editors',),
            'description': "Выберите пользователей, которые имеют право редактировать статью."
        }),
        ("Избранное", {
            'fields': ('favorited_by',),
            'description': "Пользователи, которые добавили статью в избранное."
        }),
    )
    
    # Ограничение видимых статей для обычных пользователей
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(editors=request.user) | qs.filter(author=request.user)
    
    # Автоматически назначать автора при создании статьи
    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        super().save_model(request, obj, form, change)


# ===========================
# ViewHistory
# ===========================
@admin.register(ViewHistory)
class ViewHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'ts')
    list_filter = ('user', 'article')
    search_fields = ('article__title', 'user__username')
