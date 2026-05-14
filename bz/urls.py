from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from rest_framework.authtoken.views import obtain_auth_token
from django.views.static import serve
from django.urls import re_path

urlpatterns = [
    # Админка Django (единственный раз)
    path('admin/', admin.site.urls),

    # Старые маршруты логина/логаута (оставлены, как у тебя было)
    path('login/', auth_views.LoginView.as_view(template_name='kb/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/register/'), name='logout'),

    # Все старые HTML-маршруты + API (подключаем kb.urls с namespace)
    # namespace='kb' обязателен для работы reverse('kb:...') в шаблонах
    path('', include('kb.urls', namespace='kb')),

    # Токен-эндпоинт для Flutter (оставляем)
    path('api-token-auth/', obtain_auth_token),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]    