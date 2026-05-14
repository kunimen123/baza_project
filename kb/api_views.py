from rest_framework import generics, viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from .models import Category, Tag, Article, ViewHistory
from .serializers import (
    CategorySerializer, TagSerializer,
    ArticleSerializer, ArticleWriteSerializer,
    UserSerializer,
)
from .permissions import (
    IsAuthorOrEditorOrReadOnly,
    IsAdminUserOrReadOnly,
    ArticleAdminPermission,
)
from django.contrib.auth.models import User

# ---------- Публичные / пользовательские ViewSets ----------
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.filter(is_published=True)
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrEditorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'summary', 'content']
    filterset_fields = ['category', 'tags', 'is_published']
    ordering_fields = ['created_at', 'title']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ArticleWriteSerializer
        return ArticleSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # добавить/удалить из избранного
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        article = self.get_object()
        user = request.user
        if article.favorited_by.filter(id=user.id).exists():
            article.favorited_by.remove(user)
            return Response({'status': 'unfavorited'})
        else:
            article.favorited_by.add(user)
            return Response({'status': 'favorited'})

    # Список избранного текущего пользователя
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def favorites(self, request):
        articles = Article.objects.filter(favorited_by=request.user, is_published=True)
        page = self.paginate_queryset(articles)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(articles, many=True)
        return Response(serializer.data)

    # Статьи текущего пользователя (mine)
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_articles(self, request):
        articles = Article.objects.filter(author=request.user)
        page = self.paginate_queryset(articles)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(articles, many=True)
        return Response(serializer.data)

# Профиль пользователя
class UserProfileViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]  # Все авторизованные, не только staff

    def list(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_staff': user.is_staff,
            'favorites_count': user.favorites.count(),
            'edited_articles_count': user.edited_articles.count(),
        })

# ---------- Административные ViewSets ----------
class AdminCategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUserOrReadOnly]

class AdminTagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAdminUser]

class AdminArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    permission_classes = [ArticleAdminPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['title', 'summary', 'content']
    filterset_fields = ['is_published', 'category', 'tags']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ArticleWriteSerializer
        return ArticleSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Article.objects.all()
        if not user.is_superuser:
            # как в старой админке: только свои или где редактор
            qs = qs.filter(author=user) | qs.filter(editors=user)
        return qs.distinct()

class AdminUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ['get', 'put', 'patch', 'head']

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        if 'is_staff' in request.data:
            user.is_staff = request.data['is_staff']
            user.save()
        return Response(UserSerializer(user).data)

class ViewHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ViewHistory.objects.all().order_by('-ts')
    permission_classes = [IsAdminUserOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user', 'article']
    search_fields = ['article__title', 'user__username']

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({'detail': 'Имя пользователя и пароль обязательны'}, status=400)
        
        if User.objects.filter(username=username).exists():
            return Response({'detail': 'Пользователь уже существует'}, status=400)
        
        user = User.objects.create_user(username=username, email=email, password=password)
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username
        }, status=201)