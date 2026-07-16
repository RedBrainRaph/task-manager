"""
priority.py Алгоритм интеллектуальной приоритизации задач.

Основная особенность проекта: вычисление итогового рейтинга (score)
для каждой задачи на основе нескольких факторов:
  исходный приоритет пользователя
  срочность (количество дней до дедлайна)
  текущий статус задачи
"""

from datetime import date
from typing import List, Dict

from utils import Task, parse_date, STATUSES


# Коэффициент статуса: чем активнее статус, тем выше вес
STATUS_WEIGHT: Dict[str, float] = {
    "Новая": 1.0,
    "В работе": 1.5,
    "Выполнена": 0.0,
}

# Минимальный возможный score (для выполненных задач)
COMPLETED_SCORE = 0.0


def _deadline_coefficient(deadline_str: str, today: date) -> float:
    """
    Вычисляет коэффициент срочности на основе дней до дедлайна.

    Логика:
      - Просрочено (days < 0): максимальная срочность — 20.0
      - Сегодня (days == 0): очень срочно — 15.0
      - 1–3 дня: высокая срочность — 10.0
      - 4–7 дней: средняя — 6.0
      - 8–14 дней: умеренная — 3.0
      - 15–30 дней: низкая — 1.5
      - Более 30 дней: минимальная — 0.5


        deadline_str: Дата дедлайна в формате YYYY-MM-DD.
        today: Текущая дата.

        Числовой коэффициент срочности.
    """
    deadline = parse_date(deadline_str)
    if deadline is None:
        return 0.0

    days_left = (deadline - today).days

    if days_left < 0:
        return 20.0
    elif days_left == 0:
        return 15.0
    elif days_left <= 3:
        return 10.0
    elif days_left <= 7:
        return 6.0
    elif days_left <= 14:
        return 3.0
    elif days_left <= 30:
        return 1.5
    else:
        return 0.5


def calculate_score(task: Task, today: date | None = None) -> float:
    """
    Вычисляет итоговый интеллектуальный рейтинг задачи.

    Формула:
        score = priority × 2
                + deadline_coefficient
                + status_weight

    Выполненные задачи всегда получают score = 0.0 и опускаются в конец.


        task: Объект Task.
        today: Текущая дата (подставляется автоматически, если None).

    Returns:
        Итоговый числовой рейтинг.
    """
    if today is None:
        today = date.today()

    if task.status == "Выполнена":
        return COMPLETED_SCORE

    priority_score = task.priority * 2.0
    deadline_coef = _deadline_coefficient(task.deadline, today)
    status_coef = STATUS_WEIGHT.get(task.status, 1.0)

    score = priority_score + deadline_coef + status_coef
    return round(score, 4)


def calculate_scores_for_all(tasks: List[Task]) -> Dict[int, float]:
    """
    Вычисляет рейтинги для всех задач.


        tasks: Список задач.


        Словарь {task_id: score}.
    """
    today = date.today()
    return {task.id: calculate_score(task, today) for task in tasks}


def sort_by_score(tasks: List[Task]) -> List[Task]:
    """
    Возвращает список задач, отсортированный по убыванию интеллектуального рейтинга.


        tasks: Исходный список задач.

    Returns:
        Новый список задач, отсортированный по score (высший рейтинг — первый).
    """
    today = date.today()
    return sorted(tasks, key=lambda t: calculate_score(t, today), reverse=True)
