from datetime import date

from PySide6.QtCore import QDate, Signal
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QDateEdit, QFormLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QSpinBox,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)

from .api_client import ApiError, BookClubAPI

STATUS_TITLES = {
    "planned": "В планах",
    "reading": "Читаем",
    "finished": "Прочитана",
}
HEADERS = ["№", "Название", "Автор", "Жанр", "Страниц",
           "Статус", "Предложил", "Оценка", "Прочитана"]


class BooksTab(QWidget):
    """Вкладка «Книги»: таблица, поля ввода и кнопки управления."""

    data_changed = Signal()

    def __init__(self, api: BookClubAPI, parent=None):
        super().__init__(parent)
        self.api = api
        self._selected_id: int | None = None
        self._books: dict[int, dict] = {}

        self._build_form()
        self._build_table()
        self._build_layout()
        self._on_status_changed()

    # ---------- построение интерфейса ----------
    def _build_form(self):
        self.title_edit = QLineEdit()
        self.author_edit = QLineEdit()
        self.genre_edit = QLineEdit()
        self.suggested_edit = QLineEdit()

        self.pages_spin = QSpinBox()
        self.pages_spin.setRange(1, 10000)
        self.pages_spin.setValue(300)

        self.status_combo = QComboBox()
        for value, title in STATUS_TITLES.items():
            self.status_combo.addItem(title, value)
        self.status_combo.currentIndexChanged.connect(self._on_status_changed)

        self.finished_edit = QDateEdit(QDate.currentDate())
        self.finished_edit.setCalendarPopup(True)
        self.finished_edit.setDisplayFormat("dd.MM.yyyy")

        self.rating_combo = QComboBox()
        self.rating_combo.addItem("Без оценки", None)
        for stars in range(1, 6):
            self.rating_combo.addItem(str(stars), stars)

        self.add_button = QPushButton("Добавить")
        self.save_button = QPushButton("Сохранить изменения")
        self.delete_button = QPushButton("Удалить")
        self.clear_button = QPushButton("Очистить форму")
        self.add_button.clicked.connect(self.add_book)
        self.save_button.clicked.connect(self.save_book)
        self.delete_button.clicked.connect(self.delete_book)
        self.clear_button.clicked.connect(self.clear_form)
        self._update_buttons()

    def _build_table(self):
        self.table = QTableWidget(0, len(HEADERS))
        self.table.setHorizontalHeaderLabels(HEADERS)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.itemSelectionChanged.connect(self._on_row_selected)

    def _build_layout(self):
        form = QFormLayout()
        form.addRow("Название:", self.title_edit)
        form.addRow("Автор:", self.author_edit)
        form.addRow("Жанр:", self.genre_edit)
        form.addRow("Страниц:", self.pages_spin)
        form.addRow("Предложил:", self.suggested_edit)
        form.addRow("Статус:", self.status_combo)
        form.addRow("Дата окончания:", self.finished_edit)
        form.addRow("Оценка:", self.rating_combo)

        buttons = QHBoxLayout()
        for button in (self.add_button, self.save_button,
                       self.delete_button, self.clear_button):
            buttons.addWidget(button)

        box_layout = QVBoxLayout()
        box_layout.addLayout(form)
        box_layout.addLayout(buttons)
        box = QGroupBox("Данные книги")
        box.setLayout(box_layout)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Книги книжного клуба"))
        layout.addWidget(self.table, stretch=1)
        layout.addWidget(box)

    # ---------- вспомогательные методы ----------
    def _on_status_changed(self):
        finished = self.status_combo.currentData() == "finished"
        self.finished_edit.setEnabled(finished)
        self.rating_combo.setEnabled(finished)
        if not finished:
            self.rating_combo.setCurrentIndex(0)

    def _update_buttons(self):
        has_selection = self._selected_id is not None
        self.save_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)

    def _collect_form(self) -> dict:
        finished = self.status_combo.currentData() == "finished"
        return {
            "title": self.title_edit.text(),
            "author": self.author_edit.text(),
            "genre": self.genre_edit.text(),
            "pages": self.pages_spin.value(),
            "suggested_by": self.suggested_edit.text(),
            "status": self.status_combo.currentData(),
            "rating": self.rating_combo.currentData() if finished else None,
            "finished_on": (
                self.finished_edit.date().toPython().isoformat()
                if finished else None
            ),
        }

    def _fill_form(self, book: dict):
        self.title_edit.setText(book["title"])
        self.author_edit.setText(book["author"])
        self.genre_edit.setText(book["genre"])
        self.pages_spin.setValue(book["pages"])
        self.suggested_edit.setText(book["suggested_by"])
        self.status_combo.setCurrentIndex(
            self.status_combo.findData(book["status"]))
        self.rating_combo.setCurrentIndex(
            self.rating_combo.findData(book["rating"]))
        if book["finished_on"]:
            day = date.fromisoformat(book["finished_on"])
            self.finished_edit.setDate(QDate(day.year, day.month, day.day))

    def _show_error(self, error: Exception):
        QMessageBox.warning(self, "Ошибка", str(error))

    # ---------- действия ----------
    def load_books(self):
        try:
            books = self.api.get_books()
        except ApiError as error:
            self._show_error(error)
            return

        self._books = {book["id"]: book for book in books}
        self.table.blockSignals(True)
        self.table.setRowCount(len(books))
        for row, book in enumerate(books):
            values = [
                book["id"], book["title"], book["author"], book["genre"],
                book["pages"], STATUS_TITLES[book["status"]],
                book["suggested_by"], book["rating"] or "—",
                book["finished_on"] or "—",
            ]
            for column, value in enumerate(values):
                self.table.setItem(row, column, QTableWidgetItem(str(value)))
        self.table.resizeColumnsToContents()
        self.table.blockSignals(False)

        self._selected_id = None
        self._update_buttons()

    def _on_row_selected(self):
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            return
        book_id = int(self.table.item(rows[0].row(), 0).text())
        self._selected_id = book_id
        self._fill_form(self._books[book_id])
        self._update_buttons()

    def add_book(self):
        try:
            self.api.create_book(self._collect_form())
        except ApiError as error:
            self._show_error(error)
            return
        self.clear_form()
        self.load_books()
        self.data_changed.emit()

    def save_book(self):
        if self._selected_id is None:
            return
        try:
            self.api.update_book(self._selected_id, self._collect_form())
        except ApiError as error:
            self._show_error(error)
            return
        self.load_books()
        self.data_changed.emit()

    def delete_book(self):
        if self._selected_id is None:
            return
        answer = QMessageBox.question(
            self, "Удаление", "Удалить выбранную книгу?")
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            self.api.delete_book(self._selected_id)
        except ApiError as error:
            self._show_error(error)
            return
        self.clear_form()
        self.load_books()
        self.data_changed.emit()

    def clear_form(self):
        self._selected_id = None
        self.table.clearSelection()
        for edit in (self.title_edit, self.author_edit,
                     self.genre_edit, self.suggested_edit):
            edit.clear()
        self.pages_spin.setValue(300)
        self.status_combo.setCurrentIndex(0)
        self.finished_edit.setDate(QDate.currentDate())
        self._update_buttons()
