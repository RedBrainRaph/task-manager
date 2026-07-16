"""
main.py — Точка входа в приложение.
Инициализирует TaskManager, создаёт Tk root и запускает главное окно.
"""

import tkinter as tk
import os
import sys

from task_manager import TaskManager
from gui import MainWindow


def resource_path(relative_path: str) -> str:
    """
    Возвращает корректный путь к файлам.
    Работает:
    - при запуске через Python
    - после сборки PyInstaller
    """

    try:
        base_path = sys._MEIPASS

    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def main() -> None:
    """Запускает приложение."""

    root = tk.Tk()


    # Иконка приложения


    try:
        icon = tk.PhotoImage(
            file=resource_path("icon.png")
        )

        root.iconphoto(
            True,
            icon
        )

        # сохраняем ссылку,
        # чтобы tkinter не удалил изображение
        root.icon = icon

    except Exception as e:
        print("Ошибка загрузки иконки:", e)



    # Запуск приложения


    manager = TaskManager()

    app = MainWindow(
        root,
        manager
    )

    root.protocol(
        "WM_DELETE_WINDOW",
        app._on_exit
    )

    root.mainloop()


if __name__ == "__main__":
    main()