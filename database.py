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
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                SELECT variables FROM template
                WHERE name=(?)
                """,
                (name,)
            )
            result = cursor.fetchone()
            if result:
                return result[0] == variables

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

    def read_template_by_id(self, template_id):
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
