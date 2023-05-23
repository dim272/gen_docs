"""
Файл с классом DocxUI, который объединяет функции для работы приложения.
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow
from docxtpl import DocxTemplate

from database import DataBaseInterface
from const import TEMPLATES_DIR, RESULT_DIR, FROM_DATETIME, HISTORY_DATETIME, RESULT_DIR_NAME


class DocxUI(QMainWindow):
    """ Класс, который управляет интерфейсом и логикой приложения. """

    def __init__(self):
        """
        Инициализация (создание) экземпляра класса.

        1. Инициализируется родительский класс QMainWindow (интерфейс);
        2. Определяем файл в котором содержится разметка интерфейса (interface.ui);
        3. Определяются внутренние переменные (self.user_variables, self.template_history);
        4. Создаётся экземпляр класса DataBaseInterface (self.db);
        5. Вызывается функция создания интерфейса (self.init_ui());
        6. Вызывается метод родительского класса (QMainWindow), которое открывает окно приложения (self.show()).
        """
        super(DocxUI, self).__init__()
        uic.loadUi('interface.ui', self)

        self.user_variables = {}        # Переменные, вводимые пользователем
        self.template_history = []      # История выбранного шаблона

        self.db = DataBaseInterface()
        self.init_ui()
        self.show()

    def init_ui(self):
        """
        Функция создания интерфейса.

        1. Определяет связь элементов интерфейса с функциями;
        2. Сканирует папку с шаблонами и формирует список шаблонов в интерфейсе.
        """
        self.listWidget.clicked.connect(self.click_template)
        self.listWidget_3.clicked.connect(self.update_user_variable)
        self.pushButton.clicked.connect(self.collect_user_variables)
        self.listWidget_2.clicked.connect(self.click_history_list)
        self.pushButton_2.clicked.connect(self.open_result_folder)
        self.pushButton_4.clicked.connect(self.create_button)
        self.pushButton_3.clicked.connect(self.clear_user_variables)
        self.listWidget_3.clicked.connect(self.update_user_variable)
        templates = self.get_templates()
        self.update_templates(templates_and_variables=self.collect_variables(templates))

    def paste_list(self, items, list_obj):
        """
        Формирует в интерфейсе список с переданными объектами.

        :param items: Список строк.
        :param list_obj: Объект списка (listWidget).
        """

        items.sort()
        list_obj.clear()
        for template in items:
            list_obj.addItem(template)

    def update_templates(self, templates_and_variables=None):
        """
        Если шаблоны и переменные переданы, сохраняет их в БД и отображает в интерфейсе.
        В ином случае, отображает стартовое сообщение в "ИНФО".

        :param templates_and_variables: Словарь с названием шаблонов в виде ключа и переменные в виде значения.
        """
        if templates_and_variables:
            self.db.save_templates(templates_and_variables)
            self.paste_ui_template_list(templates_and_variables)
        else:
            self.input_start_message()

    def update_user_variable(self):
        """
        Обновляет элемент "Ввод значения переменной", когда пользователь выбирает переменную из списка.
        """
        variable = self.listWidget_3.currentItem().text()
        if variable in self.user_variables:
            self.lineEdit.setText(self.user_variables[variable])
        else:
            self.lineEdit.clear()

    def paste_ui_template_list(self, templates):
        """
        Обновляется список шаблонов.

        :param templates: Словарь с названием шаблонов в виде ключа и переменные в виде значения.
        """
        templates = sorted(templates.keys())
        self.paste_list(templates, self.listWidget)

    def is_variables_correct(self, template_name):
        """
        Сверяет переменные из шаблона с переменными, введёнными пользователем.
        :param template_name: Имя шаблона.
        :return: False, если переменные не совпадают, иначе возвращает переменные.
        """
        template_path = Path(TEMPLATES_DIR / template_name)
        template_variables = self.get_variables(template_path)
        correct_variables = {}
        for variable in template_variables:
            if variable not in self.user_variables:
                return False
            correct_variables[variable] = self.user_variables[variable]
        return correct_variables

    def create_button(self):
        """
        Логика осуществления генерации шаблона.
        Вызывается при нажатии на кнопку "СОЗДАТЬ".
        """
        template_name = self.listWidget.currentItem().text()
        correct_variables = self.is_variables_correct(template_name + '.docx')
        if correct_variables:
            date_time = datetime.now()
            self.generate_document(template_name, date_time)
            self.save_history(template_name, date_time, correct_variables)
            self.show_history()
        else:
            self.textBrowser.setText('Создание невозможно. Не все значения заполнены.')

    def save_history(self, template_name, date_time, correct_variables):
        """
        Сохраняет в БД значения использованных переменных, при создании документа.

        :param template_name: Название использованного шаблона.
        :param date_time: Дата и время создания документа.
        :param correct_variables: Переменные которые использовал пользователь.
        """
        template_id = self.db.get_template_id(template_name)
        self.db.save_history(template_id, correct_variables, date_time)

    def click_history_list(self):
        """
        Вызывается при нажатии на элемент в списке "История".
        Выводятся сохранённые переменные в окно "ИНФО".
        """
        variable = self.listWidget_2.currentItem().text()
        date_time = datetime.strptime(variable, HISTORY_DATETIME)
        date_str = date_time.strftime(FROM_DATETIME)
        for template_row in self.template_history:
            template_datetime = template_row[3]
            template_datetime = template_datetime.split('.')[0] + '.000000'
            if template_datetime == date_str:
                template_variables = json.loads(template_row[2])
                self.user_variables.update(**template_variables)
                break
        self.textBrowser.setText(self.pretty_user_variables(expected_variables=list(template_variables.keys())))

    def click_template(self):
        """
        Вызывается при нажатии на элемент в списке "Шаблоны".
        Вызывает функции показа истории и переменных.
        """
        self.show_history()
        self.show_variables()
        self.textBrowser.setText('Выберите переменные шаблона в списке истории или введите вручную.')

    def show_history(self):
        """
        Заполняет список "История" данными из БД, если они найдены.
        """
        template_name = self.listWidget.currentItem().text()
        template_id = self.db.get_template_id(template_name)
        self.template_history = self.db.read_template_history(template_id)
        history_list = [self.clear_date(row[3]) for row in self.template_history]
        self.paste_list(history_list, self.listWidget_2)

    def show_variables(self):
        """
        Заполняет список "Переменные" данными из БД, если они найдены.
        """
        template_name = self.listWidget.currentItem().text()
        template_id = self.db.get_template_id(template_name)
        template_row = self.db.read_template_by_id(template_id)
        variables = template_row[2]
        variables = json.loads(variables)
        self.paste_list(variables, self.listWidget_3)

    def open_result_folder(self):
        """
        Вызывается при нажатии на кнопку "РЕЗУЛЬТАТ".
        Открывает папку с результатами.
        """
        try:
            os.startfile(RESULT_DIR)
        except:
            subprocess.Popen(['xdg-open', RESULT_DIR])

    def collect_user_variables(self):
        """
        Вызывается при нажатии на кнопку "СОХРАНИТЬ".
        Сохраняет переменную, введённую пользователем, в словарь self.user_variables.
        Обновляет список переменных в "ИНФО".
        """
        variable = self.listWidget_3.currentItem().text()
        value = self.lineEdit.text()
        self.user_variables[variable] = value
        expected_variables = [self.listWidget_3.item(x).text() for x in range(self.listWidget_3.count())]
        self.textBrowser.setText(self.pretty_user_variables(expected_variables))


    def input_start_message(self):
        """
        Выводит в "ИНФО" сообщение, если папка с шаблонами пуста.
        """

        self.textBrowser.setText('Для начала работы, создайте шаблоны в формате .docx с необходимыми '
                                 'переменными в двойных фигурных скобках:\n\n'
                                 '{{ название_переменной }}\n\n'
                                 f'и сохраните файл в папку\n"{TEMPLATES_DIR}",\n которую поместите рядом с '
                                 'исполнительным файлом')

    def get_templates(self):
        """
        Возвращает список имён шаблонов из папки шаблонов с расширением .docx

        :return: Список названий шаблонов.
        """
        return list(TEMPLATES_DIR.glob('*.docx'))

    def get_variables(self, template_path):
        """
        Возвращает список переменных из шаблона.

        :param template_path: Путь к шаблону.
        :return: Список названий переменных.
        """
        doc = DocxTemplate(template_path)
        variables = doc.undeclared_template_variables
        return sorted(list(variables))

    def collect_variables(self, template_list):
        """
        Обходит все шаблоны в папке шаблонов и формирует словарь,
        где ключом является название шаблона, а значением - список его переменных.

        :param template_list: Список путей к шаблонам.
        :return: Словарь с данными о шаблонах и их переменных.
        """
        variables = {}

        for template_path in template_list:
            template_variables = self.get_variables(template_path)
            variables[template_path.name.split('.docx')[0]] = template_variables

        return variables

    def clear_date(self, date_str):
        """
        Переводит дату в необходимый формат для вывода в списке "История".
        """
        date_time = datetime.strptime(date_str, FROM_DATETIME)
        return date_time.strftime(HISTORY_DATETIME)

    def clear_user_variables(self):
        """
        Вызывается при нажатии на кнопку "ОЧИСТИТЬ".
        Очищает словарь с сохранёнными переменными (self.user_variables).
        """
        self.user_variables.clear()
        self.textBrowser.setText('Все переменные очищены.')

    def get_correct_variables(self, doc_obj):
        """
        Сверяет названия переменных, введённых пользователем, с названиями из объекта docx.
        Необходима для вывода нужных пользователю переменных в "ИНФО".

        :param doc_obj: DocxTemplate объект.
        :return: Возвращает словарь переменных, которые найдены в обоих списках.
        """
        correct_variables = {}
        template_variables = doc_obj.undeclared_template_variables
        for variable_name in template_variables:
            if variable_name in self.user_variables:
                correct_variables[variable_name] = self.user_variables[variable_name]
        return correct_variables

    def generate_document(self, template_name, date_time):
        """
        Создание и сохранения готового документа с использованными переменными пользователя.

        :param template_name: Название шаблона.
        :param date_time: Объект datetime - Дата и время создания документа.
        """
        datetime_str = date_time.strftime('%d %h %Y %H-%M-%S')
        template_path = Path(TEMPLATES_DIR / (template_name + '.docx'))
        file_name = f'{template_name} {datetime_str}.docx'
        result_path = Path(RESULT_DIR / file_name)
        doc = DocxTemplate(template_path)
        correct_variables = self.get_correct_variables(doc)
        doc.render(correct_variables)
        doc.save(result_path)
        self.textBrowser.setText(f'Создан документ:\n"{file_name}"\n и сохранён в папку "{RESULT_DIR_NAME}"')

    def pretty_user_variables(self, expected_variables):
        """
        Преобразует словарь с переменными в читабельный для пользователя вид,
        и выводит результат в "ИНФО".

        :param expected_variables: Переменные.
        """

        result = ''
        for variable in expected_variables:
            if variable in self.user_variables:
                result += f'{variable}: {self.user_variables[variable]}\n'

        result += '\nКогда все значения будут заполнены, нажмите кнопку "Создать".'
        return result
