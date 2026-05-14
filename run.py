from waitress import serve
from bz.wsgi import application  # вместо bz_project — имя твоего проекта

if __name__ == '__main__':
    print(" Сервер запущен на http://localhost:8000")
    serve(application, host='127.0.0.1', port=8000)