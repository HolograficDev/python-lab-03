import logging
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from .main_window import BookClubWindow


def main():
    log_file = Path(__file__).resolve().parents[2] / "bookclub.log"
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        encoding="utf-8",
    )

    app = QApplication(sys.argv)
    window = BookClubWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
