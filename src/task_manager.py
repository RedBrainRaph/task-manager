"""
task_manager.py — Главный класс TaskManager: бизнес-логика управления задачами.
"""

from datetime import date
from typing import List, Optional, Dict

from utils import (
    Task,
    ValidationError,
    validate_title,
    validate_description,
    validate_priority,
    validate_deadline,
    validate_status,
    today_str,
    parse_date,
    STATUSES,
)
from storage import Storage
from priority import calculate_scores_for_all, sort_by_score, calculate_score


class TaskManager:
    """
    Центральный класс приложения.
    Управляет списком задач, делегирует хранение в Storage,
    вычисление рейтинга — в priority-модуль.
    """

    def __init__(self, storage: Optional[Storage] = None) -> None:
        self._storage = storage or Storage()
        self._tasks: List[Task] = self._storage.load_all()
        self._next_id: int = self._compute_next_id()


    # Вспомогательные методы


    def _compute_next_id(self) -> int:
        """Вычисляет следующий свободный ID на основе загруженных задач."""
        if not self._tasks:
            return 1
        return max(t.id for t in self._tasks) + 1

    def _save(self) -> None:
        """Сохраняет текущий список задач в CSV."""
        self._storage.save_all(self._tasks)

    def _find_by_id(self, task_id: int) -> Optional[Task]:
        """Возвращает задачу по ID или None, если не найдена."""
        for task in self._tasks:
            if task.id == task_id:
                return task
        return None


    # CRUD


    def add_task(
        self,
        title: str,
        description: str,
        priority: str,
        deadline: str,
        status: str = "Новая",
    ) -> Task:
        """
        Создаёт и добавляет новую задачу после полной валидации.


            title: Название задачи.
            description: Описание задачи.
            priority: Приоритет от 1 до 5 (строка).
            deadline: Дата дедлайна в формате YYYY-MM-DD.
            status: Статус (по умолчанию «Новая»).

        Returns:
            Созданный объект Task.

        Raises:
            ValidationError: При ошибке валидации любого поля.
        """
        validated_title = validate_title(title)
        validated_description = validate_description(description)
        validated_priority = validate_priority(priority)
        validated_deadline = validate_deadline(deadline)
        validated_status = validate_status(status)

        task = Task(
            id=self._next_id,
            title=validated_title,
            description=validated_description,
            priority=validated_priority,
            status=validated_status,
            deadline=validated_deadline,
            created=today_str(),
        )

        self._tasks.append(task)
        self._next_id += 1
        self._save()
        return task

    def update_task(
        self,
        task_id: int,
        title: str,
        description: str,
        priority: str,
        deadline: str,
        status: str,
    ) -> Task:
        """
        Обновляет существующую задачу.

        Args:
            task_id: ID задачи для обновления.
            title: Новое название.
            description: Новое описание.
            priority: Новый приоритет (строка).
            deadline: Новый дедлайн.
            status: Новый статус.

        Returns:
            Обновлённый объект Task.

        Raises:
            ValueError: Если задача с таким ID не найдена.
            ValidationError: При ошибке валидации.
        """
        task = self._find_by_id(task_id)
        if task is None:
            raise ValueError(f"Задача с ID {task_id} не найдена.")

        validated_title = validate_title(title)
        validated_description = validate_description(description)
        validated_priority = validate_priority(priority)
        validated_deadline = validate_deadline(deadline)
        validated_status = validate_status(status)

        task.title = validated_title
        task.description = validated_description
        task.priority = validated_priority
        task.deadline = validated_deadline
        task.status = validated_status

        self._save()
        return task

    def delete_task(self, task_id: int) -> None:
        """
        Удаляет задачу по ID.

        Args:
            task_id: ID задачи для удаления.

        Raises:
            ValueError: Если задача не найдена.
        """
        task = self._find_by_id(task_id)
        if task is None:
            raise ValueError(f"Задача с ID {task_id} не найдена.")
        self._tasks.remove(task)
        self._save()


    # Получение и фильтрация


    def get_all(self) -> List[Task]:
        """Возвращает копию списка всех задач."""
        return list(self._tasks)

    def get_scores(self) -> Dict[int, float]:
        """Возвращает словарь рейтингов {task_id: score} для всех задач."""
        return calculate_scores_for_all(self._tasks)

    def search(self, query: str) -> List[Task]:
        """
        Ищет задачи по частичному совпадению в названии (без учёта регистра).


            query: Строка поиска.

        Returns:
            Список подходящих задач.
        """
        query_lower = query.lower().strip()
        if not query_lower:
            return list(self._tasks)
        return [t for t in self._tasks if query_lower in t.title.lower()]

    def filter_tasks(
        self,
        status: Optional[str] = None,
        priority: Optional[int] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        title_query: Optional[str] = None,
    ) -> List[Task]:
        """
        Фильтрует задачи по нескольким критериям одновременно.


            status: Фильтр по статусу.
            priority: Фильтр по приоритету.
            date_from: Фильтр «не раньше» (дедлайн >= date_from).
            date_to: Фильтр «не позже» (дедлайн <= date_to).
            title_query: Подстрока для поиска в названии.

        Returns:
            Отфильтрованный список задач.
        """
        result = list(self._tasks)

        if status and status != "Все":
            result = [t for t in result if t.status == status]

        if priority is not None:
            result = [t for t in result if t.priority == priority]

        if date_from:
            parsed_from = parse_date(date_from)
            if parsed_from:
                result = [
                    t for t in result
                    if parse_date(t.deadline) is not None
                    and parse_date(t.deadline) >= parsed_from
                ]

        if date_to:
            parsed_to = parse_date(date_to)
            if parsed_to:
                result = [
                    t for t in result
                    if parse_date(t.deadline) is not None
                    and parse_date(t.deadline) <= parsed_to
                ]

        if title_query:
            q = title_query.lower().strip()
            result = [t for t in result if q in t.title.lower()]

        return result


    # Сортировка


    def sort_tasks(self, tasks: List[Task], sort_key: str, ascending: bool = True) -> List[Task]:
        """
        Сортирует переданный список задач по выбранному критерию.


            tasks: Список задач для сортировки.
            sort_key: Ключ сортировки:
                'title'    — по названию,
                'created'  — по дате создания,
                'deadline' — по дедлайну,
                'priority' — по приоритету,
                'score'    — по интеллектуальному рейтингу.
            ascending: True — по возрастанию, False — по убыванию.

        Returns:
            Отсортированный список задач.
        """
        today = date.today()

        if sort_key == "title":
            sorted_tasks = sorted(tasks, key=lambda t: t.title.lower(), reverse=not ascending)
        elif sort_key == "created":
            sorted_tasks = sorted(
                tasks,
                key=lambda t: parse_date(t.created) or date.min,
                reverse=not ascending,
            )
        elif sort_key == "deadline":
            sorted_tasks = sorted(
                tasks,
                key=lambda t: parse_date(t.deadline) or date.max,
                reverse=not ascending,
            )
        elif sort_key == "priority":
            sorted_tasks = sorted(tasks, key=lambda t: t.priority, reverse=not ascending)
        elif sort_key == "score":
            sorted_tasks = sorted(
                tasks,
                key=lambda t: calculate_score(t, today),
                reverse=not ascending,
            )
        else:
            sorted_tasks = list(tasks)

        return sorted_tasks


    # Экспорт


    def export_report(self, output_path: str = "report.csv") -> str:
        """
        Экспортирует отчёт с интеллектуальным рейтингом в CSV файл.
        Задачи сортируются по убыванию рейтинга перед записью.


            output_path: Путь к файлу отчёта.

        Returns:
            Абсолютный путь к созданному файлу.
        """
        sorted_tasks = sort_by_score(self._tasks)
        scores = calculate_scores_for_all(self._tasks)
        return self._storage.export_report(sorted_tasks, scores, output_path)
