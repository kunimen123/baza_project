from django.urls import path
from . import views

app_name = 'kb'

urlpatterns = [
    path('', views.ArticleListView.as_view(), name='article_list'),
    path('article/<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('article/<slug:slug>/edit/', views.article_edit, name='article_edit'),
    path('article/<slug:slug>/favorite/', views.ToggleFavoriteView.as_view(), name='article_favorite'),
    path('create/', views.article_create, name='article_create'),
    path('favorites/', views.favorites_list, name='favorites'),
    path('profile/', views.profile, name='profile'),
    path('register/', views.register, name='register'),
]