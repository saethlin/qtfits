# TODO: Cursor position and value display
# TODO: Look into plotting a histogram of arcsinh rescaled values
# TODO: Toolbar?

import argparse
import numpy as np
from astropy.io import fits
from PyQt5.QtWidgets import QWidget, QGridLayout, QApplication, QFileDialog
from PyQt5.QtCore import Qt

from dirlist import DirList
from histogram import ImageHistogram
from imagedisplay import ImageDisplay
from minimap import MiniMap
from headerdisplay import HeaderDisplay


class QtFits(QWidget):

    def __init__(self):
        super(QtFits, self).__init__()

        self.header = None
        self.setWindowTitle('QtFits')
        self.resize(800, 500)

        grid = QGridLayout()
        self.setLayout(grid)

        self.minimap = MiniMap()
        grid.addWidget(self.minimap, 0, 1)

        self.main = ImageDisplay()
        grid.addWidget(self.main, 0, 0, 2, 1)

        self.box = DirList(self)
        grid.addWidget(self.box, 1, 1, 2, 1)

        self.histogram = ImageHistogram()
        grid.addWidget(self.histogram, 2, 0)

        self.main.histogram = self.histogram
        self.histogram.main = self.main

        self.minimap.main = self.main
        self.main.minimap = self.minimap

        self.handlers = {
            Qt.Key_Escape: self.close,
            Qt.Key_Equal: self.main.increase_zoom,
            Qt.Key_Minus: self.main.decrease_zoom,
            Qt.Key_Down: self.box.selection_down,
            Qt.Key_Up: self.box.selection_up,
            Qt.Key_Return: self.box.select,
            Qt.Key_Right: self.box.select,
            Qt.Key_Backspace: self.box.back,
            Qt.Key_Left: self.box.back,
            Qt.Key_H: self.show_header,
            Qt.Key_O: self.open_dialog
        }

    def open(self, path, hdu=None):
        with open(path, 'rb') as input_file:
            hdulist = fits.open(input_file)
            if hdu is None:
                hdu = 0
                while hdulist[hdu].data is None:
                    hdu += 1
            image = hdulist[hdu].data.astype(np.float32)
        self.main.image = image
        self.header = str(hdulist[hdu].header).strip()

    def open_dialog(self):
        if QApplication.keyboardModifiers() == Qt.ControlModifier:
            filename = QFileDialog.getOpenFileName(self, 'Open file', '.')
            if filename[0]:
                self.open(filename[0])

    def show_header(self):
        header_window = HeaderDisplay(self.header)
        header_window.show()
        header_window.exec_()

    def keyPressEvent(self, event):
        if event.key() in self.handlers:
            self.handlers[event.key()]()

    def resizeEvent(self, event):
        self.main.refresh_display(ImageDisplay.SLICE)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Display a fits file')
    parser.add_argument('filename', help='path to or name of file to open', nargs='?')
    args = parser.parse_args()
    app = QApplication([])
    app.setStyle('Fusion')
    window = QtFits()
    if args.filename is not None:
        window.open(args.filename)
    else:
        window.main.image = np.random.rand(1024, 1024).astype(np.float32)
    window.show()
    app.exec_()
