from django.db import migrations

def create_superuser(apps, schema_editor):
    # Получаем модель User через apps.get_model, чтобы не было конфликтов
    User = apps.get_model('auth', 'User')
    
    # Проверяем, существует ли уже суперпользователь с таким именем
    if not User.objects.filter(username='admin').exists():
        # Создаем суперпользователя
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='12345'
        )
        print("✅ Суперпользователь 'admin' создан!")
    else:
        print("ℹ️ Суперпользователь 'admin' уже существует.")

class Migration(migrations.Migration):
    # Эта строка — самая важная! Указываем зависимости от предыдущих миграций.
    dependencies = [
        ('kb', '0004_fix_articles'),  # Замени на название последней существующей миграции в папке kb/migrations/
    ]

    # Указываем список операций, которые нужно выполнить
    operations = [
        migrations.RunPython(create_superuser),
    ]