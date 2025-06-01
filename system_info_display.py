import platform
import psutil
import socket
import wmi
import GPUtil
from datetime import datetime
import tkinter as tk
from tkinter import ttk
import os  # Модуль для работы с файловой системой, например, для создания директорий
import tkinter as tk  # Основной модуль для работы с графическим интерфейсом
from tkinter import ttk  # Расширение Tkinter для более красивых виджетов
from tkinter import StringVar  # Модель для строковых переменных, используется для привязки к виджетам
from tkinter import filedialog  # Модуль для диалогов выбора файлов
import ttkbootstrap as ttk  # Дополнительное оформление для Tkinter, предоставляет стили и темы
import subprocess  # Модуль для выполнения внешних процессов, используется для выполнения скриптов
import getpass  # Модуль для работы с именами пользователей, хотя здесь явно не используется
from datetime import datetime  # Модуль для работы с датой и временем, используется для создания уникальных имен файлов
import configparser  # Модуль для работы с конфигурационными файлами, здесь для чтения и записи настроек
import tkinter.colorchooser  # Добавить в секцию импортов
import json  # Для работы с JSON файлами
import shutil  # Для копирования файлов
from telemetry.logger import Logger  # Импортируем класс Logger
from system_info import get_system_info, create_system_info_tab  # Импортируем функцию для получения системной информации
import telebot  # Для отправки сообщений через Telegram
import tkinter.messagebox as messagebox  # Добавляем модуль для вывода сообщений
import re # Для работы с регулярными выражениями
import threading # Для работы с потоками
import time # Для работы с временем
import zipfile # Для работы с архивами
import logging
from gpt import GPTClient  # Импортируем GPTClient
from pathlib import Path
import backup_tab

def create_system_info_display(system_info):
    """
    Creates and displays system information with detailed metrics and controls.
    
    Args:
        system_info: The parent frame where the system information will be displayed
    """
    try:
        # --- Новый layout на grid ---
        main_container = ttk.Frame(system_info)
        main_container.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        main_container.grid_columnconfigure(0, weight=1)
        main_container.grid_columnconfigure(1, weight=0)

        # Левый блок: вся системная информация
        info_block = ttk.Frame(main_container)
        info_block.grid(row=0, column=0, sticky='nw', padx=0, pady=0)

        # --- Весь ваш layout CPU, GPU, Disk, Net, RAM теперь размещайте внутри info_block ---
        # CPU
        cpu_frame = ttk.LabelFrame(info_block, text="CPU", padding=2)
        cpu_frame.grid(row=0, column=0, sticky='nsew', padx=2, pady=2)

        # GPU
        gpu_frame = ttk.LabelFrame(info_block, text="GPU", padding=2)
        gpu_frame.grid(row=0, column=1, sticky='nsew', padx=2, pady=2)

        # Disk
        disk_frame = ttk.LabelFrame(info_block, text="Диск C:", padding=2)
        disk_frame.grid(row=1, column=0, sticky='nsew', padx=2, pady=2)

        # Network
        network_frame = ttk.LabelFrame(info_block, text="Сеть", padding=2)
        network_frame.grid(row=1, column=1, sticky='nsew', padx=2, pady=2)

        # RAM (на всю ширину)
        ram_frame = ttk.LabelFrame(info_block, text="Оперативная память", padding=2)
        ram_frame.grid(row=2, column=0, columnspan=2, sticky='ew', padx=2, pady=2)

        # Processes and Services Section
        processes_frame = ttk.LabelFrame(info_block, text="Процессы и службы", padding=2)
        processes_frame.grid(row=3, column=0, columnspan=2, sticky='ew', padx=2, pady=2)

        # Настроить веса для равномерного распределения
        info_block.grid_columnconfigure(0, weight=1)
        info_block.grid_columnconfigure(1, weight=1)
        info_block.grid_rowconfigure(0, weight=1)
        info_block.grid_rowconfigure(1, weight=1)

        # CPU Section
        cpu_grid = ttk.Frame(cpu_frame)
        cpu_grid.pack(fill='x')
        cpu_usage_meter = ttk.Meter(cpu_grid, metersize=120, padding=2, amountused=0, amounttotal=100, metertype="full", subtext="Загрузка", textright="%", bootstyle="info", stripethickness=10, textfont=('Segoe UI', 12, 'bold'))
        cpu_usage_meter.grid(row=0, column=0, padx=2, pady=1)
        cpu_temp_meter = ttk.Meter(cpu_grid, metersize=120, padding=2, amountused=0, amounttotal=100, metertype="full", subtext="Температура", textright="°C", bootstyle="danger", stripethickness=10, textfont=('Segoe UI', 12, 'bold'))
        cpu_temp_meter.grid(row=0, column=1, padx=2, pady=1)
        cpu_info_frame = ttk.Frame(cpu_grid)
        cpu_info_frame.grid(row=1, column=0, columnspan=2, padx=2, pady=1)
        cpu_freq_label = ttk.Label(cpu_info_frame, text="Частота: -- MHz", font=('Segoe UI', 10))
        cpu_freq_label.pack(side='left', padx=2)
        cpu_power_label = ttk.Label(cpu_info_frame, text="Мощность: -- W", font=('Segoe UI', 10))
        cpu_power_label.pack(side='left', padx=2)

        # Disk Section
        disk_grid = ttk.Frame(disk_frame)
        disk_grid.pack(fill='x')
        disk_usage_meter = ttk.Meter(disk_grid, metersize=120, padding=2, amountused=0, amounttotal=100, metertype="full", subtext="Использовано", textright="%", bootstyle="warning", stripethickness=10, textfont=('Segoe UI', 12, 'bold'))
        disk_usage_meter.grid(row=0, column=0, padx=2, pady=1)
        disk_info_frame = ttk.Frame(disk_grid)
        disk_info_frame.grid(row=0, column=1, padx=2, pady=1, sticky='n')
        disk_total_label = ttk.Label(disk_info_frame, text="Общий объем: -- GB", font=('Segoe UI', 10))
        disk_total_label.pack(anchor='w')
        disk_free_label = ttk.Label(disk_info_frame, text="Свободно: -- GB", font=('Segoe UI', 10))
        disk_free_label.pack(anchor='w')
        disk_temp_label = ttk.Label(disk_info_frame, text="Временные файлы: -- GB", font=('Segoe UI', 10))
        disk_temp_label.pack(anchor='w')
        disk_cleanup_btn = ttk.Button(disk_info_frame, text="Очистить мусор", command=lambda: cleanup_disk(), bootstyle="outline")
        disk_cleanup_btn.pack(anchor='center', pady=(10, 0))
        disk_name_label = ttk.Label(disk_frame, text="Локальный диск (C:)", font=('Segoe UI', 10))
        disk_name_label.pack(anchor='center', pady=(0, 1))

        # GPU Section
        gpu_grid = ttk.Frame(gpu_frame)
        gpu_grid.pack(fill='x')
        gpu_usage_meter = ttk.Meter(gpu_grid, metersize=120, padding=2, amountused=0, amounttotal=100, metertype="full", subtext="Загрузка", textright="%", bootstyle="info", stripethickness=10, textfont=('Segoe UI', 12, 'bold'))
        gpu_usage_meter.grid(row=0, column=0, padx=2, pady=1)
        gpu_temp_meter = ttk.Meter(gpu_grid, metersize=120, padding=2, amountused=0, amounttotal=100, metertype="full", subtext="Температура", textright="°C", bootstyle="danger", stripethickness=10, textfont=('Segoe UI', 12, 'bold'))
        gpu_temp_meter.grid(row=0, column=1, padx=2, pady=1)
        gpu_info_frame = ttk.Frame(gpu_grid)
        gpu_info_frame.grid(row=1, column=0, columnspan=2, padx=2, pady=1)
        gpu_core_label = ttk.Label(gpu_info_frame, text="Частота ядра: -- MHz", font=('Segoe UI', 10))
        gpu_core_label.pack(side='left', padx=2)
        gpu_mem_label = ttk.Label(gpu_info_frame, text="Частота памяти: -- MHz", font=('Segoe UI', 10))
        gpu_mem_label.pack(side='left', padx=2)

        # Network Section
        network_speed_meter = ttk.Meter(network_frame, metersize=120, padding=2, amountused=0, amounttotal=100, metertype="full", subtext="Скорость", textright="Mbps", bootstyle="primary", stripethickness=10, textfont=('Segoe UI', 12, 'bold'))
        network_speed_meter.pack(padx=2, pady=1)
        network_info_frame = ttk.Frame(network_frame)
        network_info_frame.pack(fill='x', pady=1)
        download_label = ttk.Label(network_info_frame, text="Прием: -- Mbps", font=('Segoe UI', 10))
        download_label.pack(side='left', padx=2)
        upload_label = ttk.Label(network_info_frame, text="Отправка: -- Mbps", font=('Segoe UI', 10))
        upload_label.pack(side='left', padx=2)

        # RAM Section
        ram_grid = ttk.Frame(ram_frame)
        ram_grid.pack(fill='x')
        ram_info_frame = ttk.Frame(ram_grid)
        ram_info_frame.pack(fill='x', pady=1)
        ram_total_label = ttk.Label(ram_info_frame, text="Всего: -- GB", font=('Segoe UI', 10))
        ram_total_label.pack(side='left', padx=1)
        ram_used_label = ttk.Label(ram_info_frame, text="Использовано: -- GB", font=('Segoe UI', 10))
        ram_used_label.pack(side='left', padx=1)
        ram_buttons_frame = ttk.Frame(ram_frame)
        ram_buttons_frame.pack(fill='x', pady=1, side='right')
        ram_cache_btn = ttk.Button(ram_buttons_frame, text="Очистить кэш", command=lambda: clear_ram_cache(), bootstyle="outline")
        ram_cache_btn.pack(side='left', padx=1)
        ram_full_btn = ttk.Button(ram_buttons_frame, text="Полная очистка", command=lambda: clear_ram_full(), bootstyle="outline")
        ram_full_btn.pack(side='left', padx=1)
        ram_standby_btn = ttk.Button(ram_buttons_frame, text="Очистить RAM", command=lambda: clear_ram_standby(), bootstyle="outline")
        ram_standby_btn.pack(side='left', padx=1)

        # Processes and Services Section
        processes_info_frame = ttk.Frame(processes_frame)
        processes_info_frame.pack(fill='x', pady=1)

        # Создаем фрейм для таблицы и скроллбара
        tree_frame = ttk.Frame(processes_frame)
        tree_frame.pack(fill='both', expand=True, pady=2)

        # Создаем Treeview для процессов
        processes_tree = ttk.Treeview(tree_frame, height=5, columns=('PID', 'Name', 'CPU', 'Memory'), show='headings')
        processes_tree.heading('PID', text='PID')
        processes_tree.heading('Name', text='Название')
        processes_tree.heading('CPU', text='CPU %')
        processes_tree.heading('Memory', text='Память (MB)')
        processes_tree.column('PID', width=70)
        processes_tree.column('Name', width=200)
        processes_tree.column('CPU', width=70)
        processes_tree.column('Memory', width=100)

        # Добавляем вертикальный скроллбар
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=processes_tree.yview)
        processes_tree.configure(yscrollcommand=scrollbar.set)

        # Размещаем таблицу и скроллбар
        processes_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Увеличиваем количество отображаемых процессов до 10
        processes_tree.configure(height=10)

        # Создаем метки для общей информации
        stats_frame = ttk.Frame(processes_frame)
        stats_frame.pack(fill='x', pady=2)
        
        total_processes_label = ttk.Label(stats_frame, text="Всего процессов: 0", font=('Segoe UI', 10))
        total_processes_label.pack(side='left', padx=5)
        
        total_services_label = ttk.Label(stats_frame, text="Запущено служб: 0", font=('Segoe UI', 10))
        total_services_label.pack(side='left', padx=5)
        
        total_ram_usage_label = ttk.Label(stats_frame, text="Использование ОЗУ: 0%", font=('Segoe UI', 10))
        total_ram_usage_label.pack(side='left', padx=5)

        def get_cpu_info():
            try:
                # CPU Usage
                cpu_percent = psutil.cpu_percent()
                cpu_usage_meter.configure(amountused=cpu_percent)
                
                # CPU Temperature (requires OpenHardwareMonitor or similar)
                try:
                    w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
                    temperature_infos = w.Sensor()
                    for sensor in temperature_infos:
                        if sensor.SensorType == 'Temperature' and 'CPU' in sensor.Name:
                            cpu_temp_meter.configure(amountused=sensor.Value)
                            break
                except:
                    pass
                
                # CPU Frequency
                cpu_freq = psutil.cpu_freq()
                if cpu_freq:
                    cpu_freq_label.configure(text=f"Частота: {int(cpu_freq.current)} MHz")
                
                # CPU Power (requires additional tools)
                try:
                    w = wmi.WMI(namespace="root\\OpenHardwareMonitor")
                    power_infos = w.Sensor()
                    for sensor in power_infos:
                        if sensor.SensorType == 'Power' and 'CPU' in sensor.Name:
                            cpu_power_label.configure(text=f"Мощность: {sensor.Value:.1f} W")
                            break
                except:
                    pass
            except:
                pass

        def get_gpu_info():
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    # GPU Usage
                    gpu_usage_meter.configure(amountused=gpu.load * 100)
                    # GPU Temperature
                    gpu_temp_meter.configure(amountused=gpu.temperature)
                    # GPU Core Clock
                    gpu_core_label.configure(text=f"Частота ядра: {gpu.memoryClock} MHz")
                    # GPU Memory Clock
                    gpu_mem_label.configure(text=f"Частота памяти: {gpu.memoryClock} MHz")
            except:
                pass

        def get_disk_info():
            try:
                disk = psutil.disk_usage('C:\\')
                # Disk Usage
                disk_usage_meter.configure(amountused=disk.percent)
                # Disk Info
                disk_total_label.configure(text=f"Общий объем: {disk.total / (1024**3):.1f} GB")
                disk_free_label.configure(text=f"Свободно: {disk.free / (1024**3):.1f} GB")
                
                # Calculate temp files size
                temp_size = 0
                for root, dirs, files in os.walk(os.environ.get('TEMP')):
                    for file in files:
                        try:
                            temp_size += os.path.getsize(os.path.join(root, file))
                        except:
                            pass
                disk_temp_label.configure(text=f"Временные файлы: {temp_size / (1024**3):.1f} GB")
            except:
                pass

        def get_network_speed():
            try:
                # Get initial network stats
                net_io = psutil.net_io_counters()
                time.sleep(1)
                net_io_2 = psutil.net_io_counters()
                
                # Calculate speeds in Mbps
                download_speed = (net_io_2.bytes_recv - net_io.bytes_recv) * 8 / 1000000
                upload_speed = (net_io_2.bytes_sent - net_io.bytes_sent) * 8 / 1000000
                
                # Update meter with total speed
                total_speed = download_speed + upload_speed
                network_speed_meter.configure(amountused=min(total_speed, 100))
                
                # Update labels
                download_label.configure(text=f"Прием: {download_speed:.1f} Mbps")
                upload_label.configure(text=f"Отправка: {upload_speed:.1f} Mbps")
            except:
                pass

        def get_ram_info():
            try:
                ram = psutil.virtual_memory()
                # RAM Info
                ram_total_label.configure(text=f"Всего: {ram.total / (1024**3):.1f} GB")
                ram_used_label.configure(text=f"Использовано: {ram.used / (1024**3):.1f} GB")
            except:
                pass

        def get_processes_info():
            try:
                # Очищаем текущие данные
                for item in processes_tree.get_children():
                    processes_tree.delete(item)
                
                # Получаем список процессов
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                    try:
                        pinfo = proc.info
                        memory_mb = pinfo['memory_info'].rss / (1024 * 1024)
                        processes.append((
                            pinfo['pid'],
                            pinfo['name'],
                            pinfo['cpu_percent'],
                            memory_mb
                        ))
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass

                # Сортируем по использованию CPU
                processes.sort(key=lambda x: x[2], reverse=True)

                # Показываем топ 10 процессов
                for i, (pid, name, cpu, memory) in enumerate(processes[:10]):
                    processes_tree.insert('', 'end', values=(
                        pid,
                        name,
                        f"{cpu:.1f}",
                        f"{memory:.1f}"
                    ))

                # Обновляем статистику
                total_processes_label.configure(text=f"Всего процессов: {len(processes)}")
                
                # Получаем количество запущенных служб
                services = [s for s in psutil.win_service_iter() if s.status() == 'running']
                total_services_label.configure(text=f"Запущено служб: {len(services)}")
                
                # Обновляем информацию об использовании ОЗУ
                memory = psutil.virtual_memory()
                total_ram_usage_label.configure(text=f"Использование ОЗУ: {memory.percent}%")
                
            except Exception as e:
                print(f"Ошибка при обновлении информации о процессах: {e}")

        def cleanup_disk():
            try:
                # Clean temp files
                temp_dir = os.environ.get('TEMP')
                for item in os.listdir(temp_dir):
                    try:
                        item_path = os.path.join(temp_dir, item)
                        if os.path.isfile(item_path):
                            os.unlink(item_path)
                        elif os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                    except:
                        pass
                get_disk_info()  # Refresh disk info
            except:
                pass

        def clear_ram_cache():
            try:
                # Clear system cache
                # os.system('powershell -Command "Clear-RecycleBin -Force"')
                # os.system('powershell -Command "Remove-Item -Path $env:TEMP\* -Recurse -Force"')
                get_ram_info()  # Refresh RAM info
            except:
                pass

        def clear_ram_full():
            try:
                # Full RAM cleanup
                # os.system('powershell -Command "Clear-RecycleBin -Force"')
                # os.system('powershell -Command "Remove-Item -Path $env:TEMP\* -Recurse -Force"')
                # os.system('powershell -Command "Stop-Process -Name explorer -Force; Start-Process explorer"')
                get_ram_info()  # Refresh RAM info
            except:
                pass

        def clear_ram_standby():
            try:
                # Clear standby list
                # os.system('powershell -Command "EmptyStandbyList.exe workingsets"')
                get_ram_info()  # Refresh RAM info
            except:
                pass

        def update_all():
            get_cpu_info()
            get_gpu_info()
            get_disk_info()
            get_network_speed()
            get_ram_info()
            get_processes_info()  # Добавляем обновление информации о процессах
            # system_info.after(1000, update_all) # Обновление информации каждые 1 секунду
            # обновление информации о системе каждый час
            system_info.after(3600000, update_all) # 3600000 миллисекунд = 1 час

        # Start updates
        update_all()

    except Exception as e:
        print(f"Ошибка при получении информации о системе: {e}")
        error_label = ttk.Label(system_info,
                              text=f"Не удалось получить информацию о системе: {e}",
                              font=('Segoe UI', 10),
                              foreground='red')
        error_label.pack(fill='x') 