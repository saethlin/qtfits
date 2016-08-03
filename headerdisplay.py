# TODO: Programatic width adjustment to 80 characters
from PyQt5.QtWidgets import QPlainTextEdit, QDialog, QVBoxLayout, QLineEdit
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class HeaderDisplay(QDialog):

    def __init__(self, header):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.setMinimumWidth(750)
        self.resize(750, 500)
        self.setWindowTitle('Header display')

        self.cards = [header[start:start+80] for start in range(0, len(header), 80)]

        self.display = QPlainTextEdit('\n'.join(self.cards))
        self.layout.addWidget(self.display)
        self.display.setReadOnly(True)
        self.display.setFocusPolicy(Qt.NoFocus)
        self.display.setFont(QFont("Courier New"))
        self.display.setPlaceholderText('No results found')

        self.input_box = QLineEdit()
        self.layout.addWidget(self.input_box)
        self.input_box.setPlaceholderText('Enter search term')
        self.input_box.textChanged[str].connect(self.onChanged)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Up, Qt.Key_Down):
            self.display.keyPressEvent(event)
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            self.input_box.keyPressEvent(event)

    def onChanged(self, term):
        if term == '':
            search_results = self.cards
        else:
            search_results = [card for card in self.cards if term.lower() in card.lower()]

        self.display.setPlainText('\n'.join(search_results))
