import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class WindowsVoteWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Голосование за сборку Windows")
        self.window.geometry("400x550")
        
        # Список сборок Windows
        self.windows_builds = [
            "AtlasOS",
            "ReviOS",
            "SapphireOS",
            "KernelOS",
            "MakuOS",
            "FoxOS",
            "ProOS",
            "ggOS",
            "imOS",
            "xOS",
            "Nexus LiteOS",
            "PableOS",
            "SystemX",
            "GhostSpectre",
            "Flibustier"
        ]
        
        # Создаем фрейм для информации
        info_frame = ttk.Frame(self.window, padding=10)
        info_frame.pack(fill='x')
        
        ttk.Label(info_frame, 
                 text="Анонимное голосование за сборку Windows",
                 font=('Helvetica', 12, 'bold')).pack(pady=5)
        
        ttk.Label(info_frame,
                 text="Выберите одну или несколько сборок Windows.\n"
                      "Голосование полностью анонимное.\n"
                      "Вы можете убедиться в этом, просмотрев исходный код All Tweaker.",
                 wraplength=350,
                 justify='center').pack(pady=5)
        
        # Создаем фрейм для чекбоксов
        self.checkboxes_frame = ttk.Frame(self.window, padding=10)
        self.checkboxes_frame.pack(fill='both', expand=True)
        
        # Создаем переменные для чекбоксов
        self.checkbox_vars = {}
        
        # Создаем чекбоксы
        for build in self.windows_builds:
            var = tk.BooleanVar()
            self.checkbox_vars[build] = var
            ttk.Checkbutton(self.checkboxes_frame,
                          text=build,
                          variable=var).pack(anchor='w', pady=2)
        
        # Создаем фрейм для кнопок
        button_frame = ttk.Frame(self.window, padding=10)
        button_frame.pack(fill='x')
        
        # Кнопка отправки
        ttk.Button(button_frame,
                  text="Отправить голос",
                  bootstyle="success",
                  command=self.send_vote).pack(side='right', padx=5)
        
        # Кнопка отмены
        ttk.Button(button_frame,
                  text="Отмена",
                  bootstyle="secondary",
                  command=self.window.destroy).pack(side='right', padx=5)
    
    def send_vote(self):
        # Получаем выбранные сборки
        selected_builds = [build for build, var in self.checkbox_vars.items() if var.get()]
        
        if not selected_builds:
            ttk.Messagebox.show_warning(
                "Предупреждение",
                "Пожалуйста, выберите хотя бы одну сборку Windows",
                parent=self.window
            )
            return
        
        # Отправляем голос через Telegram бота
        from telemetry.telemetry_manager import TelemetryManager
        manager = TelemetryManager()
        manager.send_message("Новый голос за сборки Windows:\n" + "\n".join(selected_builds))
        print("Ваш голос успешно отправлен!")