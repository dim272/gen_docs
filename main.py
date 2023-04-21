import sys
import json

from docxtpl import DocxTemplate
from PyQt5.QtWidgets import QApplication

from database import DataBaseInterface
from interface import DocxUI
from const import TEMPLATES_DIR


class GenDocs:
    def __init__(self):
        self.db = DataBaseInterface()
        self.ui = DocxUI()
        self.ui.listWidget.clicked.connect(self.click_template)
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
            variables[template_path.name] = list(template_variables)

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


# RESULT_DIR = Path().absolute() / 'results'
# TEST_FILE = TEMPLATES_DIR / 'test.docx'
# RESULT = RESULT_DIR / 'result.docx'
#
# doc = DocxTemplate(TEST_FILE)
# context = {
#     'фио': "Петров М. М.",
#     'дни': "14",
#     'дата': "27.07.2023"
# }
# doc.render(context)
# doc.save(RESULT)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gen = GenDocs()
    ui = gen.ui
    ui.show()
    sys.exit(app.exec())
