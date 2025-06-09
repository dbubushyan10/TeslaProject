import sys
import os
from pathlib import Path
import webbrowser
import threading
import socket
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Определение базового пути для ресурсов
if getattr(sys, 'frozen', False):
    # Режим EXE (PyInstaller)
    BASE_DIR = Path(sys._MEIPASS)
else:
    # Режим разработки
    BASE_DIR = Path(__file__).parent

app = FastAPI()

# Подключаем маршруты
from app.routers import main as main_router
from app.routers import theory
from app.routers import calculations
from app.routers import reference

app.include_router(main_router.router)
app.include_router(theory.router)
app.include_router(calculations.router)
app.include_router(reference.router)

# Монтирование статических файлов с правильным путем
static_dir = BASE_DIR / "app" / "static"
app.mount(
    "/static", 
    StaticFiles(directory=static_dir), 
    name="static"
)

def find_free_port(start_port=8080):
    """Находит свободный порт начиная с заданного"""
    port = start_port
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return port
            port += 1

def open_browser(port):
    """Открывает браузер с заданным портом"""
    webbrowser.open(f"http://localhost:{port}")

if __name__ == "__main__":
    try:
        port = find_free_port()
        
        # Запуск браузера в отдельном потоке
        threading.Thread(
            target=open_browser,
            args=(port,),
            daemon=True
        ).start()
        
        # Запуск Uvicorn
        import uvicorn
        uvicorn.run(
            app, 
            host="127.0.0.1", 
            port=port, 
            reload=False,  # Отключаем reload для EXE
            log_level="info"
        )
        
    except Exception as e:
        import traceback
        print(f"Ошибка при запуске: {e}")
        traceback.print_exc()
        input("Нажмите Enter для выхода...")