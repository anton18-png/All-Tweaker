import os
import tkinter as tk
from tkinter import ttk, messagebox
import shutil
import subprocess
from datetime import datetime

def create_registry_backup():
    try:
        # Create backup directory with timestamp
        backup_dir = os.path.join(os.getcwd(), "Backup", f"RegistryBackup_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}")
        os.makedirs(backup_dir, exist_ok=True)
        
        # Export registry hives
        registry_hives = {
            "HKLM": "hklm.reg",
            "HKCU": "hkcu.reg",
            "HKCR": "hkcr.reg",
            "HKCC": "hkcc.reg",
            "HKU": "hku.reg"
        }
        
        for hive, filename in registry_hives.items():
            subprocess.run(["reg", "export", hive, os.path.join(backup_dir, filename)], check=True)
        
        messagebox.showinfo("Успех", f"Резервная копия реестра создана в:\n{backup_dir}")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось создать резервную копию реестра:\n{str(e)}")

def update_backup_list(backup_list):
    """Обновляет список бэкапов в интерфейсе"""
    if not backup_list:
        return
        
    # Очищаем список перед обновлением
    backup_list.delete(0, tk.END)
    
    # Проверяем наличие директории с бэкапами
    backup_dir = os.path.join(os.getcwd(), "Backup")
    if not os.path.exists(backup_dir):
        return
        
    # Получаем список всех элементов в директории
    try:
        items = os.listdir(backup_dir)
    except Exception as e:
        print(f"Ошибка при чтении директории бэкапов: {e}")
        return
        
    # Разделяем директории и файлы
    dir_backups = [d for d in items 
                   if os.path.isdir(os.path.join(backup_dir, d)) 
                   and d.startswith("RegistryBackup_")]
    
    file_backups = [f for f in items 
                    if os.path.isfile(os.path.join(backup_dir, f)) 
                    and f.startswith("FullRegistryBackup_")]
    
    # Сортируем оба списка
    dir_backups.sort(reverse=True)
    file_backups.sort(reverse=True)
    
    # Добавляем сначала директории
    for backup in dir_backups:
        backup_list.insert(tk.END, backup)
    
    # Затем добавляем файлы
    for backup in file_backups:
        backup_list.insert(tk.END, backup)

def delete_backup(backup_name, tab_control):
    if not backup_name:
        messagebox.showwarning("Предупреждение", "Пожалуйста, выберите бэкап для удаления")
        return
        
    if messagebox.askyesno("Подтверждение", f"Удалить бэкап {backup_name}?"):
        backup_path = os.path.join(os.getcwd(), "Backup", backup_name)
        try:
            if os.path.isdir(backup_path):
                shutil.rmtree(backup_path)
            else:
                os.remove(backup_path)
            messagebox.showinfo("Успех", "Бэкап успешно удален")
            # Get the backup list widget from the current tab
            for tab in tab_control.tabs():
                tab_frame = tab_control.children[tab.split('.')[-1]]
                if isinstance(tab_frame, ttk.Frame):
                    for widget in tab_frame.winfo_children():
                        if isinstance(widget, ttk.Frame):
                            for child in widget.winfo_children():
                                if isinstance(child, ttk.Frame):
                                    for list_widget in child.winfo_children():
                                        if isinstance(list_widget, tk.Listbox):
                                            update_backup_list(list_widget)
                                            return
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить бэкап: {str(e)}")

def create_backup_tab(tab_control, export_full_registry, import_registry_backup):
    backup_tab = ttk.Frame(tab_control)
    tab_control.add(backup_tab, text="Бэкап реестра")
    
    # Create main layout with splitter
    main_frame = ttk.Frame(backup_tab)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Create left panel for backup list
    left_panel = ttk.Frame(main_frame)
    left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
    
    # Create buttons frame
    buttons_frame = ttk.Frame(left_panel)
    buttons_frame.pack(fill=tk.X, pady=(0, 10))

    # Create backup buttons
    backup_btn = ttk.Button(
        buttons_frame,
        text="Создать бэкап реестра",
        command=create_registry_backup,
        bootstyle="success-outline",
        width=25
    )
    backup_btn.pack(side=tk.LEFT, padx=(0, 5))
    
    full_backup_btn = ttk.Button(
        buttons_frame,
        text="Полный бэкап реестра",
        command=export_full_registry,
        bootstyle="danger-outline",
        width=25
    )
    full_backup_btn.pack(side=tk.LEFT)
    
    # Create listbox for backups
    backup_list_frame = ttk.Frame(left_panel)
    backup_list_frame.pack(fill=tk.BOTH, expand=True)
    
    backup_list = tk.Listbox(
        backup_list_frame,
        selectmode=tk.SINGLE,
        width=30,
        height=20
    )
    backup_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Add scrollbar to listbox
    scrollbar = ttk.Scrollbar(backup_list_frame, orient=tk.VERTICAL, command=backup_list.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    backup_list.configure(yscrollcommand=scrollbar.set)
    
    # Create import button
    import_btn = ttk.Button(
        left_panel,
        text="Импортировать выбранный бэкап",
        command=lambda: import_registry_backup(backup_list),
        bootstyle="success-outline",
        width=54
    )
    import_btn.pack(pady=(10, 5))
    
    # Create refresh button
    refresh_btn = ttk.Button(
        left_panel,
        text="Обновить список",
        command=lambda: update_backup_list(backup_list),
        bootstyle="warning-outline",
        width=54
    )
    refresh_btn.pack(pady=(0, 10))
    
    # Create right panel for backup details
    right_panel = ttk.Frame(main_frame)
    right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
    
    # Create backup info frame
    info_frame = ttk.LabelFrame(right_panel, text="Информация о бэкапе", padding=10)
    info_frame.pack(fill=tk.BOTH, expand=True)
    
    # Create info labels
    backup_name_label = ttk.Label(info_frame, text="Выберите бэкап для просмотра информации", font=('Segoe UI', 10))
    backup_name_label.pack(pady=(0, 10))
    
    # Create details frame
    details_frame = ttk.Frame(info_frame)
    details_frame.pack(fill=tk.BOTH, expand=True)
    
    # Create treeview for backup details
    tree = ttk.Treeview(details_frame, columns=("Value",), show="tree", height=10)
    tree.heading("#0", text="Файлы в бэкапе")
    tree.heading("Value", text="Размер")
    tree.column("#0", width=200)
    tree.column("Value", width=100)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Add scrollbar to treeview
    tree_scrollbar = ttk.Scrollbar(details_frame, orient=tk.VERTICAL, command=tree.yview)
    tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.configure(yscrollcommand=tree_scrollbar.set)
    
    # Create action buttons frame
    action_frame = ttk.Frame(info_frame)
    action_frame.pack(fill=tk.X, pady=(10, 0))
    
    # Create action buttons
    import_btn = ttk.Button(
        action_frame,
        text="Импортировать бэкап",
        command=lambda: import_registry_backup(backup_list),
        bootstyle="success-outline",
        width=25
    )
    import_btn.pack(side=tk.LEFT, padx=(0, 5))
    
    delete_btn = ttk.Button(
        action_frame,
        text="Удалить бэкап",
        command=lambda: delete_backup(backup_list.get(backup_list.curselection()[0]) if backup_list.curselection() else None, tab_control),
        bootstyle="danger-outline",
        width=25
    )
    delete_btn.pack(side=tk.LEFT)
    
    # Function to show backup details
    def show_backup_details(event):
        selection = backup_list.curselection()
        if not selection:
            backup_name_label.config(text="Выберите бэкап для просмотра информации")
            tree.delete(*tree.get_children())
            return
            
        backup_name = backup_list.get(selection[0])
        backup_path = os.path.join(os.getcwd(), "Backup", backup_name)
        
        # Update backup name label
        backup_name_label.config(text=f"Бэкап: {backup_name}")
        
        # Clear existing items
        tree.delete(*tree.get_children())
        
        if os.path.isdir(backup_path):
            # Directory backup - show all .reg files
            reg_files = [f for f in os.listdir(backup_path) if f.endswith('.reg')]
            for reg_file in reg_files:
                full_path = os.path.join(backup_path, reg_file)
                size = os.path.getsize(full_path)
                size_str = f"{size / 1024:.1f} KB" if size < 1024 * 1024 else f"{size / (1024 * 1024):.1f} MB"
                tree.insert("", "end", text=reg_file, values=(size_str,))
        else:
            # Single file backup - show file info
            size = os.path.getsize(backup_path)
            size_str = f"{size / 1024:.1f} KB" if size < 1024 * 1024 else f"{size / (1024 * 1024):.1f} MB"
            tree.insert("", "end", text=backup_name, values=(size_str,))
    
    # Bind events
    backup_list.bind('<<ListboxSelect>>', show_backup_details)
    
    # Initial update
    update_backup_list(backup_list) 