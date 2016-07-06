from PyQt5.QtWidgets import QPlainTextEdit, QDialog, QVBoxLayout
from PyQt5.QtGui import QFont


class HeaderDisplay(QDialog):

    def __init__(self, header):
        super().__init__()
        self.display = QPlainTextEdit(header)
        self.display.setReadOnly(True)
        self.display.setFont(QFont("Courier New"))
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.display)
        self.setMinimumWidth(750)
        self.resize(750, 500)
