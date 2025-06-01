import os
import zipfile
import shutil
from datetime import datetime
import telebot

# если есть файл config.py, то используем его, иначе используем config_for_github.py
if os.path.exists('config.py'):
    from .config import verify_and_get_credentials
else:
    from .config_for_github import verify_and_get_credentials

class TelemetryManager:
    def __init__(self):
        pass  # Никакой инициализации не требуется

    def get_credentials(self):
        return verify_and_get_credentials()

    def send_telegram(self, file_path):
        # Получаем декодированные значения
        TOKEN, chat_id = self.get_credentials()
        bot = telebot.TeleBot(TOKEN)
        try:
            with open(file_path, 'rb') as f:
                # Определяем тип файла для сообщения
                filename = os.path.basename(file_path)
                if filename.endswith('.zip'):
                    # Проверяем, является ли это архивом телеметрии
                    if 'telemetry' in filename.lower():
                        caption = f'Телеметрия: {filename}'
                    else:
                        caption = f'Архив с лог файлами: {filename}\n\n'
                elif filename.endswith('.log'):
                    caption = f'Лог файл: {filename}'
                else:
                    caption = f'Файл: {filename}'
                    
                bot.send_document(chat_id, f, caption=caption)
        except Exception as e:
            print(f'Ошибка отправки в Telegram: {e}')

    def send_message(self, message):
        """
        Отправляет текстовое сообщение через Telegram
        
        Args:
            message (str): Текст сообщения для отправки
            
        Returns:
            bool: True если сообщение успешно отправлено, False в случае ошибки
        """
        try:
            TOKEN, chat_id = self.get_credentials()
            bot = telebot.TeleBot(TOKEN)
            bot.send_message(chat_id, message)
            return True
        except Exception as e:
            print(f'Ошибка отправки сообщения в Telegram: {e}')
            return False

    def collect_telemetry_data(self):
        username = os.getenv('USERNAME', 'unknown')
        current_date = datetime.now().strftime('%Y-%m-%d')
        seconds = datetime.now().strftime('%H-%M-%S')
        archive_name = f'Telemetry-{username}-{current_date}-{seconds}.zip'
        temp_dir = 'user_data//temp'
        os.makedirs(temp_dir, exist_ok=True)
        try:
            # Копируем все файлы из user_data\logs, кроме temp
            for root, dirs, files in os.walk('user_data//logs'):
                if 'temp' in root:
                    continue
                rel_path = os.path.relpath(root, 'user_data')
                temp_path = os.path.join(temp_dir, rel_path)
                os.makedirs(temp_path, exist_ok=True)
                for file in files:
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(temp_path, file)
                    shutil.copy2(src_file, dst_file)
            # Создаём архив
            archive_path = f'user_data//{archive_name}'
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname)
            # Отправляем архив в Telegram
            self.send_telegram(archive_path)
            # Удаляем временные файлы
            shutil.rmtree(temp_dir)
            os.remove(archive_path)
            return True
        except Exception as e:
            print(f"Ошибка при сборе телеметрии: {str(e)}")
            return False 