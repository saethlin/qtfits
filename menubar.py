from PyQt5.QtWidgets import QMenuBar, QSizePolicy


class MenuBar(QMenuBar):

    def __init__(self, master):
        super().__init__()
        self.setMinimumSize(1, 10)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)

        file_menu = self.addMenu('File')
        file_menu.addAction('open', master.open_dialog)

        self.addMenu('HDUs')

        self.addMenu('Header')

