from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow


class DocxUI(QMainWindow):
    def __init__(self):
        super(DocxUI, self).__init__()
        uic.loadUi('interface.ui', self)
        self.show()

    def paste_list(self, items, list_obj):
        items.sort()
        list_obj.clear()
        for template in items:
            list_obj.addItem(template)
