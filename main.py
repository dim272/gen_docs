import sys
import json
from pathlib import Path
from datetime import datetime
from dateutil import parser as dateutil_parser

from docxtpl import DocxTemplate
from PyQt5.QtWidgets import QApplication

from database import DataBaseInterface
from interface import DocxUI
from const import TEMPLATES_DIR, RESULT_DIR, FROM_DATETIME, HISTORY_DATETIME


class GenDocs:
    def __init__(self):
        self.user_variables = {}        # Переменные, вводимые пользователем
        self.template_history = []      # История выбранного шаблона
        self.db = DataBaseInterface()
        self.ui = DocxUI()
        self.ui.listWidget.clicked.connect(self.click_template)
        self.ui.listWidget_3.clicked.connect(self.update_user_variable)
        self.ui.pushButton.clicked.connect(self.collect_user_variables)
        self.ui.listWidget_2.clicked.connect(self.click_history_list)
        self.ui.pushButton_3.clicked.connect(self.clear_user_variables)
        self.ui.pushButton_4.clicked.connect(self.create_button)
        templates = self.get_templates()
        templates_and_variables = self.collect_variables(templates)
        self.db.save_templates(templates_and_variables)
        self.paste_ui_template_list(templates_and_variables)

    @staticmethod
    def get_templates():
        return TEMPLATES_DIR.glob('*.docx')

    def get_variables(self, template_path):
        doc = DocxTemplate(template_path)
        variables = doc.undeclared_template_variables
        return sorted(list(variables))

    def collect_variables(self, template_list):
        variables = {}

        for template_path in template_list:
            template_variables = self.get_variables(template_path)
            variables[template_path.name.split('.docx')[0]] = template_variables

        return variables

    def paste_ui_template_list(self, templates):
        templates = sorted(templates.keys())
        self.ui.paste_list(templates, self.ui.listWidget)

    def click_template(self):
        self.show_history()
        self.show_variables()

    def clear_date(self, date_str):
        date_time = datetime.strptime(date_str, FROM_DATETIME)
        return date_time.strftime(HISTORY_DATETIME)

    def show_history(self):
        template_name = self.ui.listWidget.currentItem().text()
        template_id = self.db.get_template_id(template_name)
        self.template_history = self.db.read_template_history(template_id)
        history_list = [self.clear_date(row[3]) for row in self.template_history]
        self.ui.paste_list(history_list, self.ui.listWidget_2)

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

    def is_variables_correct(self, template_name):
        template_path = Path(TEMPLATES_DIR / template_name)
        template_variables = self.get_variables(template_path)
        for variable in template_variables:
            if variable not in self.user_variables:
                return False
        return True

    def create_button(self):
        template_name = self.ui.listWidget.currentItem().text()
        if self.is_variables_correct(template_name + '.docx'):
            date_time = datetime.now()
            self.generate_document(template_name, date_time)
            self.save_history(template_name, date_time)
        else:
            self.ui.textBrowser.setText('Создание невозможно. Не все значения заполнены.')

    def get_correct_variables(self, doc_obj):
        correct_variables = {}
        template_variables = doc_obj.undeclared_template_variables
        for variable_name in template_variables:
            if variable_name in self.user_variables:
                correct_variables[variable_name] = self.user_variables[variable_name]
        return correct_variables

    def generate_document(self, template_name, date_time):
        datetime_str = date_time.strftime('%d_%h_%Y_%H_%M_%S')
        template_path = Path(TEMPLATES_DIR / (template_name + '.docx'))
        result_path = Path(RESULT_DIR / f'{template_name}_{datetime_str}.docx')
        doc = DocxTemplate(template_path)
        correct_variables = self.get_correct_variables(doc)
        doc.render(correct_variables)
        doc.save(result_path)

    def save_history(self, template_name, date_time):
        used_variables = self.user_variables
        template_id = self.db.get_template_id(template_name)
        self.db.save_history(template_id, used_variables, date_time)

    def click_history_list(self):
        variable = self.ui.listWidget_2.currentItem().text()
        date_time = datetime.strptime(variable, HISTORY_DATETIME)
        date_str = date_time.strftime(FROM_DATETIME)
        for template_row in self.template_history:
            template_datetime = template_row[3]
            template_datetime = template_datetime.split('.')[0] + '.000000'
            if template_datetime == date_str:
                template_variables = json.loads(template_row[2])
                self.user_variables.update(**template_variables)
                break


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gen = GenDocs()
    ui = gen.ui
    ui.show()
    sys.exit(app.exec())

# -- TODO проверять количество переменных
# -- TODO очищать переменные ... -- в автоматическом режиме не будем
# -- TODO не перезаписывать файл
# -- TODO при выборе истории забирать значения переменных из бд
# TODO выводить подсказки в инфо
# TODO изменить переменную с пробелом на нижнее подчёркивание (в ui вернуть)
# TODO убрать .docx из названия в шаблонах
# TODO список история обновлять при нажатии на кнопку создать
# TODO из списка истории убрать миллисекунды

