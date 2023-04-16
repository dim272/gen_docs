import json
import sqlite3
from datetime import datetime

from const import DB_NAME


class DataBaseInterface:

    def __init__(self):
        self.con = sqlite3.connect(DB_NAME)
        self.__init_tables()

    def __init_tables(self):
        with self.con:
            cur = self.con.cursor()
            cur.execute(
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
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS history 
                (
                    id INTEGER PRIMARY KEY,
                    template_id INTEGER NOT NULL,
                    used_variables JSON NOT NULL,
                    use_date DATETIME NOT NULL, 
                    FOREIGN KEY (template_id) REFERENCES template (id) 
                )
                """
            )
            self.con.commit()

    def save_templates(self, template_list):
        with self.con:
            cur = self.con.cursor()
            date_added = datetime.now()
            for template_filename, variables in template_list.items():
                cur.execute(
                    "INSERT OR REPLACE INTO template (path, variables, date_added)"
                    "VALUES (?, ?, ?)",
                    (template_filename, json.dumps(variables), date_added)
                )
            self.con.commit()

    def save_history(self, template_id, used_variables):
        with self.con:
            cur = self.con.cursor()
            date_added = datetime.now()
            cur.execute(
                """
                INSERT INTO history (template_id, used_variables, use_date)
                VALUES (?, ?, ?)
                """,
                (template_id, json.dumps(used_variables), date_added)
            )
            self.con.commit()

    def read_templates(self):
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT * FROM template")
            rows = cur.fetchall()
        return rows

    def read_template_history(self, template_id):
        with self.con:
            cur = self.con.cursor()
            cur.execute(
                """
                SELECT * FROM template
                WHERE template_id = (?)
                """,
                (template_id,)

            )
            history = cur.fetchall()
        return history

if __name__ == '__main__':
    x = DataBaseInterface()
    x.save_templates(
        []
    )
    x.save_history(
        1,
        []
    )

