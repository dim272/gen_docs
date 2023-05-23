"""
Файл, который запускает приложение.
"""

import sys

from PyQt5.QtWidgets import QApplication

from interface import DocxUI
from const import TEMPLATES_DIR, RESULT_DIR


class GenDocs:
    """ Основной класс приложения, запускающий его. """

    def __init__(self):
        """
        Инициализация (создание) экземпляра класса.

        1. Вызывается функция проверки папок с результатами и шаблонами;
        2. Создаётся экземпляр класса DocxUI, в котором собрана логика приложения.
        """
        self.init_work_dirs()
        self.ui = DocxUI()

    @staticmethod
    def init_work_dirs():
        """
        Проверяются на наличие директории папок с шаблонами и результатами.
        Если папки нет - она создаётся.
        """
        for path in [RESULT_DIR, TEMPLATES_DIR]:
            if not path.is_dir():
                path.mkdir()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gen = GenDocs()
    ui = gen.ui
    ui.show()
    sys.exit(app.exec())
