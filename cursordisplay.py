from PyQt5.QtWidgets import QLabel, QSizePolicy


class CursorDisplay(QLabel):

    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self.set(0, 0, 0)

    def set(self, x, y, value):
        self.setText('Location: {}, {}\nVaue: {}'.format(x, y, value))
