import os
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QListWidget, QLineEdit
from PyQt5.QtCore import Qt


class DirList(QLabel):

    def __init__(self):
        super(DirList, self).__init__()
        self.main = None
        self.app = None
        self.entries = []
        self.setFixedWidth(200)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.list = QListWidget()
        self.layout.addWidget(self.list)
        self.list.mouseDoubleClickEvent = self.select

        self.input_box = QLineEdit()
        self.layout.addWidget(self.input_box)

        self.input_box.setPlaceholderText('Enter search term')
        self.input_box.textChanged[str].connect(self.onChanged)

        self.directory = os.getcwd()
        self.reload_entries()

        self.handlers = {
            Qt.Key_Up: self.selection_up,
            Qt.Key_Down: self.selection_down,
            Qt.Key_Right: self.select,
            Qt.Key_Left: self.back,
        }

    def reload_entries(self):
        entries = [entry.name for entry in os.scandir(self.directory)
                   if (not entry.name.startswith('.')) and (entry.is_dir() or (entry.is_file() and entry.name.endswith('.fits')))]
        self.entries = sorted(entries)
        self.list.clear()
        self.list.addItems(self.entries)
        self.list.addItem('..')
        self.list.setCurrentRow(0)

    def selection_up(self):
        index = self.list.currentRow() - 1
        if index < 0:
            index = len(self.list) - 1
        self.list.setCurrentRow(index)

    def selection_down(self):
        index = self.list.currentRow() + 1
        if index > len(self.list) - 1:
            index = 0
        self.list.setCurrentRow(index)

    def select(self, *args):
        new_path = os.path.join(self.directory, str(self.list.currentItem().text()))
        if os.path.isdir(new_path):
            self.directory = new_path
            self.reload_entries()
        elif os.path.isfile(new_path):
            self.app.open(new_path)

    def back(self):
        new_path = os.path.dirname(self.directory)
        if os.path.isdir(new_path):
            self.directory = new_path
            self.reload_entries()

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.selection_up()
        elif event.angleDelta().y() < 0:
            self.selection_down()

    def keyPressEvent(self, event):
        if event.key() in self.handlers:
            self.handlers[event.key()]()
        elif event.key() == Qt.Key_Escape:
            self.main.keyPressEvent(event)
        else:
            self.input_box.keyPressEvent(event)

    def onChanged(self, term):
        if term == '':
            search_results = self.entries
        else:
            search_results = [entry for entry in self.entries if term.lower() in entry.lower()]

        self.list.clear()
        self.list.addItems(search_results)
        self.list.addItem('..')
        self.list.setCurrentRow(0)