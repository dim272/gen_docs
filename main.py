import sys
import json
from pathlib import Path

from docxtpl import DocxTemplate
from PyQt5.QtWidgets import QApplication

from database import DataBaseInterface
from interface import DocxUI
from const import TEMPLATES_DIR, RESULT_DIR


class GenDocs:
    def __init__(self):
        self.user_variables = {}   # Переменные, вводимые пользователем
        self.db = DataBaseInterface()
        self.ui = DocxUI()
        self.ui.listWidget.clicked.connect(self.click_template)
        self.ui.listWidget_3.clicked.connect(self.update_user_variable)
        self.ui.pushButton.clicked.connect(self.collect_user_variables)
        self.ui.pushButton_3.clicked.connect(self.clear_user_variables)
        self.ui.pushButton_4.clicked.connect(self.generate_document)
        templates = self.get_templates()
        templates_and_variables = self.get_variables(templates)
        self.db.save_templates(templates_and_variables)
        self.paste_ui_template_list(templates_and_variables)

    @staticmethod
    def get_templates():
        return TEMPLATES_DIR.glob('*.docx')

    @staticmethod
    def get_variables(template_list):
        variables = {}

        for template_path in template_list:
            doc = DocxTemplate(template_path)
            template_variables = doc.undeclared_template_variables
            variables[template_path.name] = sorted(list(template_variables))

        return variables

    def paste_ui_template_list(self, templates):
        templates = list(templates.keys())
        self.ui.paste_list(templates, self.ui.listWidget)

    def click_template(self):
        self.show_history()
        self.show_variables()

    def show_history(self):
        template_name = self.ui.listWidget.currentItem().text()
        template_id = self.db.get_template_id(template_name)
        history = self.db.read_template_history(template_id)
        history = [x[3] for x in history]
        self.ui.paste_list(history, self.ui.listWidget_2)

    def show_variables(self):
        template_name = self.ui.listWidget.currentItem().text()
        template_id = self.db.get_template_id(template_name)
        template_row = self.db.read_template_by_id(template_id)
        variables = template_row[2]
        variables = json.loads(variables)
        self.ui.paste_list(variables, self.ui.listWidget_3)

    def collect_user_variables(self):
        variable = self.ui.listWidget_3.currentItem().text()
        value = self.ui.lineEdit.text()
        self.user_variables[variable] = value
        self.ui.textBrowser.setText(json.dumps(self.user_variables))

    def clear_user_variables(self):
        self.user_variables.clear()
        self.ui.textBrowser.setText(json.dumps(self.user_variables))

    def update_user_variable(self):
        variable = self.ui.listWidget_3.currentItem().text()
        if variable in self.user_variables:
            self.ui.lineEdit.setText(self.user_variables[variable])
        else:
            self.ui.lineEdit.clear()

    def create_button(self):
        pass

    def generate_document(self):
        if self.user_variables:
            # TODO проверять количество переменных
            # TODO не перезаписывать файл

            template_name = self.ui.listWidget.currentItem().text()
            template_path = Path(TEMPLATES_DIR / template_name)
            result_path = Path(RESULT_DIR / template_name)
            doc = DocxTemplate(template_path)
            doc.render(self.user_variables)
            doc.save(result_path)

            self.save_history(template_name)
        else:
            self.ui.textBrowser.setText('Создание не возможно. Не все значения заполнены.')

    def save_history(self, template_name):
        used_variables = self.user_variables
        template_id = self.db.get_template_id(template_name)
        self.db.save_history(template_id, used_variables)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gen = GenDocs()
    ui = gen.ui
    ui.show()
    sys.exit(app.exec())
