import platform
import psutil
import cpuinfo
import wmi
import GPUtil
import socket
import uuid
import os
import subprocess
import winreg
import win32api
import tkinter as tk
from tkinter import ttk

def create_system_info_tab(tab_control, system_info, disks, network_info, drivers_info, vcredist_info, open_gl_info):
    """Создает вкладку с информацией о системе"""
    # Создаем вкладку с информацией о системе
    system_tab = ttk.Frame(tab_control)
    tab_control.add(system_tab, text='Информация о системе')
    
    # Создаем контейнер с прокруткой
    canvas = tk.Canvas(system_tab)
    scrollable_frame = ttk.Frame(canvas)
    
    # Настройка прокрутки
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    
    # Упаковка элементов
    canvas.pack(side="left", fill="both", expand=True)
    
    # Привязка колесика мыши
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    canvas.bind_all("<MouseWheel>", on_mousewheel)
    
    # Создаем фрейм для разделения информации на две колонки
    main_frame = ttk.Frame(scrollable_frame)
    main_frame.pack(fill="both", expand=True, padx=10, pady=5)
    
    # Левая колонка для основной информации
    left_frame = ttk.Frame(main_frame)
    left_frame.pack(side="left", fill="both", expand=True, padx=5)
    
    # Правая колонка для драйверов и дополнительной информации
    right_frame = ttk.Frame(main_frame)
    right_frame.pack(side="right", fill="both", expand=True, padx=5)
    
    # Заполняем левую колонку
    create_left_column(left_frame, system_info, disks, network_info)
    
    # Заполняем правую колонку
    create_right_column(right_frame, drivers_info, vcredist_info, open_gl_info)
    
    return system_tab

def create_left_column(left_frame, system_info, disks, network_info):
    """Создает левую колонку с основной информацией"""
    # 1. Основная информация о системе
    system_frame = ttk.LabelFrame(left_frame, text="Основная информация", padding=10)
    system_frame.pack(fill="x", pady=5)
    
    for key, value in system_info.items():
        info_frame = ttk.Frame(system_frame)
        info_frame.pack(fill="x", pady=2)
        ttk.Label(info_frame, text=f"{key}:", font=('Segoe UI', 10, 'bold')).pack(side="left", padx=5)
        ttk.Label(info_frame, text=value, font=('Segoe UI', 10)).pack(side="left", padx=5)
    
    # 2. Информация о дисках
    disks_frame = ttk.LabelFrame(left_frame, text="Диски", padding=10)
    disks_frame.pack(fill="x", pady=5)
    
    for disk in disks:
        disk_frame = ttk.Frame(disks_frame)
        disk_frame.pack(fill="x", pady=2)
        ttk.Label(disk_frame, text=f"Диск {disk['Диск']}:", font=('Segoe UI', 10, 'bold')).pack(side="left", padx=5)
        ttk.Label(disk_frame, text=f"Тип: {disk['Тип']}", font=('Segoe UI', 10)).pack(side="left", padx=5)
        ttk.Label(disk_frame, text=f"Общий объем: {disk['Общий объем']}", font=('Segoe UI', 10)).pack(side="left", padx=5)
        ttk.Label(disk_frame, text=f"Свободно: {disk['Свободно']}", font=('Segoe UI', 10)).pack(side="left", padx=5)
        ttk.Label(disk_frame, text=f"Использовано: {disk['Использовано']}", font=('Segoe UI', 10)).pack(side="left", padx=5)
    
    # 3. Информация о сети
    network_frame = ttk.LabelFrame(left_frame, text="Сеть", padding=10)
    network_frame.pack(fill="x", pady=5)
    
    for interface in network_info:
        interface_frame = ttk.Frame(network_frame)
        interface_frame.pack(fill="x", pady=2)
        ttk.Label(interface_frame, text=f"Интерфейс {interface['Интерфейс']}:", font=('Segoe UI', 10, 'bold')).pack(side="left", padx=5)
        ttk.Label(interface_frame, text=f"IP: {interface['IP']}", font=('Segoe UI', 10)).pack(side="left", padx=5)
        ttk.Label(interface_frame, text=f"Маска: {interface['Маска']}", font=('Segoe UI', 10)).pack(side="left", padx=5)

def create_right_column(right_frame, drivers_info, vcredist_info, open_gl_info):
    """Создает правую колонку с информацией о драйверах и дополнительной информацией"""
    # Информация о драйверах
    drivers_frame = ttk.LabelFrame(right_frame, text="Драйверы", padding=10)
    drivers_frame.pack(fill="both", expand=True, pady=5)
    
    # Создаем таблицу для драйверов
    drivers_tree = ttk.Treeview(drivers_frame, columns=('Имя', 'Описание', 'Версия', 'Дата', 'Производитель'), show='headings')
    drivers_tree.heading('Имя', text='Имя')
    drivers_tree.heading('Описание', text='Описание')
    drivers_tree.heading('Версия', text='Версия')
    drivers_tree.heading('Дата', text='Дата')
    drivers_tree.heading('Производитель', text='Производитель')
    
    # Настройка ширины столбцов
    drivers_tree.column('Имя', width=150)
    drivers_tree.column('Описание', width=200)
    drivers_tree.column('Версия', width=100)
    drivers_tree.column('Дата', width=100)
    drivers_tree.column('Производитель', width=150)
    
    # Добавляем скроллбар для таблицы
    drivers_scrollbar = ttk.Scrollbar(drivers_frame, orient="vertical", command=drivers_tree.yview)
    drivers_tree.configure(yscrollcommand=drivers_scrollbar.set)
    
    # Упаковка элементов
    drivers_tree.pack(side="left", fill="both", expand=True)
    drivers_scrollbar.pack(side="right", fill="y")
    
    # Добавляем все драйверы в таблицу
    for driver in drivers_info:
        if 'Ошибка' in driver:
            ttk.Label(drivers_frame, text=driver['Ошибка'], font=('Segoe UI', 10)).pack(pady=5)
            break
        drivers_tree.insert('', 'end', values=(
            driver.get('Имя', ''),
            driver.get('Описание', ''),
            driver.get('Версия', ''),
            driver.get('Дата', ''),
            driver.get('Производитель', '')
        ))
    
    # Информация о Visual C++
    vcredist_frame = ttk.LabelFrame(right_frame, text="Visual C++", padding=10)
    vcredist_frame.pack(fill="x", pady=5)
    
    for vcredist in vcredist_info:
        if 'Ошибка' in vcredist:
            ttk.Label(vcredist_frame, text=vcredist['Ошибка'], font=('Segoe UI', 10)).pack(pady=5)
            break
        vcredist_info_frame = ttk.Frame(vcredist_frame)
        vcredist_info_frame.pack(fill="x", pady=2)
        ttk.Label(vcredist_info_frame, text=f"Тип: {vcredist.get('Тип', '')}", font=('Segoe UI', 10, 'bold')).pack(side="left", padx=5)
        if 'Версия' in vcredist:
            ttk.Label(vcredist_info_frame, text=f"Версия: {vcredist.get('Версия', '')}", font=('Segoe UI', 10)).pack(side="left", padx=5)
        ttk.Label(vcredist_info_frame, text=f"Путь: {vcredist.get('Путь', '')}", font=('Segoe UI', 10)).pack(side="left", padx=5)
    
    # Информация об OpenGL
    open_gl_frame = ttk.LabelFrame(right_frame, text="OpenGL", padding=10)
    open_gl_frame.pack(fill="x", pady=5)
    
    for open_gl in open_gl_info:
        if 'Ошибка' in open_gl:
            ttk.Label(open_gl_frame, text=open_gl['Ошибка'], font=('Segoe UI', 10)).pack(pady=5)
            break
        open_gl_info_frame = ttk.Frame(open_gl_frame)
        open_gl_info_frame.pack(fill="x", pady=2)
        ttk.Label(open_gl_info_frame, text=f"Тип: {open_gl.get('Тип', '')}", font=('Segoe UI', 10, 'bold')).pack(side="left", padx=5)
        if 'Версия' in open_gl:
            ttk.Label(open_gl_info_frame, text=f"Версия: {open_gl.get('Версия', '')}", font=('Segoe UI', 10)).pack(side="left", padx=5)
        if 'Производитель' in open_gl:
            ttk.Label(open_gl_info_frame, text=f"Производитель: {open_gl.get('Производитель', '')}", font=('Segoe UI', 10)).pack(side="left", padx=5)
        if 'Рендерер' in open_gl:
            ttk.Label(open_gl_info_frame, text=f"Рендерер: {open_gl.get('Рендерер', '')}", font=('Segoe UI', 10)).pack(side="left", padx=5)

def check_open_gl():
    """Проверяет наличие и версию OpenGL"""
    try:
        # Пробуем получить информацию об OpenGL через WMI
        w = wmi.WMI()
        for video in w.Win32_VideoController():
            if video.DriverVersion:
                return [{
                    'Тип': 'OpenGL',
                    'Версия': video.DriverVersion,
                    'Производитель': video.AdapterCompatibility,
                    'Рендерер': video.Name
                }]
        return [{'Ошибка': 'Не удалось получить информацию об OpenGL'}]
    except Exception as e:
        return [{'Ошибка': f'Не удалось получить информацию об OpenGL: {str(e)}'}]

def get_system_info():
    """Получает информацию о системе, дисках и сети"""
    try:
        # Инициализация WMI
        w = wmi.WMI()
        
        # Получаем основную информацию о системе
        system_info = {
            'ОС': f"{platform.system()} {platform.release()} {platform.version()}",
            'Архитектура': platform.machine(),
            'Компьютер': platform.node(),
            'Пользователь': os.getenv('USERNAME'),
            'Процессор': platform.processor(),
            'Ядра CPU': psutil.cpu_count(logical=False),
            'Потоки CPU': psutil.cpu_count(logical=True),
            'Загрузка CPU': f"{psutil.cpu_percent()}%",
            'Всего RAM': f"{round(psutil.virtual_memory().total / (1024**3), 2)} ГБ",
            'Доступно RAM': f"{round(psutil.virtual_memory().available / (1024**3), 2)} ГБ",
            'Использовано RAM': f"{psutil.virtual_memory().percent}%"
        }
        
        # Получаем MAC-адрес
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0,2*6,2)][::-1])
        system_info['MAC-адрес'] = mac
        
        # Получаем информацию о GPU
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]  # Берем первый GPU
                system_info['GPU'] = gpu.name
                system_info['Память GPU'] = f"{gpu.memoryTotal} МБ"
                system_info['Загрузка GPU'] = f"{gpu.load*100}%"
        except:
            system_info['GPU'] = "Не удалось получить информацию"
        
        # Получаем информацию о дисках
        disks = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append({
                    'Диск': partition.device,
                    'Тип': partition.fstype,
                    'Общий объем': f"{round(usage.total / (1024**3), 2)} ГБ",
                    'Свободно': f"{round(usage.free / (1024**3), 2)} ГБ",
                    'Использовано': f"{usage.percent}%"
                })
            except:
                continue
        
        # Получаем информацию о сети
        network_info = []
        for interface_name, interface_addresses in psutil.net_if_addrs().items():
            for address in interface_addresses:
                if address.family == socket.AF_INET:  # IPv4
                    network_info.append({
                        'Интерфейс': interface_name,
                        'IP': address.address,
                        'Маска': address.netmask
                    })
        
        # Получаем информацию о драйверах
        drivers_info = []
        try:
            for driver in w.Win32_PnPSignedDriver():
                drivers_info.append({
                    'Имя': driver.DeviceName,
                    'Описание': driver.Description,
                    'Версия': driver.DriverVersion,
                    'Дата': driver.DriverDate,
                    'Производитель': driver.Manufacturer
                })
        except:
            drivers_info.append({'Ошибка': 'Не удалось получить информацию о драйверах'})
        
        # Получаем информацию о Visual C++
        vcredist_info = []
        try:
            # Проверяем наличие Visual C++ Redistributable
            vcredist_paths = [
                r"C:\Windows\System32\vcruntime140.dll",
                r"C:\Windows\System32\msvcp140.dll"
            ]
            
            for path in vcredist_paths:
                if os.path.exists(path):
                    version_info = win32api.GetFileVersionInfo(path, "\\")
                    version = f"{version_info['FileVersionMS'] / 65536}.{version_info['FileVersionMS'] % 65536}.{version_info['FileVersionLS'] / 65536}.{version_info['FileVersionLS'] % 65536}"
                    vcredist_info.append({
                        'Тип': 'Visual C++ Redistributable',
                        'Версия': version,
                        'Путь': path
                    })
            
            if not vcredist_info:
                vcredist_info.append({'Ошибка': 'Visual C++ Redistributable не найден'})
        except:
            vcredist_info.append({'Ошибка': 'Не удалось получить информацию о Visual C++'})
        
        # Получаем информацию об OpenGL
        open_gl_info = check_open_gl()
        
        return system_info, disks, network_info, drivers_info, vcredist_info, open_gl_info
        
    except Exception as e:
        return {}, [], [], [{'Ошибка': str(e)}], [{'Ошибка': str(e)}], [{'Ошибка': str(e)}] 