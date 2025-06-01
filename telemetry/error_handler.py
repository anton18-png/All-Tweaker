import sys
import os
import traceback
from datetime import datetime
import telebot

# если есть файл config.py, то используем его, иначе используем config_for_github.py
if os.path.exists('config.py'):
    from .config import verify_and_get_credentials
else:
    from .config_for_github import verify_and_get_credentials

def handle_top_level_error():
    """Обработчик ошибок на верхнем уровне программы"""
    try:
        # Получаем информацию об ошибке
        exc_type, exc_value, exc_traceback = sys.exc_info()
        
        # Проверяем наличие ошибки
        if exc_type is None:
            return
            
        # Формируем сообщение об ошибке
        error_message = f"⚠️ Критическая ошибка при запуске All Tweaker!\n\n"
        
        # Безопасно получаем информацию об ошибке
        try:
            error_type = exc_type.__name__ if exc_type and hasattr(exc_type, '__name__') else str(exc_type)
            error_message += f"Тип ошибки: {error_type}\n"
        except:
            error_message += "Тип ошибки: Неизвестная ошибка\n"
            
        try:
            error_message += f"Сообщение: {str(exc_value)}\n"
        except:
            error_message += "Сообщение: Не удалось получить текст ошибки\n"
            
        error_message += f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        error_message += f"Пользователь: {os.getenv('USERNAME', 'unknown')}\n\n"
        
        # Добавляем стек вызовов
        try:
            if exc_traceback:
                error_message += "Стек вызовов:\n"
                error_message += "".join(traceback.format_tb(exc_traceback))
        except:
            error_message += "Не удалось получить стек вызовов\n"
        
        # Отправляем сообщение в Telegram
        send_telegram_message(error_message)
        
        # Собираем и отправляем логи
        try:
            send_logs()
        except Exception as log_error:
            print(f"Ошибка при отправке логов: {str(log_error)}")
        
    except Exception as e:
        # Если произошла ошибка при отправке уведомления
        print(f"Ошибка при отправке уведомления: {str(e)}")
        try:
            # Пробуем отправить хотя бы базовое сообщение об ошибке
            token, chat_id = verify_and_get_credentials()
            bot = telebot.TeleBot(token)
            bot.send_message(chat_id, f"⚠️ Произошла ошибка в All Tweaker, но не удалось получить детали: {str(e)}")
        except:
            pass

def send_telegram_message(message):
    """Отправляет сообщение в Telegram"""
    try:
        token, chat_id = verify_and_get_credentials()
        
        # Отправляем сообщение
        bot = telebot.TeleBot(token)
        bot.send_message(chat_id, message)
    except Exception as e:
        print(f"Ошибка при отправке сообщения в Telegram: {str(e)}")

def send_logs():
    """Собирает и отправляет логи в Telegram"""
    try:
        import zipfile
        import shutil
        from datetime import datetime
        
        # Создаем временную директорию
        temp_dir = os.path.join('telemetry', 'temp_logs')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Копируем все файлы из директории logs
        log_dir = os.path.join('telemetry', 'logs')
        if os.path.exists(log_dir):
            for root, dirs, files in os.walk(log_dir):
                for file in files:
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(temp_dir, file)
                    shutil.copy2(src_file, dst_file)
        
        # Создаем архив
        username = os.getenv('USERNAME', 'unknown')
        archive_name = f'{username}_logs_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.zip'
        archive_path = os.path.join('telemetry', archive_name)
        
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)
        
        # Отправляем архив
        send_telegram_file(archive_path)
        
        # Удаляем временные файлы
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        if os.path.exists(archive_path):
            os.remove(archive_path)
            
    except Exception as e:
        print(f"Ошибка при отправке логов: {str(e)}")

def send_telegram_file(file_path):
    """Отправляет файл в Telegram"""
    try:
        token, chat_id = verify_and_get_credentials()
        
        # Отправляем файл
        bot = telebot.TeleBot(token)
        with open(file_path, 'rb') as f:
            bot.send_document(chat_id, f, caption=f'Логи: {os.path.basename(file_path)}')
    except Exception as e:
        print(f"Ошибка при отправке файла в Telegram: {str(e)}") 