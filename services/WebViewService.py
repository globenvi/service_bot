import os
import subprocess
from pyngrok import ngrok
from environs import Env

class WebViewService:
    def __init__(self):
        env = Env()  # Инициализация environs
        env.read_env()  # Чтение .env файла

        # Получение токена из переменных окружения с валидацией
        self.ngrok_token = env.str("NGROK_TOKEN", None)
        if not self.ngrok_token:
            raise ValueError("Ngrok token not found in environment. Please set NGROK_TOKEN in your .env file.")

        self.web_path = os.path.join(os.getcwd(), "web")
        self.create_web_folder()
        self.create_index_file()
        self.ngrok_tunnel = None

    def create_web_folder(self):
        """Создает папку web/ если она отсутствует."""
        os.makedirs(self.web_path, exist_ok=True)

    def create_index_file(self):
        """Создает стартовый index.html если он отсутствует."""
        index_file = os.path.join(self.web_path, "index.html")
        if not os.path.exists(index_file):
            with open(index_file, "w") as f:
                f.write("<html><body><h1>Welcome to WebView</h1></body></html>")

    def start_ngrok(self):
        """Запускает ngrok туннель."""
        ngrok.set_auth_token(self.ngrok_token)
        self.ngrok_tunnel = ngrok.connect(5000)
        print(f"Ngrok tunnel created: {self.ngrok_tunnel.public_url}")

    def start_server(self):
        """Запускает Flask сервер через subprocess."""
        flask_command = [
            "python",  # Команда для запуска Python
            "-m", "flask",  # Модуль Flask
            "run",  # Команда Flask
            "--host=0.0.0.0",  # Слушать все IP
            "--port=5000"  # Порт
        ]
        env = os.environ.copy()
        env["FLASK_APP"] = os.path.join(self.web_path, "index.html")  # Задаём корневой файл приложения
        self.flask_process = subprocess.Popen(flask_command, env=env)

    def start(self):
        """Запускает ngrok туннель и Flask сервер."""
        self.start_ngrok()
        self.start_server()

    def stop(self):
        """Останавливает Flask сервер и ngrok туннель."""
        if self.flask_process:
            self.flask_process.terminate()
            self.flask_process.wait()
        if self.ngrok_tunnel:
            ngrok.disconnect(self.ngrok_tunnel.public_url)
            print("Ngrok tunnel closed.")
