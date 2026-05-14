from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api_views import (
    CategoryViewSet, TagViewSet, ArticleViewSet,
    AdminCategoryViewSet, AdminTagViewSet, AdminArticleViewSet,
    AdminUserViewSet, ViewHistoryViewSet, UserProfileViewSet, RegisterView
)

public_router = DefaultRouter()
public_router.register(r'categories', CategoryViewSet, basename='category')
public_router.register(r'tags', TagViewSet, basename='tag')
public_router.register(r'articles', ArticleViewSet, basename='article')
public_router.register(r'profile', UserProfileViewSet, basename='profile')

admin_router = DefaultRouter()
admin_router.register(r'categories', AdminCategoryViewSet, basename='admin-category')
admin_router.register(r'tags', AdminTagViewSet, basename='admin-tag')
admin_router.register(r'articles', AdminArticleViewSet, basename='admin-article')
admin_router.register(r'users', AdminUserViewSet, basename='admin-user')
admin_router.register(r'history', ViewHistoryViewSet, basename='admin-history')

app_name = 'kb'

urlpatterns = [
    # Старые HTML-страницы (все без изменений, только убрал дубликат)
    path('', views.ArticleListView.as_view(), name='article_list'),
    path('article/<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('article/<slug:slug>/edit/', views.article_edit, name='article_edit'),
    path('article/<slug:slug>/favorite/', views.ToggleFavoriteView.as_view(), name='article_favorite'),
    path('create/', views.article_create, name='article_create'),
    path('favorites/', views.favorites_list, name='favorites'),
    path('profile/', views.profile, name='profile'),
    path('register/', views.register, name='register'),

    # API (новые эндпоинты для Flutter)
    path('api/', include(public_router.urls)),
    path('api/admin/', include(admin_router.urls)),
    path('api/auth/', include('rest_framework.urls')),
    path('api/register/', RegisterView.as_view(), name='register'),
]