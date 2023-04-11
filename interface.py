import sys

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QLineEdit, QListWidget
from PyQt5.QtCore import Qt

class DocxUI(QWidget):
    def __init__(self):
        super().__init__()
        self.variables_list = []
        self.initUI()
        self.create_variables(["дата", "ФИО", "Адрес"])


    def initUI(self):
        self.setGeometry(1100, 800, 1100, 800)
        self.setWindowTitle("Gen doxs")

        self.templates_output = QListWidget(self)
        self.templates_output.resize(300, 725)
        self.templates_output.move(25, 55)
        self.templates_output.addItem("Заявление на отпуск")
        self.templates_output.addItem("Извещение")
        self.templates_output.addItem("Протокол")
        self.templates_output.addItem("Характеристика")
        self.templates_output.addItem("Иск")
        self.templates_output.addItem("Постановление")

        self.history_output = QListWidget(self)
        self.history_output.resize(300, 725)
        self.history_output.move(350, 55)
        self.history_output.addItem("20.03.2023")
        self.history_output.addItem("26.03.2023")
        self.history_output.addItem("10.04.2023")

        btn_create = QPushButton('Саздать', self)
        btn_create.resize(125, 25)
        btn_create.move(700, 125)
        btn_create.setStyleSheet('QPushButton {background-color: #A3C1DA }')

        btn_clear = QPushButton('Очистить', self)
        btn_clear.resize(125, 25)
        btn_clear.move(825, 125)
        btn_clear.setStyleSheet('QPushButton {background-color: #A3C1DA }')

        btn_list = QPushButton('Список', self)
        btn_list.resize(125, 25)
        btn_list.move(950, 125)
        btn_list.setStyleSheet('QPushButton {background-color: #A3C1DA }')

        title_info = QLabel(self)
        title_info.resize(50, 25)
        title_info.move(700, 175)
        title_info.setText("ИНФО:")

        data_info = QLabel(self)
        data_info.resize(375, 250)
        data_info.move(700, 200)
        data_info.setText("Выберите шаблон")
        data_info.setAlignment(Qt.AlignTop)

        template_title = QLabel(self)
        template_title.resize(100, 25)
        template_title.move(25, 25)
        template_title.setText("Шаблоны")

        history_title = QLabel(self)
        history_title.resize(100, 25)
        history_title.move(350, 25)
        history_title.setText("История")

    def create_variables(self, variables):
        for index, variable in enumerate(variables):
            label = QLabel(self)
            label.resize(70, 25)
            label.move(700, (index+1)*25)
            label.setText(variable)
            inp = QLineEdit(self)
            inp.resize(300, 25)
            inp.move(775, (index+1)*25)
            self.variables_list.append((label, inp))







if __name__== "__main__":
    app = QApplication(sys.argv)
    ui = DocxUI()
    ui.show()
    sys.exit(app.exec())
