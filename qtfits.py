# TODO: Cursor position and value display
# TODO: View change by clicking on minimap
# TODO: Histogram sliders
# TODO: Header display
# TODO: Toolbar?

import sys
import re
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

        self.mini = MiniMap()
        grid.addWidget(self.mini, 0, 1)

        self.main = ImageDisplay(self.mini)
        grid.addWidget(self.main, 0, 0, 2, 1)

        self.box = DirList(self)
        grid.addWidget(self.box, 1, 1, 2, 1)

        self.histogram = ImageHistogram(self.main)
        grid.addWidget(self.histogram, 2, 0)

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

        self.open(sys.argv[1])

    def open(self, path, hdu=None):
        with open(path, 'rb') as input_file:
            hdulist = fits.open(input_file)
            if hdu is None:
                hdu = 0
                while hdulist[hdu].data is None:
                    hdu += 1
            image = hdulist[hdu].data.astype(np.float32)
        self.main.image = image
        self.histogram.image = image
        header_text = str(hdulist[hdu].header).strip()
        self.header = re.sub("(.{80})", "\\1\n", header_text, 0, re.DOTALL).strip()

    def open_dialog(self):
        if QApplication.keyboardModifiers() == Qt.ControlModifier:
            fname = QFileDialog.getOpenFileName(self, 'Open file', '.')
            if fname[0]:
                self.open(fname[0])

    def show_header(self):
        header_window = HeaderDisplay(self.header)
        header_window.exec_()

    def keyPressEvent(self, event):
        if event.key() in self.handlers:
            handler = self.handlers[event.key()]
            handler()

    def resizeEvent(self, event):
        self.main.refresh_display(ImageDisplay.SLICE)


if __name__ == '__main__':
    app = QApplication([])
    app.setStyle('Fusion')
    window = QtFits()
    window.show()
    app.exec_()
