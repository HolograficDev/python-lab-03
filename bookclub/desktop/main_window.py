from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QMessageBox, QTabWidget

from .activity_tab import ActivityTab
from .api_client import BookClubAPI
from .books_tab import BooksTab
from .statistics_tab import StatisticsTab


class BookClubWindow(QMainWindow):
    """Главное окно: меню, вкладки и строка состояния."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Книжный клуб")
        self.resize(950, 700)

        self.api = BookClubAPI()
        self.books_tab = BooksTab(self.api)
        self.statistics_tab = StatisticsTab(self.api)
        self.activity_tab = ActivityTab(self.api)

        self.tabs = QTabWidget()
        self.tabs.addTab(self.books_tab, "Книги")
        self.tabs.addTab(self.statistics_tab, "Статистика")
        self.tabs.addTab(self.activity_tab, "Журнал")
        self.setCentralWidget(self.tabs)

        self._build_menu()
        self.books_tab.data_changed.connect(self.refresh_all)
        self.tabs.currentChanged.connect(self._on_tab_changed)

        self.refresh_all()
        self.statusBar().showMessage("Готово")

    def _build_menu(self):
        file_menu = self.menuBar().addMenu("Файл")

        refresh_action = QAction("Обновить данные", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_all)
        file_menu.addAction(refresh_action)

        file_menu.addSeparator()
        exit_action = QAction("Выход", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = self.menuBar().addMenu("Справка")
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def refresh_all(self):
        self.books_tab.load_books()
        self.statistics_tab.load_statistics()
        self.activity_tab.load_activity_log()
        self.statusBar().showMessage("Данные обновлены", 3000)

    def _on_tab_changed(self, index: int):
        tab = self.tabs.widget(index)
        if tab is self.statistics_tab:
            self.statistics_tab.load_statistics()
        elif tab is self.activity_tab:
            self.activity_tab.load_activity_log()

    def show_about(self):
        QMessageBox.information(
            self,
            "О программе",
            "Книжный клуб — система учёта книг.\n\n"
            "Добавляйте книги, отмечайте статус чтения, ставьте оценки "
            "и следите за активностью клуба на графике.",
        )
