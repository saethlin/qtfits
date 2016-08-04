from functools import partial
from PyQt5.QtWidgets import QMenuBar, QSizePolicy


class MenuBar(QMenuBar):

    def __init__(self, master):
        super().__init__()
        self.master = master
        self.setMinimumSize(1, 10)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)

        file_menu = self.addMenu('File')
        file_menu.addAction('open', master.open_dialog, 'ctrl+o')

        self.hdu_menu = self.addMenu('HDUs')

        header_menu = self.addMenu('Header')
        header_menu.addAction('show header', master.show_header, 'ctrl+h')

        self.setStyleSheet("QToolButton:hover {background-color:green} QToolButton:!hover { background-color: lightgray }")

    def set_hdulist(self, hdulist):
        self.hdu_menu.clear()

        hdulist_info = hdulist.info(output=False)
        hdulist_info = [[str(entry[0]) + ' ' + entry[1], len(entry[4]) == 2] for entry in hdulist_info]

        for e, entry in enumerate(hdulist_info):
            new_action = self.hdu_menu.addAction(entry[0], partial(self.master.set_hdu, hdu=e))
            new_action.setEnabled(entry[1])
