import os
import logging
from datetime import datetime
import traceback
import sys
import shutil
import zipfile
import configparser
import platform
import winreg
from .telemetry_manager import TelemetryManager
import main

telemetry_override = None  # None = по настройкам, True = включить, False = отключить

# Обработка аргументов командной строки для управления телеметрией
TELEMETRY_OFF_FLAGS = {'-nt', '-n', '--no-telemetry'}
TELEMETRY_ON_FLAGS = {'-t', '-d', '-debugging', '--telemetry'}
for arg in sys.argv[1:]:
    if arg.lower() in TELEMETRY_OFF_FLAGS:
        telemetry_override = False
        print("[CLI] Telemetry will be DISABLED by command-line flag.")
        break
    elif arg.lower() in TELEMETRY_ON_FLAGS:
        telemetry_override = True
        print("[CLI] Telemetry will be ENABLED by command-line flag.")
        break

def is_telemetry_enabled():
    """Проверяет, включена ли отправка телеметрии в настройках или переопределена через аргумент"""
    global telemetry_override
    if telemetry_override is not None:
        return telemetry_override
    try:
        config = configparser.ConfigParser()
        config.read('user_data//settings.ini', encoding='cp1251')
        return config.getboolean('Telemetry', 'send_on_close', fallback=True)
    except Exception as e:
        print(f"Error checking telemetry settings: {e}")
        return True  # По умолчанию включено, если не удалось прочитать настройки

def get_windows_version():
    """Получает подробную информацию о версии Windows"""
    try:
        # Получаем информацию о выпуске Windows
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
        product_name = winreg.QueryValueEx(key, "ProductName")[0]
        release_id = winreg.QueryValueEx(key, "DisplayVersion")[0]
        current_build = winreg.QueryValueEx(key, "CurrentBuild")[0]
        ubr = winreg.QueryValueEx(key, "UBR")[0]
        winreg.CloseKey(key)
        
        # Формируем строку с информацией
        version_info = f"{product_name} (Build {current_build}.{ubr})"
        if release_id:
            version_info += f" {release_id}"
            
        return version_info
    except Exception:
        return f"Windows {platform.release()}"

class Logger:
    def __init__(self):
        # Создаем директорию для логов, если она не существует
        self.log_dir = os.path.join('user_data', 'logs')
        os.makedirs(self.log_dir, exist_ok=True)

        # Получаем имя пользователя
        username = os.getenv('USERNAME', 'unknown')
        
        # Формируем имя файла лога с текущей датой и временем
        current_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        self.log_file = os.path.join(self.log_dir, f'{username}_All_Tweaker_{main.version}_{current_datetime}.log')
        
        # Настраиваем логгер
        self.logger = logging.getLogger('AllTweaker')
        self.logger.setLevel(logging.INFO)
        
        # Создаем форматтер для логов
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', 
                                    datefmt='%Y-%m-%d %H:%M:%S')
        
        # Создаем обработчик для записи в файл
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Создаем обработчик для вывода в консоль
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Перехватываем необработанные исключения
        sys.excepthook = self.handle_exception
        
        # Флаг для отслеживания отправки логов
        self.logs_sent = False
        
    def send_logs_to_telegram(self):
        """Отправляет все логи из папки user_data//logs в Telegram"""
        try:
            # Проверяем настройки телеметрии
            if not is_telemetry_enabled():
                return
                
            # Проверяем, не были ли логи уже отправлены
            if self.logs_sent:
                return
                
            manager = TelemetryManager()
            # Создаем временную директорию для архивации
            temp_dir = os.path.join('user_data', 'temp_logs')
            os.makedirs(temp_dir, exist_ok=True)
            
            # Копируем все файлы из директории logs
            for root, dirs, files in os.walk(self.log_dir):
                for file in files:
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(temp_dir, file)
                    shutil.copy2(src_file, dst_file)
            
            # Получаем имя пользователя
            username = os.getenv('USERNAME', 'unknown')
            
            # Создаем архив с именем пользователя
            archive_name = f'{username}_logs_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.zip'
            archive_path = os.path.join('user_data', archive_name)
            
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname)
            
            # Отправляем архив
            if 0 == 1: # не хочу отправлять архив
                manager.send_telegram(archive_path)
            
            # Удаляем временные файлы
            shutil.rmtree(temp_dir)
            os.remove(archive_path)
            
            # Устанавливаем флаг отправки
            self.logs_sent = True
            
            return True
        except Exception as e:
            print(f"Ошибка при отправке логов: {str(e)}")
            return False

    def handle_exception(self, exc_type, exc_value, exc_traceback):
        """Обработчик необработанных исключений"""
        if issubclass(exc_type, KeyboardInterrupt):
            # Не логируем прерывание пользователем
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
            
        # Логируем ошибку
        self.logger.error("Необработанное исключение:", exc_info=(exc_type, exc_value, exc_traceback))
        
        # Отправляем уведомление об ошибке в Telegram
        try:
            # Проверяем настройки телеметрии
            if not is_telemetry_enabled():
                return
                
            manager = TelemetryManager()
            error_message = f"⚠️ Критическая ошибка в All Tweaker! {main.version}\n\n"
            error_message += f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            error_message += f"👤 Пользователь: #{os.getenv('USERNAME', 'unknown')}\n\n"
            error_message += f"Тип ошибки: {exc_type.__name__}\n"
            error_message += f"📝 Сообщение: {str(exc_value)}\n"
            error_message += "Подробности в прикрепленном логе."
            
            # Отправляем сообщение об ошибке
            manager.send_message(error_message)
            
            # Отправляем логи только если они еще не были отправлены
            if not self.logs_sent:
                self.send_logs_to_telegram()
        except Exception as e:
            print(f"Ошибка при отправке уведомления об ошибке: {str(e)}")

    def send_error_notification(self, error_message, exc_info=None):
        """Отправляет уведомление об ошибке в Telegram"""
        try:
            # Проверяем настройки телеметрии
            if not is_telemetry_enabled():
                return
                
            manager = TelemetryManager()
            # Формируем полное сообщение об ошибке
            full_message = f"⚠️ Ошибка в All Tweaker!\n\n"
            full_message += f"📝 Сообщение: {error_message}\n\n"
            full_message += f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            full_message += f"👤 Пользователь: #{os.getenv('USERNAME', 'unknown')}\n"
            full_message += f"🐍 Версия All Tweaker: {main.version}\n"
            full_message += f"📊 Всего логов: {len(os.listdir(self.log_dir))}\n"

            if exc_info:
                full_message += f"\nДетали ошибки:\n{exc_info}"
            
            # Отправляем сообщение
            manager.send_message(full_message)
            
            # Отправляем логи только если они еще не были отправлены
            if not self.logs_sent:
                self.send_logs_to_telegram()
        except Exception as e:
            print(f"Ошибка при отправке уведомления: {str(e)}")

    def log_error(self, message, exc_info=None):
        """Логирует ошибку и отправляет уведомление в Telegram"""
        if exc_info:
            self.logger.error(f"{message}\n{traceback.format_exc()}")
        else:
            self.logger.error(message)
        
        # Отправляем уведомление об ошибке
        self.send_error_notification(message, exc_info)
        
    def log_tweak_execution(self, tweak_name, tweak_path):
        """Логирует выполнение твика"""
        self.logger.info(f"Запущен твик: {tweak_name} (путь: {tweak_path})")
        
    def log_settings_change(self, setting_name, old_value, new_value):
        """Логирует изменение настроек"""
        self.logger.info(f"Изменена настройка '{setting_name}': {old_value} -> {new_value}")
        
    def log_python_error(self, error_msg, exc_info=None):
        """Логирование ошибок Python"""
        self.logger.error(f"Ошибка Python: {error_msg}", exc_info=exc_info)
        
    def log_program_start(self):
        """Логирует запуск программы и отправляет логи в Telegram"""
        self.logger.info("Программа запущена")
        
        # Отправляем сообщение о запуске
        try:
            if is_telemetry_enabled():
                from telemetry.telemetry_manager import TelemetryManager
                manager = TelemetryManager()
                
                success_message = f"🚀 All Tweaker {main.version} успешно запущен!\n\n"
                success_message += f"⏰ Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                success_message += f"👤 Пользователь: #{os.getenv('USERNAME', 'unknown')}\n\n"
                success_message += f"💻 Операционная система: {get_windows_version()}\n"
                success_message += f"📊 Всего логов: {len(os.listdir(self.log_dir))}\n"

                manager.send_message(success_message)
        except Exception as e:
            self.logger.error(f"Ошибка при отправке сообщения о запуске: {str(e)}")
        
        # Отправляем логи в Telegram только если они еще не были отправлены
        if not self.logs_sent:
            self.send_logs_to_telegram()
        
    def log_program_exit(self):
        """Логирует завершение программы"""
        self.logger.info("Программа завершена")
        # удаляем __pycache__ рекурсивно во всех поддиректориях
        # for root, dirs, files in os.walk('.'):
        #     for dir in dirs:
        #         if dir == '__pycache__':
        #             shutil.rmtree(os.path.join(root, dir))