"""
gui.py  Главный графический интерфейс на Tkinter (ttk).

Содержит:
   MainWindow главное окно с таблицей и кнопками.
   TaskFormWindow: диалог добавления / редактирования задачи.
   FilterWindow: диалог настройки фильтров.
  SortWindow: диалог выбора сортировки.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Optional, Dict

from task_manager import TaskManager
from utils import Task, STATUSES, PRIORITY_LABELS, ValidationError
from charts import ChartsWindow
from priority import calculate_score



# Цвета и шрифты


APP_BG = "#121212"          # основной фон
CARD_BG = "#1E1E1E"         # панели
HEADER_BG = "#0B0B0B"       # верхняя панель
HEADER_FG = "#FFFFFF"

TEXT_COLOR = "#EAEAEA"
TEXT_SECONDARY = "#B0B0B0"

BRONZE = "#CD7F32"
BRONZE_LIGHT = "#E6A15C"

GREEN = "#2ECC71"
DARK_GREEN = "#1E8449"

BURGUNDY = "#8E2430"
RED = "#C0392B"

ORANGE = "#E67E22"
GOLD = "#D4AC0D"

PURPLE = "#8E44AD"
BLUE = "#2980B9"

WARNING = ORANGE
SUCCESS = GREEN
DANGER = RED
ACCENT = BRONZE

FONT_MAIN = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_HEADER = ("Segoe UI", 14, "bold")
FONT_SMALL = ("Segoe UI", 9)



# Диалог добавления / редактирования задачи


class TaskFormWindow:
    """Модальное окно для создания или редактирования задачи."""

    def __init__(self, parent: tk.Widget, title: str, task: Optional[Task] = None) -> None:
        self._result: Optional[dict] = None
        self._task = task

        self._dialog = tk.Toplevel(parent)
        self._dialog.title(title)
        self._dialog.geometry("500x480")
        self._dialog.resizable(False, False)
        self._dialog.grab_set()
        self._dialog.configure(bg=APP_BG)
        self._dialog.attributes("-topmost",True)

        self._build_form()

        if task:
            self._fill_form(task)

        self._dialog.wait_window()

    def _build_form(self) -> None:
        container = tk.Frame(
            self._dialog,
            bg=APP_BG,
            padx=30,
            pady=25
        )

        container.pack(
            fill=tk.BOTH,
            expand=True
        )

        title = tk.Label(
            container,

            text="Создание задачи",

            font=FONT_HEADER,

            bg=APP_BG,

            fg=BRONZE_LIGHT
        )

        title.grid(
            row=0,
            column=0,
            columnspan=2,

            sticky="w",

            pady=(0, 20)
        )

        def field_label(row, text):
            tk.Label(

                container,

                text=text,

                font=FONT_BOLD,

                bg=APP_BG,

                fg=TEXT_COLOR

            ).grid(

                row=row,

                column=0,

                sticky="w",

                pady=8
            )

        # Название

        field_label(
            1,
            "Название"
        )

        self._entry_title = ttk.Entry(
            container,
            font=FONT_MAIN,
            width=40
        )

        self._entry_title.grid(
            row=1,
            column=1,
            padx=15
        )

        # Описание

        field_label(
            2,
            "Описание"
        )

        self._text_desc = tk.Text(

            container,

            width=40,

            height=5,

            font=FONT_MAIN,

            bg="#1E1E1E",

            fg=TEXT_COLOR,

            insertbackground="white",

            relief="flat"

        )

        self._text_desc.grid(
            row=2,
            column=1,
            padx=15
        )

        # Приоритет

        field_label(
            3,
            "Приоритет"
        )

        self._combo_priority = ttk.Combobox(

            container,

            values=[
                str(k)
                for k in PRIORITY_LABELS
            ],

            state="readonly",

            width=10

        )

        self._combo_priority.current(2)

        self._combo_priority.grid(
            row=3,
            column=1,

            sticky="w",

            padx=15
        )

        # Статус

        field_label(
            4,
            "Статус"
        )

        self._combo_status = ttk.Combobox(

            container,

            values=list(STATUSES),

            state="readonly",

            width=18

        )

        self._combo_status.current(0)

        self._combo_status.grid(
            row=4,
            column=1,

            sticky="w",

            padx=15
        )

        # Дата

        field_label(
            5,
            "Дедлайн"
        )

        self._entry_deadline = ttk.Entry(

            container,

            width=18

        )

        self._entry_deadline.grid(

            row=5,

            column=1,

            sticky="w",

            padx=15

        )

        container.columnconfigure(
            1,
            weight=1
        )

        # кнопки

        buttons = tk.Frame(

            self._dialog,

            bg=APP_BG,

            pady=15

        )

        buttons.pack(
            fill=tk.X
        )

        save = tk.Button(
            buttons,
            text="✓ Сохранить",

            font=FONT_BOLD,

            bg=GREEN,
            fg="#FFFFFF",

            activebackground=GREEN,
            activeforeground="#FFFFFF",

            relief="flat",
            borderwidth=0,
            highlightthickness=0,

            padx=20,
            pady=8,

            cursor="hand2",

            command=self._on_save
        )

        save.pack(
            side=tk.RIGHT,
            padx=10
        )

        cancel = tk.Button(
            buttons,
            text="✕ Отмена",

            font=FONT_BOLD,

            bg=BURGUNDY,
            fg="#FFFFFF",

            activebackground=BURGUNDY,
            activeforeground="#FFFFFF",

            relief="flat",
            borderwidth=0,
            highlightthickness=0,

            padx=20,
            pady=8,

            cursor="hand2",

            command=self._dialog.destroy
        )

        cancel.pack(
            side=tk.RIGHT
        )

        def on_enter_save(e):
            save.config(bg="#3FAF6F")

        def on_leave_save(e):
            save.config(bg=GREEN)

        def on_enter_cancel(e):
            cancel.config(bg="#A52A4A")

        def on_leave_cancel(e):
            cancel.config(bg=BURGUNDY)

        save.bind("<Enter>", on_enter_save)
        save.bind("<Leave>", on_leave_save)

        cancel.bind("<Enter>", on_enter_cancel)
        cancel.bind("<Leave>", on_leave_cancel)





    def _fill_form(self, task: Task) -> None:
        """Заполняет форму данными существующей задачи."""
        self._entry_title.insert(0, task.title)
        self._text_desc.insert("1.0", task.description)
        self._combo_priority.set(str(task.priority))
        self._combo_status.set(task.status)
        self._entry_deadline.insert(0, task.deadline)

    def _on_save(self) -> None:
        """Считывает данные формы и закрывает диалог."""
        self._result = {
            "title": self._entry_title.get(),
            "description": self._text_desc.get("1.0", tk.END).strip(),
            "priority": self._combo_priority.get(),
            "status": self._combo_status.get(),
            "deadline": self._entry_deadline.get(),
        }
        self._dialog.destroy()

    @property
    def result(self) -> Optional[dict]:
        """Возвращает словарь с данными формы или None при отмене."""
        return self._result



# Диалог фильтрации


class FilterWindow:
    """Диалог для настройки фильтров задач."""

    def __init__(self, parent: tk.Widget, current_filters: dict) -> None:
        self._result: Optional[dict] = None

        self._dialog = tk.Toplevel(parent)
        self._dialog.title("Фильтрация задач")
        self._dialog.geometry("380x340")
        self._dialog.resizable(False, False)
        self._dialog.grab_set()
        self._dialog.configure(bg=APP_BG)

        self._build(current_filters)
        self._dialog.wait_window()

    def _build(self, current: dict) -> None:
        container = tk.Frame(self._dialog, bg=APP_BG, padx=24, pady=20)
        container.pack(fill=tk.BOTH, expand=True)

        tk.Label(container, text="Фильтры", font=FONT_HEADER, bg=APP_BG, fg=HEADER_BG).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 14)
        )

        def lbl(row: int, text: str) -> None:
            tk.Label(container, text=text, font=FONT_BOLD, bg=APP_BG).grid(
                row=row, column=0, sticky="w", pady=5
            )

        lbl(1, "Статус:")
        self._combo_status = ttk.Combobox(
            container, values=["Все"] + list(STATUSES), state="readonly", font=FONT_MAIN, width=16
        )
        self._combo_status.set(current.get("status", "Все"))
        self._combo_status.grid(row=1, column=1, sticky="w", padx=(8, 0))

        lbl(2, "Приоритет:")
        self._combo_priority = ttk.Combobox(
            container,
            values=["Все"] + [str(i) for i in range(1, 6)],
            state="readonly",
            font=FONT_MAIN,
            width=8,
        )
        self._combo_priority.set(current.get("priority", "Все"))
        self._combo_priority.grid(row=2, column=1, sticky="w", padx=(8, 0))

        lbl(3, "Дедлайн от:")
        self._entry_from = ttk.Entry(container, font=FONT_MAIN, width=14)
        self._entry_from.insert(0, current.get("date_from", ""))
        self._entry_from.grid(row=3, column=1, sticky="w", padx=(8, 0))

        lbl(4, "Дедлайн до:")
        self._entry_to = ttk.Entry(container, font=FONT_MAIN, width=14)
        self._entry_to.insert(0, current.get("date_to", ""))
        self._entry_to.grid(row=4, column=1, sticky="w", padx=(8, 0))

        lbl(5, "Поиск в названии:")
        self._entry_search = ttk.Entry(container, font=FONT_MAIN, width=22)
        self._entry_search.insert(0, current.get("title_query", ""))
        self._entry_search.grid(row=5, column=1, sticky="w", padx=(8, 0))

        btn_frame = tk.Frame(self._dialog, bg=APP_BG, padx=24, pady=12)
        btn_frame.pack(fill=tk.X)

        tk.Button(
            btn_frame, text="Применить", font=FONT_BOLD, bg=ACCENT, fg="white",
            relief="flat", padx=16, pady=7, cursor="hand2", command=self._on_apply
        ).pack(side=tk.RIGHT, padx=4)

        tk.Button(
            btn_frame, text="Сбросить", font=FONT_MAIN, bg=WARNING, fg="white",
            relief="flat", padx=16, pady=7, cursor="hand2", command=self._on_reset
        ).pack(side=tk.RIGHT, padx=4)

        tk.Button(
            btn_frame, text="Отмена", font=FONT_MAIN, bg="#CCCCCC", fg="#333333",
            relief="flat", padx=16, pady=7, cursor="hand2", command=self._dialog.destroy
        ).pack(side=tk.RIGHT, padx=4)

    def _on_apply(self) -> None:
        p = self._combo_priority.get()
        self._result = {
            "status": self._combo_status.get(),
            "priority": None if p == "Все" else int(p),
            "date_from": self._entry_from.get().strip(),
            "date_to": self._entry_to.get().strip(),
            "title_query": self._entry_search.get().strip(),
        }
        self._dialog.destroy()

    def _on_reset(self) -> None:
        self._result = {
            "status": "Все",
            "priority": None,
            "date_from": "",
            "date_to": "",
            "title_query": "",
        }
        self._dialog.destroy()

    @property
    def result(self) -> Optional[dict]:
        return self._result



# Диалог сортировки


class SortWindow:
    """Диалог выбора критерия сортировки."""

    SORT_OPTIONS = [
        ("Название", "title"),
        ("Дата создания", "created"),
        ("Дедлайн", "deadline"),
        ("Приоритет", "priority"),
        ("Интеллектуальный рейтинг", "score"),
    ]

    def __init__(self, parent: tk.Widget, current_key: str, current_asc: bool) -> None:
        self._result: Optional[dict] = None

        self._dialog = tk.Toplevel(parent)
        self._dialog.title("Сортировка задач")
        self._dialog.geometry("320x300")
        self._dialog.resizable(False, False)
        self._dialog.grab_set()
        self._dialog.configure(bg=APP_BG)

        self._build(current_key, current_asc)
        self._dialog.wait_window()

    def _build(self, current_key: str, current_asc: bool) -> None:
        container = tk.Frame(self._dialog, bg=APP_BG, padx=24, pady=20)
        container.pack(fill=tk.BOTH, expand=True)

        tk.Label(container, text="Сортировка", font=FONT_HEADER, bg=APP_BG, fg=HEADER_BG).pack(
            anchor="w", pady=(0, 12)
        )

        self._key_var = tk.StringVar(value=current_key)
        for label, key in self.SORT_OPTIONS:
            ttk.Radiobutton(
                container, text=label, variable=self._key_var, value=key
            ).pack(anchor="w", pady=2)

        tk.Label(container, text="Направление:", font=FONT_BOLD, bg=APP_BG).pack(
            anchor="w", pady=(12, 4)
        )
        self._asc_var = tk.BooleanVar(value=current_asc)
        ttk.Radiobutton(container, text="По возрастанию ↑", variable=self._asc_var, value=True).pack(
            anchor="w"
        )
        ttk.Radiobutton(container, text="По убыванию ↓", variable=self._asc_var, value=False).pack(
            anchor="w"
        )

        btn_frame = tk.Frame(self._dialog, bg=APP_BG, padx=24, pady=10)
        btn_frame.pack(fill=tk.X)

        tk.Button(
            btn_frame, text="Применить", font=FONT_BOLD, bg=ACCENT, fg="white",
            relief="flat", padx=16, pady=7, cursor="hand2", command=self._on_apply
        ).pack(side=tk.RIGHT, padx=4)

        tk.Button(
            btn_frame, text="Отмена", font=FONT_MAIN, bg="#CCCCCC", fg="#333333",
            relief="flat", padx=16, pady=7, cursor="hand2", command=self._dialog.destroy
        ).pack(side=tk.RIGHT, padx=4)

    def _on_apply(self) -> None:
        self._result = {"key": self._key_var.get(), "ascending": self._asc_var.get()}
        self._dialog.destroy()

    @property
    def result(self) -> Optional[dict]:
        return self._result



# Главное окно


class MainWindow:
    """Главное окно приложения."""

    TREE_COLUMNS = (
        ("id", "ID", 40),
        ("title", "Название", 200),
        ("priority", "Приоритет", 90),
        ("status", "Статус", 100),
        ("deadline", "Дедлайн", 100),
        ("created", "Создана", 100),
        ("score", "Рейтинг", 80),
    )

    def __init__(self, root: tk.Tk, manager: TaskManager) -> None:
        self._root = root
        self._manager = manager
        self._filters: dict = {
            "status": "Все",
            "priority": None,
            "date_from": "",
            "date_to": "",
            "title_query": "",
        }
        self._sort_key: str = "score"
        self._sort_asc: bool = False

        self._setup_root()
        self._build_header()
        self._build_toolbar()
        self._build_search_bar()
        self._build_table()
        self._build_statusbar()
        self._refresh_table()


    # Построение интерфейса


    def _setup_root(self) -> None:
        self._root.tk.call(
            "tk",
            "scaling",
            1.2
        )
        self._root.title("Task Manager")
        self._root.geometry("1100x680")
        self._root.minsize(900, 550)
        self._root.configure(bg=APP_BG)

        style = ttk.Style(self._root)
        style.theme_use("clam")


        # Общий стиль


        style.configure(
            ".",
            background=APP_BG,
            foreground=TEXT_COLOR,
            font=FONT_MAIN
        )


        # Таблица


        style.configure(
            "Treeview",
            background="#181818",
            foreground="#EEEEEE",
            fieldbackground="#181818",
            rowheight=32,
            font=FONT_MAIN,
            borderwidth=0
        )

        style.configure(
            "Treeview.Heading",
            background="#0B0B0B",
            foreground=BRONZE_LIGHT,
            font=("Segoe UI", 10, "bold"),
            relief="flat"
        )

        style.map(
            "Treeview",
            background=[
                ("selected", BRONZE)
            ],
            foreground=[
                ("selected", "#000000")
            ]
        )

        # ==========================
        # Поля ввода
        # ==========================

        style.configure(
            "TEntry",
            fieldbackground="#242424",
            foreground=TEXT_COLOR,
            borderwidth=0
        )

        style.configure(
            "TCombobox",
            fieldbackground="#242424",
            background="#242424",
            foreground=TEXT_COLOR,
            borderwidth=0
        )


        # Кнопки


        style.configure(
            "Green.TButton",
            background="#2E8B57",
            foreground="white",
            padding=(14, 8),
            borderwidth=0,
            font=FONT_BOLD
        )

        style.map(
            "Green.TButton",
            background=[
                ("active", "#3CB371")
            ]
        )

        style.configure(
            "Bronze.TButton",
            background="#CD7F32",
            foreground="white",
            padding=(14, 8),
            borderwidth=0,
            font=FONT_BOLD
        )

        style.map(
            "Bronze.TButton",
            background=[
                ("active", "#E6A15C")
            ]
        )

        style.configure(
            "Red.TButton",
            background="#800020",
            foreground="white",
            padding=(14, 8),
            borderwidth=0,
            font=FONT_BOLD
        )

        style.map(
            "Red.TButton",
            background=[
                ("active", "#A52A2A")
            ]
        )

        style.configure(
            "Clear.TButton",
            background="#800020",
            foreground="white",
            padding=(10, 5),
            borderwidth=0,
            font=FONT_SMALL
        )

        style.map(
            "Clear.TButton",
            background=[
                ("active", "#A52A2A")
            ]
        )

        style.configure(
            "Purple.TButton",
            background="#6C5CE7",
            foreground="white",
            padding=(14, 8),
            borderwidth=0,
            font=FONT_BOLD
        )

        style.configure(
            "Orange.TButton",
            background="#D97706",
            foreground="white",
            padding=(14, 8),
            borderwidth=0,
            font=FONT_BOLD
        )

        style.configure(
            "Gold.TButton",
            background="#D4AF37",
            foreground="black",
            padding=(14, 8),
            borderwidth=0,
            font=FONT_BOLD
        )

    def _build_header(self) -> None:
        header = tk.Frame(self._root, bg=HEADER_BG, height=65)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="  Система управления задачами",
            font=("Segoe UI", 14, "bold"),
            bg=HEADER_BG,
            fg=BRONZE_LIGHT,
        ).pack(side=tk.LEFT, padx=16)

        self._lbl_filter_indicator = tk.Label(
            header,
            text="",
            font=FONT_SMALL,
            bg=HEADER_BG,
            fg="#A0C4FF",
        )
        self._lbl_filter_indicator.pack(side=tk.RIGHT, padx=16)

    def _build_toolbar(self) -> None:

        toolbar = tk.Frame(
            self._root,
            bg=APP_BG,
            pady=8
        )

        toolbar.pack(fill=tk.X)

        def btn(text, style, cmd):
            button = ttk.Button(
                toolbar,
                text=text,
                style=style,
                command=cmd
            )

            button.pack(
                side=tk.LEFT,
                padx=6
            )

            return button

        btn(
            "➕ Добавить",
            "Green.TButton",
            self._on_add
        )

        btn(
            "✏️ Изменить",
            "Bronze.TButton",
            self._on_edit
        )

        btn(
            "🗑 Удалить",
            "Red.TButton",
            self._on_delete
        )

        tk.Frame(
            toolbar,
            bg=APP_BG,
            width=20
        ).pack(side=tk.LEFT)

        btn(
            "🔽 Фильтр",
            "Purple.TButton",
            self._on_filter
        )

        btn(
            "🔄 Сортировка",
            "Green.TButton",
            self._on_sort
        )

        tk.Frame(
            toolbar,
            bg=APP_BG,
            width=20
        ).pack(side=tk.LEFT)

        btn(
            "📊 Графики",
            "Orange.TButton",
            self._on_charts
        )

        btn(
            "📤 Экспорт",
            "Gold.TButton",
            self._on_export
        )

        btn(
            "️✕ Выход",
            "Red.TButton",
            self._on_exit
        )

    def _build_search_bar(self) -> None:

        bar = tk.Frame(
            self._root,
            bg=APP_BG,
            pady=8
        )

        bar.pack(
            fill=tk.X,
            padx=15
        )

        tk.Label(
            bar,
            text="Поиск:",
            font=FONT_BOLD,
            bg=APP_BG,
            fg=TEXT_COLOR
        ).pack(
            side=tk.LEFT
        )

        self._search_var = tk.StringVar()

        self._search_var.trace_add(
            "write",
            self._on_search_changed
        )

        search_entry = ttk.Entry(
            bar,
            textvariable=self._search_var,
            font=FONT_MAIN,
            width=35
        )

        search_entry.pack(
            side=tk.LEFT,
            padx=12
        )

        clear_btn = ttk.Button(
            bar,
            text="✕ Очистить",
            style="Red.TButton",
            command=self._clear_search
        )

        clear_btn.pack(
            side=tk.LEFT,
            padx=8
        )

    def _build_table(self) -> None:

        frame = tk.Frame(
            self._root,
            bg=APP_BG
        )

        frame.pack(
            fill=tk.BOTH,
            expand=True,
            padx=15,
            pady=5
        )

        # вертикальный скролл

        scrollbar_y = ttk.Scrollbar(
            frame,
            orient=tk.VERTICAL
        )

        scrollbar_y.pack(
            side=tk.RIGHT,
            fill=tk.Y
        )

        # горизонтальный скролл

        scrollbar_x = ttk.Scrollbar(
            frame,
            orient=tk.HORIZONTAL
        )

        scrollbar_x.pack(
            side=tk.BOTTOM,
            fill=tk.X
        )

        self._tree = ttk.Treeview(
            frame,

            columns=[
                c[0]
                for c in self.TREE_COLUMNS
            ],

            show="headings",

            yscrollcommand=scrollbar_y.set,

            xscrollcommand=scrollbar_x.set,

            selectmode="browse"
        )

        scrollbar_y.config(
            command=self._tree.yview
        )

        scrollbar_x.config(
            command=self._tree.xview
        )

        # Заголовки таблицы

        for col_id, col_name, col_width in self.TREE_COLUMNS:
            self._tree.heading(
                col_id,
                text=col_name
            )

            self._tree.column(
                col_id,
                width=col_width,
                minwidth=50,

                anchor="center"
            )

        # название задачи слева

        self._tree.column(
            "title",
            anchor="w",
            width=250
        )

        # Цветовые состояния строк

        self._tree.tag_configure(
            "overdue",
            background="#3A1717",
            foreground="#FF8A8A"
        )

        self._tree.tag_configure(
            "today",
            background="#3A2D14",
            foreground="#FFD166"
        )

        self._tree.tag_configure(
            "done",
            background="#14331E",
            foreground="#7DCEA0"
        )

        self._tree.tag_configure(
            "normal",
            background="#181818",
            foreground="#EAEAEA"
        )

        self._tree.bind(
            "<Double-1>",
            lambda e: self._on_edit()
        )

        self._tree.pack(
            fill=tk.BOTH,
            expand=True
        )

    def _build_statusbar(self) -> None:

        self._statusbar = tk.Label(

            self._root,

            text="",

            font=FONT_SMALL,

            bg="#0B0B0B",

            fg=BRONZE_LIGHT,

            anchor="w",

            padx=15,

            pady=6
        )

        self._statusbar.pack(
            fill=tk.X,
            side=tk.BOTTOM
        )


    # Обновление таблицы


    def _get_filtered_sorted_tasks(self) -> List[Task]:
        """Применяет текущие фильтры, поиск и сортировку."""
        q = self._search_var.get().strip() if hasattr(self, "_search_var") else ""

        tasks = self._manager.filter_tasks(
            status=self._filters.get("status"),
            priority=self._filters.get("priority"),
            date_from=self._filters.get("date_from") or None,
            date_to=self._filters.get("date_to") or None,
            title_query=q or self._filters.get("title_query") or None,
        )
        return self._manager.sort_tasks(tasks, self._sort_key, self._sort_asc)

    def _refresh_table(self) -> None:
        """Очищает и заново заполняет таблицу задач."""
        for item in self._tree.get_children():
            self._tree.delete(item)

        tasks = self._get_filtered_sorted_tasks()
        scores = self._manager.get_scores()

        from datetime import date as _date
        today = _date.today()
        from utils import parse_date

        for task in tasks:
            score = scores.get(task.id, 0.0)
            deadline = parse_date(task.deadline)
            days_left = (deadline - today).days if deadline else None

            if task.status == "Выполнена":
                tag = "done"
            elif days_left is not None and days_left < 0:
                tag = "overdue"
            elif days_left is not None and days_left == 0:
                tag = "today"
            else:
                tag = "normal"

            self._tree.insert(
                "",
                tk.END,
                iid=str(task.id),
                values=(
                    task.id,
                    task.title,
                    PRIORITY_LABELS.get(task.priority, task.priority),
                    task.status,
                    task.deadline,
                    task.created,
                    f"{score:.2f}",
                ),
                tags=(tag,),
            )

        self._update_statusbar(len(tasks))
        self._update_filter_indicator()

    def _update_statusbar(self, count: int) -> None:
        all_tasks = self._manager.get_all()
        total = len(all_tasks)
        overdue = sum(
            1 for t in all_tasks
            if t.status != "Выполнена"
            and __import__("utils").parse_date(t.deadline) is not None
            and (__import__("utils").parse_date(t.deadline) - __import__("datetime").date.today()).days < 0
        )
        self._statusbar.config(
            text=f"  Показано: {count} из {total}   |   Просрочено: {overdue}   |   "
                 f"Сортировка: {self._sort_key}  {'↑' if self._sort_asc else '↓'}"
        )

    def _update_filter_indicator(self) -> None:
        active = []
        if self._filters.get("status") and self._filters["status"] != "Все":
            active.append(f"статус={self._filters['status']}")
        if self._filters.get("priority"):
            active.append(f"приоритет={self._filters['priority']}")
        if self._filters.get("date_from"):
            active.append(f"от={self._filters['date_from']}")
        if self._filters.get("date_to"):
            active.append(f"до={self._filters['date_to']}")
        if self._filters.get("title_query"):
            active.append(f"поиск={self._filters['title_query']!r}")

        text = ("  Фильтры: " + " | ".join(active)) if active else ""
        self._lbl_filter_indicator.config(text=text)

    def _get_selected_task_id(self) -> Optional[int]:
        """Возвращает ID выбранной строки таблицы или None."""
        selected = self._tree.selection()
        if not selected:
            return None
        return int(selected[0])


    # Обработчики событий


    def _on_add(self) -> None:
        form = TaskFormWindow(self._root, "Добавить задачу")
        if form.result is None:
            return
        data = form.result
        try:
            self._manager.add_task(
                title=data["title"],
                description=data["description"],
                priority=data["priority"],
                deadline=data["deadline"],
                status=data["status"],
            )
            self._refresh_table()
            messagebox.showinfo("Успех", "Задача успешно добавлена.")
        except ValidationError as e:
            messagebox.showerror("Ошибка валидации", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить задачу:\n{e}")

    def _on_edit(self) -> None:
        task_id = self._get_selected_task_id()
        if task_id is None:
            messagebox.showwarning("Выбор задачи", "Пожалуйста, выберите задачу для редактирования.")
            return

        all_tasks = self._manager.get_all()
        task = next((t for t in all_tasks if t.id == task_id), None)
        if task is None:
            messagebox.showerror("Ошибка", "Задача не найдена.")
            return

        form = TaskFormWindow(self._root, "Редактировать задачу", task=task)
        if form.result is None:
            return
        data = form.result
        try:
            self._manager.update_task(
                task_id=task_id,
                title=data["title"],
                description=data["description"],
                priority=data["priority"],
                deadline=data["deadline"],
                status=data["status"],
            )
            self._refresh_table()
            messagebox.showinfo("Успех", "Задача успешно обновлена.")
        except ValidationError as e:
            messagebox.showerror("Ошибка валидации", str(e))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить задачу:\n{e}")

    def _on_delete(self) -> None:
        task_id = self._get_selected_task_id()
        if task_id is None:
            messagebox.showwarning("Выбор задачи", "Пожалуйста, выберите задачу для удаления.")
            return

        confirmed = messagebox.askyesno(
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить задачу #{task_id}?\nЭто действие необратимо.",
        )
        if not confirmed:
            return
        try:
            self._manager.delete_task(task_id)
            self._refresh_table()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить задачу:\n{e}")

    def _on_filter(self) -> None:
        dialog = FilterWindow(self._root, self._filters)
        if dialog.result is not None:
            self._filters = dialog.result
            self._refresh_table()

    def _on_sort(self) -> None:
        dialog = SortWindow(self._root, self._sort_key, self._sort_asc)
        if dialog.result is not None:
            self._sort_key = dialog.result["key"]
            self._sort_asc = dialog.result["ascending"]
            self._refresh_table()

    def _on_search_changed(self, *args) -> None:
        self._refresh_table()

    def _clear_search(self) -> None:
        self._search_var.set("")

    def _on_charts(self) -> None:
        tasks = self._manager.get_all()
        if not tasks:
            messagebox.showinfo("Нет данных", "Добавьте задачи, чтобы просматривать графики.")
            return
        ChartsWindow(self._root, tasks)

    def _on_export(self) -> None:
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV файлы", "*.csv"), ("Все файлы", "*.*")],
            initialfile="report.csv",
            title="Сохранить отчёт",
        )
        if not path:
            return
        try:
            saved_path = self._manager.export_report(path)
            messagebox.showinfo("Экспорт завершён", f"Отчёт сохранён:\n{saved_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать отчёт:\n{e}")

    def _on_exit(self) -> None:
        if messagebox.askyesno("Выход", "Выйти из приложения?"):
            self._root.quit()
