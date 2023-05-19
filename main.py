import sys

from PyQt5.QtWidgets import QApplication

from interface import DocxUI
from const import TEMPLATES_DIR, RESULT_DIR


class GenDocs:
    def __init__(self):
        self.init_work_dirs()
        self.ui = DocxUI()

    @staticmethod
    def init_work_dirs():
        for path in [RESULT_DIR, TEMPLATES_DIR]:
            if not path.is_dir():
                path.mkdir()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gen = GenDocs()
    ui = gen.ui
    ui.show()
    sys.exit(app.exec())


# TODO stand-alone
