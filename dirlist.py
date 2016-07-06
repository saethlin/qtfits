import os
from PyQt5.QtWidgets import QListWidget


class DirList(QListWidget):

    def __init__(self, parent):
        super(DirList, self).__init__()
        self.parent = parent
        self.setFixedWidth(200)
        self.directory = os.getcwd()
        self.reload_entries()
        self.setCurrentRow(0)

    def reload_entries(self):
        entries = [entry.name for entry in os.scandir(self.directory)
                   if entry.is_dir() or (entry.is_file() and entry.name.endswith('.fits'))]

        self.clear()
        self.addItems(entries)
        self.addItem('..')

    def selection_up(self):
        index = self.currentRow() - 1
        if index < 0:
            index = len(self) - 1
        self.setCurrentRow(index)

    def selection_down(self):
        index = self.currentRow() + 1
        if index > len(self) - 1:
            index = 0
        self.setCurrentRow(index)

    def select(self):
        new_path = os.path.join(self.directory, str(self.currentItem().text()))
        if os.path.isdir(new_path):
            self.directory = new_path
            self.reload_entries()
        elif os.path.isfile(new_path):
            self.parent.open(new_path)

    def back(self):
        new_path = os.path.dirname(self.directory)
        if os.path.isdir(new_path):
            self.directory = new_path
            self.reload_entries()

    def keyPressEvent(self, event):
        self.parent.keyPressEvent(event)
