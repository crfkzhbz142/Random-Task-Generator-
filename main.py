import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
from datetime import datetime

class RandomTaskGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Task Generator")
        self.root.geometry("800x600")

        # Файлы для хранения данных
        self.tasks_file = "tasks.json"
        self.history_file = "history.json"

        # Предопределённые задачи по типам
        self.default_tasks = {
            "учёба": [
                "Прочитать главу учебника",
                "Сделать домашнее задание",
                "Подготовиться к экзамену",
                "Написать реферат",
                "Просмотреть обучающее видео"
            ],
            "спорт": [
                "Сделать зарядку",
                "Пойти на пробежку",
                "Посетить тренировку",
                "Выполнить упражнения на пресс",
                "Позаниматься йогой"
            ],
            "работа": [
                "Проверить электронную почту",
                "Составить отчёт",
                "Провести совещание",
                "Ответить на запросы клиентов",
                "Обновить документацию"
            ]
        }

        # Загрузка данных
        self.tasks = self.load_tasks()
        self.history = self.load_history()

        self.setup_ui()

    def setup_ui(self):
        """Создание интерфейса"""
        # Фрейм для генерации задач
        generate_frame = ttk.LabelFrame(self.root, text="Генерация задачи", padding=10)
        generate_frame.pack(fill="x", padx=10, pady=5)

        generate_btn = ttk.Button(generate_frame, text="Сгенерировать задачу", command=self.generate_task)
        generate_btn.pack(pady=10)

        # Фрейм для добавления новых задач
        add_frame = ttk.LabelFrame(self.root, text="Добавить новую задачу", padding=10)
        add_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(add_frame, text="Новая задача:").grid(row=0, column=0, sticky="w", pady=2)
        self.new_task_entry = ttk.Entry(add_frame, width=40)
        self.new_task_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(add_frame, text="Тип задачи:").grid(row=1, column=0, sticky="w", pady=2)
        self.task_type = ttk.Combobox(add_frame, values=["учёба", "спорт", "работа"], width=15)
        self.task_type.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        add_task_btn = ttk.Button(add_frame, text="Добавить задачу", command=self.add_task)
        add_task_btn.grid(row=2, column=0, columnspan=2, pady=10)

        # Фрейм для фильтров
        filter_frame = ttk.LabelFrame(self.root, text="Фильтры", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Фильтр по типу:").grid(row=0, column=0, sticky="w")
        self.filter_type = ttk.Combobox(filter_frame, values=["Все", "учёба", "спорт", "работа"])
        self.filter_type.grid(row=0, column=1, padx=5)
        self.filter_type.set("Все")

        apply_filter_btn = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filters)
        apply_filter_btn.grid(row=0, column=2, padx=(20, 5))

        reset_filter_btn = ttk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filters)
        reset_filter_btn.grid(row=0, column=3, padx=5)

        # Фрейм для отображения истории
        history_frame = ttk.LabelFrame(self.root, text="История сгенерированных задач", padding=10)
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("Время", "Задача", "Тип")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=12)

        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=200)

        self.history_tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.history_tree.configure(yscrollcommand=scrollbar.set)

        # Фрейм для кнопок управления
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill="x", padx=10, pady=5)

        save_btn = ttk.Button(control_frame, text="Сохранить данные", command=self.save_data)
        save_btn.pack(side="left", padx=5)

        load_btn = ttk.Button(control_frame, text="Загрузить данные", command=self.load_data)
        load_btn.pack(side="left", padx=5)

        clear_history_btn = ttk.Button(control_frame, text="Очистить историю", command=self.clear_history)
        clear_history_btn.pack(side="left", padx=5)

        # Обновление отображения
        self.update_history_display()

    def load_tasks(self):
        """Загрузка списка задач из JSON или использование предопределённых"""
        if os.path.exists(self.tasks_file):
            try:
                with open(self.tasks_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                messagebox.showwarning("Предупреждение", "Не удалось загрузить задачи. Используются предопределённые.")
                return self.default_tasks
        else:
            # Сохраняем предопределённые задачи при первом запуске
            self.save_tasks(self.default_tasks)
            return self.default_tasks

    def load_history(self):
        """Загрузка истории из JSON"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                messagebox.showwarning("Предупреждение", "Не удалось загрузить историю. Создаётся новая.")
                return []
        else:
            return []

    def save_tasks(self, tasks):
        """Сохранение списка задач в JSON"""
        try:
            with open(self.tasks_file, "w", encoding="utf-8") as f:
                json.dump(tasks, f, ensure_ascii=False, indent=2)
        except IOError as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить задачи: {e}")


    def save_history(self, history):
        """Сохранение истории в JSON"""
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except IOError as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {e}")

    def save_data(self):
        """Сохранение всех данных"""
        self.save_tasks(self.tasks)
        self.save_history(self.history)
        messagebox.showinfo("Успех", "Данные успешно сохранены!")

    def load_data(self):
        """Загрузка всех данных"""
        self.tasks = self.load_tasks()
        self.history = self.load_history()
        self.update_history_display()
