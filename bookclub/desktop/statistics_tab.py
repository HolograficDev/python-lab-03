import os

os.environ.setdefault("QT_API", "pyside6")

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PySide6.QtWidgets import QGridLayout, QLabel, QMessageBox, QVBoxLayout, QWidget

from .api_client import ApiError, BookClubAPI


class StatisticsTab(QWidget):
    """Вкладка «Статистика»: показатели и график активности чтения."""

    def __init__(self, api: BookClubAPI, parent=None):
        super().__init__(parent)
        self.api = api

        self.labels: dict[str, QLabel] = {}
        grid = QGridLayout()
        captions = [
            ("total", "Всего книг:"),
            ("finished", "Прочитано:"),
            ("reading", "Читаем сейчас:"),
            ("planned", "В планах:"),
            ("average", "Средняя оценка:"),
            ("pages", "Страниц прочитано:"),
            ("best", "Лучшая книга:"),
        ]
        for row, (key, caption) in enumerate(captions):
            grid.addWidget(QLabel(caption), row, 0)
            value = QLabel("—")
            self.labels[key] = value
            grid.addWidget(value, row, 1)
        grid.setColumnStretch(1, 1)

        self.figure = Figure(figsize=(6, 3))
        self.canvas = FigureCanvasQTAgg(self.figure)

        layout = QVBoxLayout(self)
        layout.addLayout(grid)
        layout.addWidget(self.canvas, stretch=1)

    def load_statistics(self):
        try:
            stats = self.api.get_statistics()
        except ApiError as error:
            QMessageBox.warning(self, "Ошибка", str(error))
            return

        by_status = stats["by_status"]
        average = stats["average_rating"]
        best = stats["best_book"]

        self.labels["total"].setText(str(stats["total_count"]))
        self.labels["finished"].setText(str(by_status["finished"]))
        self.labels["reading"].setText(str(by_status["reading"]))
        self.labels["planned"].setText(str(by_status["planned"]))
        self.labels["average"].setText(
            f"{average:.2f}" if average is not None else "—")
        self.labels["pages"].setText(str(stats["total_pages_read"]))
        self.labels["best"].setText(
            f"{best['title']} ({best['rating']}/5)" if best else "—")

        self._draw_chart(stats["finished_by_month"])

    def _draw_chart(self, finished_by_month: list[dict]):
        self.figure.clear()
        axes = self.figure.add_subplot(111)
        months = [item["month"] for item in finished_by_month]
        counts = [item["count"] for item in finished_by_month]

        if months:
            axes.bar(months, counts, color="#8a6a43")
            axes.set_ylim(0, max(counts) + 1)
            axes.yaxis.get_major_locator().set_params(integer=True)
        else:
            axes.text(0.5, 0.5, "Нет прочитанных книг",
                      ha="center", va="center", transform=axes.transAxes)

        axes.set_title("Активность клуба: прочитано книг по месяцам")
        axes.set_xlabel("Месяц")
        axes.set_ylabel("Книг")
        self.figure.tight_layout()
        self.canvas.draw()
