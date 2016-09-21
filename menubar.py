from functools import partial
try:
    from PyQt5.QtWidgets import QMenuBar, QSizePolicy
    from PyQt5.QtGui import QFont
except ImportError:
    from PyQt4.QtGui import QMenuBar, QSizePolicy, QFont


class MenuBar(QMenuBar):

    def __init__(self, master):
        super().__init__()
        self.master = master
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self.setFont(QFont('System', 10))

        file_menu = self.addMenu('File')
        file_menu.addAction('Open...', master.open_dialog, 'ctrl+o')

        self.hdu_menu = self.addMenu('HDUs')

        header_menu = self.addMenu('Header')
        header_menu.addAction('Show header', master.show_header, 'ctrl+h')

    def set_hdulist(self, hdulist):
        self.hdu_menu.clear()

        hdulist_info = hdulist.info(output=False)
        hdulist_info = [[str(entry[0]) + ' ' + entry[1], len(entry[4]) == 2] for entry in hdulist_info]

        for index, entry in enumerate(hdulist_info):
            new_action = self.hdu_menu.addAction(entry[0], partial(self.master.set_hdu, hdu=index))
            new_action.setEnabled(entry[1])
