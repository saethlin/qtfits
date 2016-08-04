import os
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QListWidget, QLineEdit
from PyQt5.QtCore import Qt, QTimer


class DirListEntries(QListWidget):

    def __init__(self):
        super().__init__()
        self.input_box = None
        self.entries = []
        self.handlers = {
            Qt.Key_Up: self.selection_up,
            Qt.Key_Down: self.selection_down,
            Qt.Key_Right: self.select,
            Qt.Key_Left: self.back,
        }
        self.setToolTip('Current directory contents')

        self.directory = os.getcwd()
        self.reload_entries()

        self.timer = QTimer(self)
        self.timer.setInterval(250)
        self.timer.timeout.connect(self.reload_entries)
        self.timer.start()

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
        new_path = os.path.normpath(new_path)
        if os.path.isdir(new_path):
            self.directory = new_path
            self.reload_entries()
            self.setCurrentRow(0)
        elif os.path.isfile(new_path):
            self.app.open(new_path)

    def back(self):
        new_path = os.path.dirname(self.directory)
        if os.path.isdir(new_path):
            self.directory = new_path
            self.reload_entries()
            self.setCurrentRow(0)

    def reload_entries(self):
        entries = [entry.name
                   for entry in os.scandir(self.directory)
                   if (not entry.name.startswith('.')) and
                   (entry.is_dir() or (entry.is_file() and entry.name.endswith('.fits')))]
        self.entries = sorted(entries)
        if self.currentRow() == -1 or (self.input_box is not None and self.input_box.displayText() == ''):
            cur_index = self.currentRow()
            self.clear()
            self.addItems(self.entries)
            self.addItem('..')
            self.setCurrentRow(cur_index)

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.selection_up()
        elif event.angleDelta().y() < 0:
            self.selection_down()

    def mouseDoubleClickEvent(self, QMouseEvent):
        self.select()


class InputBox(QLineEdit):

    def __init__(self, dirlist):
        super().__init__()
        self.dirlist = dirlist
        self.setPlaceholderText('Enter search term')
        self.textChanged[str].connect(self.onChanged)

    def onChanged(self, term):
        if term == '':
            search_results = self.dirlist.entries
        else:
            search_results = [entry for entry in self.dirlist.entries if term.lower() in entry.lower()]

        self.dirlist.clear()
        self.dirlist.addItems(search_results)
        self.dirlist.addItem('..')
        self.dirlist.setCurrentRow(0)


class DirList(QLabel):

    def __init__(self):
        super().__init__()
        self.setFixedWidth(200)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.list = DirListEntries()
        self.layout.addWidget(self.list)

        self.input_box = InputBox(self.list)
        self.layout.addWidget(self.input_box)

        self.input_box.list = self.list
        self.list.input_box = self.input_box
