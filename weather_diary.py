"""
Weather Diary - Дневник погоды
GUI-приложение для ведения дневника погоды с возможностью добавления,
просмотра, фильтрации записей и сохранения в JSON файл.
"""

import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox


class WeatherDiary:
    """Основной класс приложения Weather Diary"""
    
    def __init__(self, root):
        """
        Конструктор класса. Инициализирует главное окно приложения.
        
        Args:
            root: корневой элемент tkinter (главное окно)
        """
        # Настройка главного окна
        self.root = root
        self.root.title("Weather Diary - Дневник погоды")  # Заголовок окна
        self.root.geometry("800x600")  # Размер окна: ширина 800, высота 600 пикселей
        
        # Имя файла для хранения данных в формате JSON
        self.data_file = "weather_data.json"
        
        # Список для хранения всех записей о погоде
        # Каждая запись - это словарь с ключами:
        # date, temperature, description, precipitation
        self.entries = []
        
        # Загружаем существующие данные из файла (если файл есть)
        self.load_from_file()
        
        # Создаем все элементы интерфейса
        self.create_widgets()
        
        # Отображаем записи в таблице
        self.refresh_display()
    
    def create_widgets(self):
        """
        Создает все графические элементы интерфейса:
        - Поля для ввода (дата, температура, описание, осадки)
        - Кнопки (добавить, фильтровать, сохранить)
        - Таблицу для отображения записей
        """
        
        # ==================== РАМКА ДЛЯ ВВОДА ДАННЫХ ====================
        # LabelFrame - это рамка с заголовком для группировки элементов
        input_frame = ttk.LabelFrame(self.root, text="Добавить запись", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        # fill="x" - растягиваем по горизонтали
        # padx/pady - отступы от краев
        
        # ---------- Поле 1: ДАТА ----------
        # Метка (подпись) для поля даты
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(
            row=0, column=0, sticky="w", padx=5
        )
        # sticky="w" - прижимаем к западной (левой) стороне
        
        # Поле для ввода даты
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5)
        
        # Автоматически подставляем сегодняшнюю дату для удобства пользователя
        today = datetime.now().strftime("%Y-%m-%d")
        self.date_entry.insert(0, today)
        
        # ---------- Поле 2: ТЕМПЕРАТУРА ----------
        ttk.Label(input_frame, text="Температура (°C):").grid(
            row=0, column=2, sticky="w", padx=5
        )
        
        self.temp_entry = ttk.Entry(input_frame, width=10)
        self.temp_entry.grid(row=0, column=3, padx=5)
        
        # ---------- Поле 3: ОПИСАНИЕ ПОГОДЫ ----------
        ttk.Label(input_frame, text="Описание:").grid(
            row=1, column=0, sticky="w", padx=5
        )
        
        self.desc_entry = ttk.Entry(input_frame, width=40)
        self.desc_entry.grid(row=1, column=1, columnspan=3, padx=5, sticky="ew")
        # columnspan=3 - поле растягивается на 3 колонки
        # sticky="ew" - растягивается по горизонтали (east-west)
        
        # ---------- Поле 4: ОСАДКИ (ЧЕКБОКС) ----------
        # BooleanVar хранит булево значение (True/False)
        self.precip_var = tk.BooleanVar()
        
        # Checkbutton - это флажок/чекбокс
        ttk.Checkbutton(
            input_frame, 
            text="Осадки", 
            variable=self.precip_var
        ).grid(row=1, column=4, padx=10)
        
        # ---------- КНОПКА "ДОБАВИТЬ ЗАПИСЬ" ----------
        # command=self.add_entry - при нажатии вызывается метод add_entry
        ttk.Button(
            input_frame, 
            text="Добавить запись", 
            command=self.add_entry
        ).grid(row=2, column=0, columnspan=5, pady=10)
        
        # ==================== РАМКА ДЛЯ ФИЛЬТРАЦИИ ====================
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        # ---------- Фильтр по дате ----------
        ttk.Label(filter_frame, text="Фильтр по дате:").grid(
            row=0, column=0, padx=5
        )
        
        self.filter_date_entry = ttk.Entry(filter_frame, width=15)
        self.filter_date_entry.grid(row=0, column=1, padx=5)
        
        ttk.Button(
            filter_frame, 
            text="Применить", 
            command=self.apply_filter
        ).grid(row=0, column=2, padx=5)
        
        # ---------- Фильтр по температуре ----------
        ttk.Label(filter_frame, text="Температура выше:").grid(
            row=0, column=3, padx=5
        )
        
        self.filter_temp_entry = ttk.Entry(filter_frame, width=10)
        self.filter_temp_entry.grid(row=0, column=4, padx=5)
        
        ttk.Button(
            filter_frame, 
            text="Применить", 
            command=self.apply_filter
        ).grid(row=0, column=5, padx=5)
        
        # ---------- КНОПКИ УПРАВЛЕНИЯ ----------
        # Кнопка сброса фильтра
        ttk.Button(
            filter_frame, 
            text="Сбросить фильтр", 
            command=self.reset_filter
        ).grid(row=1, column=0, columnspan=3, pady=5)
        
        # Кнопка сохранения в файл
        ttk.Button(
            filter_frame, 
            text="Сохранить в файл", 
            command=self.save_to_file
        ).grid(row=1, column=3, columnspan=3, pady=5)
        
        # ==================== ТАБЛИЦА ДЛЯ ОТОБРАЖЕНИЯ ====================
        # Treeview - это виджет для отображения данных в виде таблицы/дерева
        columns = ("date", "temperature", "description", "precipitation")
        self.tree = ttk.Treeview(
            self.root, 
            columns=columns, 
            show="headings",  # Показываем только заголовки, без первого пустого столбца
            height=20
        )
        
        # Настройка заголовков и ширины столбцов
        self.tree.heading("date", text="Дата")
        self.tree.column("date", width=100)
        
        self.tree.heading("temperature", text="Температура (°C)")
        self.tree.column("temperature", width=100)
        
        self.tree.heading("description", text="Описание")
        self.tree.column("description", width=350)
        
        self.tree.heading("precipitation", text="Осадки")
        self.tree.column("precipitation", width=80)
        
        # ---------- Полоса прокрутки ----------
        scrollbar = ttk.Scrollbar(
            self.root, 
            orient="vertical",  # Вертикальная ориентация
            command=self.tree.yview  # Связываем с вертикальной прокруткой таблицы
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Размещаем таблицу и скроллбар
        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)
    
    def validate_date(self, date_str):
        """
        Проверяет, соответствует ли строка формату даты ГГГГ-ММ-ДД.
        
        Args:
            date_str (str): Строка с датой для проверки
            
        Returns:
            bool: True если формат правильный, False в противном случае
        """
        try:
            # Пробуем преобразовать строку в объект datetime
            # Если формат не совпадает - возникает исключение ValueError
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def add_entry(self):
        """
        Обработчик кнопки "Добавить запись".
        Считывает данные из полей ввода, проверяет их корректность
        и добавляет новую запись в список и таблицу.
        """
        
        # 1. СЧИТЫВАЕМ ДАННЫЕ ИЗ ПОЛЕЙ ВВОДА
        date = self.date_entry.get().strip()
        temp_str = self.temp_entry.get().strip()
        description = self.desc_entry.get().strip()
        precipitation = self.precip_var.get()  # True или False
        
        # 2. ВАЛИДАЦИЯ (ПРОВЕРКА КОРРЕКТНОСТИ) ДАННЫХ
        
        # Проверка даты
        if not self.validate_date(date):
            messagebox.showerror(
                "Ошибка", 
                "Неверный формат даты!\nИспользуйте формат: ГГГГ-ММ-ДД\nНапример: 2024-01-15"
            )
            return  # Прерываем выполнение функции
        
        # Проверка температуры (должна быть числом)
        try:
            temperature = float(temp_str)
        except ValueError:
            messagebox.showerror(
                "Ошибка", 
                "Температура должна быть числом!\nНапример: 15, -5, 23.5"
            )
            return
        
        # Проверка описания (не должно быть пустым)
        if not description:
            messagebox.showerror("Ошибка", "Описание не может быть пустым!")
            return
        
        # 3. СОЗДАЕМ НОВУЮ ЗАПИСЬ
        entry = {
            "date": date,
            "temperature": temperature,
            "description": description,
            "precipitation": "Да" if precipitation else "Нет"  # Преобразуем булево значение в текст
        }
        
        # 4. ДОБАВЛЯЕМ ЗАПИСЬ В СПИСОК
        self.entries.append(entry)
        
        # 5. СОРТИРУЕМ ЗАПИСИ ПО ДАТЕ (для удобства просмотра)
        self.entries.sort(key=lambda x: x["date"])
        
        # 6. ОЧИЩАЕМ ПОЛЯ ВВОДА ДЛЯ СЛЕДУЮЩЕЙ ЗАПИСИ
        self.temp_entry.delete(0, tk.END)  # Очищаем поле температуры
        self.desc_entry.delete(0, tk.END)  # Очищаем поле описания
        self.precip_var.set(False)  # Снимаем галочку с чекбокса
        # Поле даты не очищаем - пусть остается текущая дата
        
        # 7. ОБНОВЛЯЕМ ТАБЛИЦУ
        self.refresh_display()
        
        # 8. ПОКАЗЫВАЕМ СООБЩЕНИЕ ОБ УСПЕХЕ
        messagebox.showinfo("Успех", "Запись успешно добавлена!")
    
    def apply_filter(self):
        """
        Применяет фильтры к записям и отображает отфильтрованные данные.
        Фильтрация может происходить по дате и/или по температуре.
        """
        
        # Получаем значения фильтров из полей ввода
        filter_date = self.filter_date_entry.get().strip()
        filter_temp = self.filter_temp_entry.get().strip()
        
        # Начинаем с полного списка записей
        filtered_entries = self.entries.copy()
        
        # ---------- ПРИМЕНЯЕМ ФИЛЬТР ПО ДАТЕ ----------
        if filter_date:
            if self.validate_date(filter_date):
                # Оставляем только записи с указанной датой
                filtered_entries = [
                    entry for entry in filtered_entries 
                    if entry["date"] == filter_date
                ]
            else:
                messagebox.showwarning(
                    "Предупреждение", 
                    "Неверный формат даты фильтра!\nИспользуйте ГГГГ-ММ-ДД"
                )
        
        # ---------- ПРИМЕНЯЕМ ФИЛЬТР ПО ТЕМПЕРАТУРЕ ----------
        if filter_temp:
            try:
                temp_threshold = float(filter_temp)
                # Оставляем записи с температурой ВЫШЕ указанного значения
                filtered_entries = [
                    entry for entry in filtered_entries 
                    if entry["temperature"] > temp_threshold
                ]
            except ValueError:
                messagebox.showwarning(
                    "Предупреждение", 
                    "Температура фильтра должна быть числом!"
                )
        
        # Отображаем отфильтрованные записи
        self.display_entries(filtered_entries)
    
    def reset_filter(self):
        """
        Сбрасывает все активные фильтры и показывает все записи.
        """
        # Очищаем поля фильтрации
        self.filter_date_entry.delete(0, tk.END)
        self.filter_temp_entry.delete(0, tk.END)
        
        # Обновляем отображение (показываем все записи)
        self.refresh_display()
    
    def display_entries(self, entries_to_display):
        """
        Отображает переданный список записей в таблице.
        
        Args:
            entries_to_display (list): Список записей для отображения
        """
        # Очищаем таблицу (удаляем все существующие строки)
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Добавляем каждую запись в таблицу
        for entry in entries_to_display:
            self.tree.insert(
                "",  # Пустая строка означает корневой элемент
                "end",  # Вставляем в конец
                values=(
                    entry["date"],
                    entry["temperature"],
                    entry["description"],
                    entry["precipitation"]
                )
            )
    
    def refresh_display(self):
        """
        Обновляет отображение таблицы, показывая все записи (без фильтров).
        """
        self.display_entries(self.entries)
    
    def save_to_file(self):
        """
        Сохраняет все записи в JSON файл.
        JSON (JavaScript Object Notation) - популярный формат хранения данных.
        """
        try:
            # Открываем файл для записи в кодировке UTF-8
            with open(self.data_file, "w", encoding="utf-8") as f:
                # Преобразуем список записей в JSON строку с отступами для читаемости
                # ensure_ascii=False - позволяет сохранять русские буквы
                json.dump(self.entries, f, ensure_ascii=False, indent=4)
            
            messagebox.showinfo("Успех", f"Данные сохранены в файл {self.data_file}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{e}")
    
    def load_from_file(self):
        """
        Загружает записи из JSON файла при запуске приложения.
        Если файл не существует - просто создает пустой список.
        """
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.entries = json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{e}")
                self.entries = []
        else:
            # Файла нет - начинаем с пустого списка
            self.entries = []


def main():
    """
    Главная функция программы.
    Создает окно приложения и запускает главный цикл обработки событий.
    """
    # Создаем корневой объект tkinter (главное окно)
    root = tk.Tk()
    
    # Создаем экземпляр нашего приложения
    app = WeatherDiary(root)
    
    # Запускаем главный цикл событий (приложение начинает работу)
    root.mainloop()


# Проверяем, что файл запущен непосредственно, а не импортирован как модуль
if __name__ == "__main__":
    main()

