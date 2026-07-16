"""
storage.py — Модуль хранения данных в CSV файле.
Отвечает за чтение и запись задач через csv.DictReader / csv.DictWriter.
"""

import csv
import os
from dataclasses import asdict
from typing import List

from utils import Task, CSV_FIELDNAMES, DATA_FILE


class Storage:
    """Класс для работы с CSV-хранилищем задач."""

    def __init__(self, filepath: str = DATA_FILE) -> None:
        self.filepath = filepath
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Создаёт CSV файл с заголовками, если он ещё не существует."""
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
                writer.writeheader()

    def load_all(self) -> List[Task]:
        """
        Читает все задачи из CSV файла.

        Returns:
            Список объектов Task.
        """
        tasks: List[Task] = []
        try:
            with open(self.filepath, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        task = Task(
                            id=int(row["id"]),
                            title=row["title"],
                            description=row["description"],
                            priority=int(row["priority"]),
                            status=row["status"],
                            deadline=row["deadline"],
                            created=row["created"],
                        )
                        tasks.append(task)
                    except (KeyError, ValueError):
                        continue
        except FileNotFoundError:
            self._ensure_file_exists()
        return tasks

    def save_all(self, tasks: List[Task]) -> None:
        """
        Перезаписывает CSV файл полным списком задач.


            tasks: Список объектов Task для сохранения.
        """
        with open(self.filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
            writer.writeheader()
            for task in tasks:
                writer.writerow(asdict(task))

    def export_report(self, tasks: List[Task], scores: dict, output_path: str = "report.csv") -> str:
        """
        Экспортирует отчёт с интеллектуальным рейтингом в отдельный CSV файл.


            tasks: Список задач.
            scores: Словарь {task_id: score}.
            output_path: Путь к файлу отчёта.

        Returns:
            Абсолютный путь к созданному отчёту.
        """
        report_fields = ["number", "title", "priority", "status", "deadline", "score"]
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=report_fields)
            writer.writeheader()
            for idx, task in enumerate(tasks, start=1):
                writer.writerow(
                    {
                        "number": idx,
                        "title": task.title,
                        "priority": task.priority,
                        "status": task.status,
                        "deadline": task.deadline,
                        "score": round(scores.get(task.id, 0.0), 2),
                    }
                )
        return os.path.abspath(output_path)
