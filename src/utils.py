"""
utils.py — Утилиты, константы, dataclass Task и функции валидации.
"""

import re
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


DATA_FILE = "tasks.csv"

CSV_FIELDNAMES = ["id", "title", "description", "priority", "status", "deadline", "created"]

STATUSES = ("Новая", "В работе", "Выполнена")

PRIORITY_LABELS = {
    1: "1 — Очень низкий",
    2: "2 — Низкий",
    3: "3 — Средний",
    4: "4 — Высокий",
    5: "5 — Критический",
}

DATE_FORMAT = "%Y-%m-%d"


@dataclass
class Task:
    """Датакласс, представляющий одну задачу."""

    id: int
    title: str
    description: str
    priority: int
    status: str
    deadline: str
    created: str


class ValidationError(Exception):
    """Исключение при ошибке валидации пользовательских данных."""
    pass


def validate_title(title: str) -> str:
    """
    Проверяет корректность названия задачи.


        title: Строка с названием.

    Returns:
        Очищенная строка.

    Raises:
        ValidationError: Если название пустое или превышает 100 символов.
    """
    title = title.strip()
    if not title:
        raise ValidationError("Название задачи не может быть пустым.")
    if len(title) > 100:
        raise ValidationError("Название задачи не должно превышать 100 символов.")
    return title


def validate_description(description: str) -> str:
    """
    Проверяет корректность описания задачи.


        description: Строка с описанием.

    Returns:
        Очищенная строка.

    Raises:
        ValidationError: Если описание пустое.
    """
    description = description.strip()
    if not description:
        raise ValidationError("Описание задачи не может быть пустым.")
    return description


def validate_priority(priority_str: str) -> int:
    """
    Проверяет корректность приоритета.


        priority_str: Строковое представление числа 1–5.

    Returns:
        Целочисленный приоритет.

    Raises:
        ValidationError: Если значение вне диапазона 1–5.
    """
    try:
        priority = int(priority_str)
    except (ValueError, TypeError):
        raise ValidationError("Приоритет должен быть целым числом от 1 до 5.")
    if priority < 1 or priority > 5:
        raise ValidationError("Приоритет должен быть в диапазоне от 1 до 5.")
    return priority


def validate_deadline(deadline_str: str) -> str:
    """
    Проверяет корректность даты дедлайна в формате YYYY-MM-DD.


        deadline_str: Строка с датой.

    Returns:
        Строка с датой (без изменений, если валидна).

    Raises:
        ValidationError: Если дата некорректна (несуществующая, неверный формат).
    """
    deadline_str = deadline_str.strip()
    if not deadline_str:
        raise ValidationError("Дата дедлайна не может быть пустой.")
    try:
        datetime.strptime(deadline_str, DATE_FORMAT)
    except ValueError:
        raise ValidationError(
            f"Некорректная дата: '{deadline_str}'. Используйте формат YYYY-MM-DD "
            f"и убедитесь, что дата реально существует (например, 2026-02-31 недопустима)."
        )
    return deadline_str


def validate_status(status: str) -> str:
    """
    Проверяет, что статус задачи допустим.


        status: Строка статуса.

    Returns:
        Статус без изменений.

    Raises:
        ValidationError: Если статус не входит в список допустимых.
    """
    if status not in STATUSES:
        raise ValidationError(f"Статус должен быть одним из: {', '.join(STATUSES)}.")
    return status


def today_str() -> str:
    """Возвращает текущую дату в формате YYYY-MM-DD."""
    return date.today().strftime(DATE_FORMAT)


def parse_date(date_str: str) -> Optional[date]:
    """
    Безопасно парсит строку даты.


        date_str: Строка в формате YYYY-MM-DD.

    Returns:
        Объект date или None при ошибке.
    """
    try:
        return datetime.strptime(date_str, DATE_FORMAT).date()
    except (ValueError, TypeError):
        return None
