"""
TODO:
Histogram sliders
Header display
Toolbar?
"""

import os
import numpy as np
from astropy.io import fits
from PyQt5.QtWidgets import QWidget, QGridLayout, QApplication
from PyQt5.QtCore import Qt

from dirlist import DirList
from histogram import ImageHistogram
from imagedisplay import ImageDisplay
from minimap import MiniMap


class QtFits(QWidget):

    def __init__(self):
        super(QtFits, self).__init__()

        self.setWindowTitle('QtFits')
        self.resize(800, 500)

        grid = QGridLayout()
        self.setLayout(grid)

        self.mini = MiniMap()
        grid.addWidget(self.mini, 0, 1)

        self.main = ImageDisplay(self.mini)
        grid.addWidget(self.main, 0, 0, 0, 1)

        self.box = DirList(self, os.getcwd())
        grid.addWidget(self.box, 1, 1, 2, 1)

        self.histogram = ImageHistogram()
        grid.addWidget(self.histogram, 2, 0)

        self.handlers = dict()
        self.handlers[Qt.Key_Escape] = self.close
        self.handlers[Qt.Key_Equal] = self.main.increase_zoom
        self.handlers[Qt.Key_Minus] = self.main.decrease_zoom
        self.handlers[Qt.Key_Down] = self.box.selection_down
        self.handlers[Qt.Key_Up] = self.box.selection_up
        self.handlers[Qt.Key_Return] = self.box.select
        self.handlers[Qt.Key_Right] = self.box.select
        self.handlers[Qt.Key_Backspace] = self.box.back
        self.handlers[Qt.Key_Left] = self.box.back

        self.open('test.fits')

    def open(self, path, hdu=0):
        with open(path, 'rb') as input_file:
            image = fits.open(input_file)[hdu].data.astype(np.float32)
        self.main.image = image
        self.histogram.image = image

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
