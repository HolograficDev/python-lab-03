from datetime import datetime

from PySide6.QtWidgets import (
    QAbstractItemView, QMessageBox, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget,
)

from .api_client import ApiError, BookClubAPI

ACTION_TITLES = {
    "created": "Создание",
    "updated": "Изменение",
    "deleted": "Удаление",
}


class ActivityTab(QWidget):
    """Вкладка «Журнал»: история создания, изменения и удаления книг."""

    def __init__(self, api: BookClubAPI, parent=None):
        super().__init__(parent)
        self.api = api

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(
            ["Время", "Действие", "№ книги", "Описание"])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)

        layout = QVBoxLayout(self)
        layout.addWidget(self.table)

    def load_activity_log(self):
        try:
            entries = self.api.get_activity_log()
        except ApiError as error:
            QMessageBox.warning(self, "Ошибка", str(error))
            return

        self.table.setRowCount(len(entries))
        for row, entry in enumerate(entries):
            moment = datetime.fromisoformat(entry["created_at"])
            values = [
                moment.astimezone().strftime("%d.%m.%Y %H:%M:%S"),
                ACTION_TITLES[entry["action"]],
                str(entry["book_id"]),
                entry["details"],
            ]
            for column, value in enumerate(values):
                self.table.setItem(row, column, QTableWidgetItem(value))
        self.table.resizeColumnsToContents()
