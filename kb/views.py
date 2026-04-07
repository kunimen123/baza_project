from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.urls import reverse
from .models import Article, Tag, Category, ViewHistory
from .forms import RegisterForm, ArticleForm, LoginForm
from django.contrib.auth import login
from django.http import HttpResponseForbidden
from django.contrib import messages

# Простой permission helper (можно расширить)
def can_edit(user, article):
    if not user.is_authenticated:
        return False
    # Автор своей статьи
    if article.author == user:
        return True
    # Назначенный редактор
    if user in article.editors.all():
        return True
    # Админ может всё
    if user.is_staff:
        return True

    return False

class ArticleListView(ListView):
    model = Article
    template_name = 'kb/article_list.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        qs = Article.objects.filter(is_published=True)
        q = self.request.GET.get('q')
        tag = self.request.GET.get('tag')
        mine = self.request.GET.get('mine')
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(content__icontains=q) | Q(summary__icontains=q))
        if tag:
            qs = qs.filter(tags__slug=tag)
        if mine and self.request.user.is_authenticated:
            qs = qs.filter(author=self.request.user)

        return qs.prefetch_related('tags')
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['tags'] = Tag.objects.all()
        ctx['current_tag'] = self.request.GET.get('tag', '')
        ctx['q'] = self.request.GET.get('q', '')
        ctx['mine'] = self.request.GET.get('mine', '')
        return ctx

class ArticleDetailView(DetailView):
    model = Article
    template_name = 'kb/article_detail.html'
    context_object_name = 'article'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        # Логирование просмотра — оставляем как есть
        if request.user.is_authenticated:
            ViewHistory.objects.create(user=request.user, article=self.object)

        context = self.get_context_data(object=self.object)

        # --- РЕКОМЕНДАЦИИ (НОВЫЙ ВАРИАНТ) ---
        context['recs'] = self.get_recommendations(self.object)

        return self.render_to_response(context)

    def get_recommendations(self, article):
        """
        Рекомендации по приоритетам:
        1) Совпадающие теги
        2) Совпадающая категория
        3) Любые статьи
        """

    # --- 1. Рекомендации по тегам ---
        tag_ids = article.tags.values_list('id', flat=True)
        qs = Article.objects.filter(is_published=True)\
                            .exclude(pk=article.pk)\
                            .filter(tags__in=tag_ids)\
                            .distinct()

        if qs.count() >= 5:
            return qs[:5]

        # --- 2. Рекомендации по категории ---
        qs_cat = Article.objects.filter(
            is_published=True,
            category=article.category
        ).exclude(pk=article.pk).distinct()

        if qs_cat.exists():
            # объединяем найденные ранее + по категории
            combined = (qs | qs_cat).distinct()
            if combined.count() >= 5:
                return combined[:5]

        # --- 3. Фоллбэк — любые статьи ---
        fallback = Article.objects.filter(is_published=True)\
                                .exclude(pk=article.pk)[:5]

        return fallback


class ToggleFavoriteView(LoginRequiredMixin, View):
    def post(self, request, slug):
        article = get_object_or_404(Article, slug=slug)
        user = request.user
        if article.favorited_by.filter(pk=user.pk).exists():
            article.favorited_by.remove(user)
        else:
            article.favorited_by.add(user)
        return redirect(article.get_absolute_url())


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('kb:article_list')
        else:
            messages.error(request, "Проверьте правильность заполнения формы.")    
    else:
        form = RegisterForm()
    return render(request, 'kb/register.html', {'form': form})

@login_required
def profile(request):
    user = request.user
    fav_count = user.favorites.count() if hasattr(user, 'favorites') else 0
    edited_count = user.edited_articles.count() if hasattr(user, 'edited_articles') else 0
    return render(request, 'kb/profile.html', {
        'user': user,
        'fav_count': fav_count,
        'edited_count': edited_count,
    })

@login_required
def article_edit(request, slug):
    article = get_object_or_404(Article, slug=slug)
    
    if not can_edit(request.user, article):
        messages.error(request, "У вас нет прав на редактирование этой статьи.")
        return redirect('kb:article_detail', slug=slug)

    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            art = form.save()
            art.edited_by.add(request.user)
            messages.success(request, "Статья успешно сохранена.")
            return redirect('kb:article_detail', slug=art.slug)
        else:
            messages.error(request, "Проверьте правильность заполнения формы.")
    else:
        form = ArticleForm(instance=article)

    return render(request, 'kb/article_edit.html', {'form': form, 'article': article})


@login_required
def favorites_list(request):
    articles = Article.objects.filter(favorited_by=request.user).order_by('-created_at')
    return render(request, 'kb/favorites.html', {'articles': articles})

@login_required
def article_create(request):
    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.is_published = False            
            article.save()
            form.save_m2m()
            messages.success(request, "Статья успешно создана.")
            return redirect(article.get_absolute_url())
        else:
            messages.error(request, "Проверьте правильность заполнения формы.")
    else:
        form = ArticleForm()

    return render(request, 'kb/article_create.html', {'form': form})