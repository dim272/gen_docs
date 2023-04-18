import json
import sqlite3
from datetime import datetime

from const import DB_NAME


class DataBaseInterface:

    def __init__(self):
        self.connection = sqlite3.connect(DB_NAME)
        self.__init_tables()

    def __init_tables(self):
        """Создание таблиц в БД"""
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS template 
                (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    path TEXT NOT NULL UNIQUE,
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
        with self.connection:
            cursor = self.connection.cursor()
            date_added = datetime.now()
            for template_filename, variables in templates.items():
                cursor.execute(
                    "INSERT INTO template (path, variables, date_added)"
                    "VALUES (?, ?, ?)",
                    (template_filename, json.dumps(variables), date_added)
                )
            self.connection.commit()

    def save_history(self, template_id, used_variables):
        with self.connection:
            cursor = self.connection.cursor()
            date_added = datetime.now()
            cursor.execute(
                """
                INSERT INTO history (template_id, used_variables, use_date)
                VALUES (?, ?, ?)
                """,
                (template_id, json.dumps(used_variables), date_added)
            )
            self.connection.commit()

    def read_templates(self):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM template")
            rows = cursor.fetchall()
        return rows

    def read_template_history(self, template_id):
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


if __name__ == '__main__':
    x = DataBaseInterface()
    # x.save_templates(
    #     {
    #         'test.docx': ['ФИО', 'Адрес', 'Дата'],
    #         'test2.docx': ['ФИО2', 'Адрес2', 'Дата2']
    #     }
    # )
    #
    # x.save_history(
    #     1,
    #     ['Иванов И.И.', 'Какой-то адрес']
    # )
    # templates = x.read_templates()
    # print(templates)
    # history = x.read_template_history(1)
    # print(history)
