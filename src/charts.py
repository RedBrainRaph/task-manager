"""
charts.py — Построение аналитических графиков через matplotlib.

Три графика:
  1. Количество задач по статусу (столбчатая диаграмма).
  2. Количество задач по приоритету (горизонтальная столбчатая диаграмма).
  3. Распределение задач по срокам дедлайна (временная шкала / scatter).
"""

from datetime import date
from typing import List, Dict

import matplotlib
matplotlib.use("TkAgg")  # указываем бэкенд для Tkinter-приложений

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

from utils import Task, STATUSES, PRIORITY_LABELS, parse_date


# Цветовая палитра для статусов
STATUS_COLORS: Dict[str, str] = {
    "Новая": "#4A90D9",
    "В работе": "#F5A623",
    "Выполнена": "#7ED321",
}

PRIORITY_COLORS = ["#D0E8FF", "#80BFFF", "#4A90D9", "#F5A623", "#E74C3C"]


class ChartsWindow:
    """
    Класс, открывающий отдельное Tkinter-окно с тремя вкладками графиков.
    """

    def __init__(self, parent: tk.Widget, tasks: List[Task]) -> None:
        self._tasks = tasks
        self._window = tk.Toplevel(parent)
        self._window.title("Аналитика задач")
        self._window.geometry("900x620")
        self._window.resizable(True, True)
        self._window.grab_set()

        self._notebook = tk.ttk.Notebook(self._window)
        self._notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self._build_status_chart()
        self._build_priority_chart()
        self._build_deadline_chart()


    # График 1: задачи по статусу


    def _build_status_chart(self) -> None:
        """Столбчатая диаграмма количества задач каждого статуса."""
        frame = tk.Frame(self._notebook, bg="white")
        self._notebook.add(frame, text="По статусу")

        counts = {s: 0 for s in STATUSES}
        for task in self._tasks:
            if task.status in counts:
                counts[task.status] += 1

        fig = Figure(figsize=(8, 5), dpi=100, facecolor="white")
        ax = fig.add_subplot(111)

        statuses = list(counts.keys())
        values = list(counts.values())
        colors = [STATUS_COLORS.get(s, "#888888") for s in statuses]

        bars = ax.bar(statuses, values, color=colors, width=0.5, edgecolor="white", linewidth=1.5)

        ax.set_title("Количество задач по статусу", fontsize=14, fontweight="bold", pad=15)
        ax.set_xlabel("Статус", fontsize=11)
        ax.set_ylabel("Количество задач", fontsize=11)
        ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
        ax.set_facecolor("#F9F9F9")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        for bar, val in zip(bars, values):
            if val > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.05,
                    str(val),
                    ha="center",
                    va="bottom",
                    fontsize=12,
                    fontweight="bold",
                )

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


    # График 2: задачи по приоритету


    def _build_priority_chart(self) -> None:
        """Горизонтальная столбчатая диаграмма количества задач по приоритету."""
        frame = tk.Frame(self._notebook, bg="white")
        self._notebook.add(frame, text="По приоритету")

        counts = {p: 0 for p in range(1, 6)}
        for task in self._tasks:
            if 1 <= task.priority <= 5:
                counts[task.priority] += 1

        fig = Figure(figsize=(8, 5), dpi=100, facecolor="white")
        ax = fig.add_subplot(111)

        priorities = list(counts.keys())
        values = list(counts.values())
        labels = [PRIORITY_LABELS[p] for p in priorities]
        colors = PRIORITY_COLORS

        bars = ax.barh(labels, values, color=colors, edgecolor="white", linewidth=1.5)

        ax.set_title("Количество задач по приоритету", fontsize=14, fontweight="bold", pad=15)
        ax.set_xlabel("Количество задач", fontsize=11)
        ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
        ax.set_facecolor("#F9F9F9")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.invert_yaxis()

        for bar, val in zip(bars, values):
            if val > 0:
                ax.text(
                    bar.get_width() + 0.05,
                    bar.get_y() + bar.get_height() / 2,
                    str(val),
                    ha="left",
                    va="center",
                    fontsize=11,
                    fontweight="bold",
                )

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


    # График 3: распределение задач по дедлайнам


    def _build_deadline_chart(self) -> None:
        """Диаграмма рассеяния (scatter): задачи на временной шкале дедлайнов."""
        frame = tk.Frame(self._notebook, bg="white")
        self._notebook.add(frame, text="По срокам")

        today = date.today()
        task_dates: List[date] = []
        task_priorities: List[int] = []
        task_colors_list: List[str] = []
        task_labels_scatter: List[str] = []

        for task in self._tasks:
            d = parse_date(task.deadline)
            if d is not None:
                task_dates.append(d)
                task_priorities.append(task.priority)
                days_left = (d - today).days
                if days_left < 0:
                    color = "#E74C3C"
                elif days_left == 0:
                    color = "#F39C12"
                elif days_left <= 7:
                    color = "#F5A623"
                else:
                    color = "#4A90D9"
                task_colors_list.append(color)
                task_labels_scatter.append(task.title[:20])

        fig = Figure(figsize=(8, 5), dpi=100, facecolor="white")
        ax = fig.add_subplot(111)

        if task_dates:
            import matplotlib.dates as mdates

            x_vals = [mdates.date2num(d) for d in task_dates]
            scatter = ax.scatter(
                x_vals,
                task_priorities,
                c=task_colors_list,
                s=[p * 40 for p in task_priorities],
                alpha=0.8,
                edgecolors="white",
                linewidths=1.5,
                zorder=3,
            )

            ax.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m.%Y"))
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            fig.autofmt_xdate(rotation=30, ha="right")

            ax.set_yticks(range(1, 6))
            ax.set_yticklabels([PRIORITY_LABELS[p] for p in range(1, 6)], fontsize=9)
        else:
            ax.text(
                0.5, 0.5,
                "Нет задач с датой дедлайна",
                ha="center", va="center",
                transform=ax.transAxes,
                fontsize=13,
                color="#888888",
            )

        ax.set_title("Распределение задач по срокам дедлайна", fontsize=14, fontweight="bold", pad=15)
        ax.set_xlabel("Дата дедлайна", fontsize=11)
        ax.set_ylabel("Приоритет", fontsize=11)
        ax.set_facecolor("#F9F9F9")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="x", linestyle="--", alpha=0.4)

        # Легенда
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], marker="o", color="w", markerfacecolor="#E74C3C", markersize=10, label="Просрочено"),
            Line2D([0], [0], marker="o", color="w", markerfacecolor="#F39C12", markersize=10, label="Сегодня"),
            Line2D([0], [0], marker="o", color="w", markerfacecolor="#F5A623", markersize=10, label="≤ 7 дней"),
            Line2D([0], [0], marker="o", color="w", markerfacecolor="#4A90D9", markersize=10, label="> 7 дней"),
        ]
        ax.legend(handles=legend_elements, loc="upper left", fontsize=9, framealpha=0.7)

        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
