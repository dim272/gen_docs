"""Файл содержит класс DataBaseInterface который объединяет методы для работы с базой данных"""

import json
import sqlite3
from datetime import datetime

from const import DB_NAME


class DataBaseInterface:
    """
    Класс для работы с базой данных.
    """

    def __init__(self):
        """
        1. Создаётся связь с бд sqlite3
        2. Вызывается функция для создания таблиц.
        """
        self.connection = sqlite3.connect(DB_NAME)
        self.init_tables()

    def init_tables(self):
        """
        Создаются таблицы в БД.

        1. С помощью контекстного менеджера открывается соединение с бд;
        2. Создаётся объект курсора, с помощью которого будут передаваться команды;
        3. Передаются две команды для создания таблиц, если они не созданы;
        4. С помощью метода self.connection.commit(), команды выполняются.
        """
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS template 
                (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    variables JSON NOT NULL,
                    date_added DATETIME NOT NULL
                )
                """
                )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS history 
                (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_id INTEGER NOT NULL,
                    used_variables JSON NOT NULL,
                    use_date DATETIME NOT NULL, 
                    FOREIGN KEY (template_id) REFERENCES template (id) 
                )
                """
            )
            self.connection.commit()

    def save_templates(self, templates):
        """
        Сохраняет данные о шаблонах в таблицу template.

        :param templates: Словарь в котором ключом является название шаблона из папки шаблонов,
        а значением является список его переменных.
            Пример:
                {
                    "Заявление на отпуск": ["фио", "дни", "дата"],
                    "Командировка": ["фио", "должность", "город", "дата"]
                }

        """
        with self.connection:
            cursor = self.connection.cursor()
            date_added = datetime.now()
            for template_filename, variables in templates.items():
                json_variables = json.dumps(variables)
                if not self.template_exist(template_filename, json_variables):
                    cursor.execute(
                        "INSERT INTO template (name, variables, date_added)"
                        "VALUES (?, ?, ?)",
                        (template_filename, json_variables, date_added)
                    )
            self.connection.commit()

    def template_exist(self, name, variables):
        """
        Производит поиск шаблона в таблице template.

        :param name: Имя шаблона.
        :param variables: Переменные шаблона.
        :return: True, если шаблон найден, иначе False.
        """
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                SELECT variables FROM template
                WHERE name=(?)
                """,
                (name,)
            )
            result = cursor.fetchall()
            for row in result:
                if row[0] == variables:
                    return True
            return False

    def save_history(self, template_id, used_variables, date_added):
        """
        Сохраняет в таблицу history, переменные которые использовал пользователь при генерации нового документа.

        :param template_id: Номер шаблона из таблицы template.
        :param used_variables: Список используемых переменных.
        :param date_added: Дата создания документа.
        """

        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                INSERT INTO history (template_id, used_variables, use_date)
                VALUES (?, ?, ?)
                """,
                (template_id, json.dumps(used_variables), date_added)
            )
            self.connection.commit()

    def read_templates(self):
        """
        Запрашивает все данные из таблицы template.

        :return: Список кортежей с данными из таблицы.
        """
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM template")
            rows = cursor.fetchall()
        return rows

    def read_template_by_id(self, template_id):
        """
        Запрашивает данные о шаблоне по его id.

        :param template_id: Номер шаблона в таблице template.
        :return: Кортеж с данными о шаблоне.
        """
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                SELECT * FROM template
                WHERE id = (?)
                """,
                (template_id,)
            )
            template = cursor.fetchone()
        return template

    def read_template_history(self, template_id):
        """
        Запрашивает строки из таблицы history с заданным template_id

        :param template_id: Номер шаблона в таблице template.
        :return: Список кортежей с данными об истории использования шаблона.
        """

        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                SELECT * FROM history
                WHERE template_id = (?)
                """,
                (template_id,)
            )
            history = cursor.fetchall()
        return history

    def get_template_id(self, template_name):
        """
        Запрашивает последний существующий номер шаблона с определённым именем.

        :param template_name: Имя шаблона.
        :return: Номер шаблона.
        """

        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                SELECT id FROM template
                WHERE name = (?)
                ORDER BY id DESC
                """,
                (template_name,)
            )
            template_id = cursor.fetchone()
        return template_id[0]
