from rest_framework.permissions import BasePermission, SAFE_METHODS

def can_edit_static(user, article):
    if not user.is_authenticated:
        return False
    if user.is_staff:
        return True
    if article.author == user:
        return True
    return user in article.editors.all()

class IsAuthorOrEditorOrReadOnly(BasePermission):
    """Разрешает редактирование автору, редактору или админу. Остальным только чтение."""
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return can_edit_static(request.user, obj)

class IsAdminUserOrReadOnly(BasePermission):
    """Для админских действий: полный доступ у is_staff, остальным только чтение (если надо)"""
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_staff

# Для админского ArticleViewSet ограничим видимость как в старой админке
class ArticleAdminPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        # edit/delete только если есть права (is_staff или автор/редактор)
        return can_edit_static(request.user, obj)