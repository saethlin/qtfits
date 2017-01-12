# TODO: Loading message and I/O in threads
# TODO: Fast initial render when reclipping or zooming in
# TODO: Draw line across image and plot pixels it collides with
# TODO: Select a region and show statistics
import argparse
import numpy as np
from astropy.io import fits
try:
    from PyQt5.QtWidgets import QWidget, QGridLayout, QApplication, QFileDialog, QVBoxLayout
    from PyQt5.QtCore import Qt
except ImportError:
    from PyQt4.QtGui import QWidget, QGridLayout, QApplication, QFileDialog, QVBoxLayout
    from PyQt4.QtCore import Qt

from dirlist import DirList
from histogram import ImageHistogram
from imagedisplay import ImageDisplay
from minimap import MiniMap
from headerdisplay import HeaderDisplay
from cursordisplay import CursorDisplay
from menubar import MenuBar


class QtFits(QApplication):

    def __init__(self, filename=None):
        super().__init__([])
        self.header = None
        self.setStyle('Fusion')
        self.setApplicationName('QtFits')

        self.overlord = QWidget()
        self.overlord.resize(800, 500)

        overlord_layout = QVBoxLayout()
        self.overlord.setLayout(overlord_layout)
        overlord_layout.setContentsMargins(0, 0, 0, 0)
        overlord_layout.setSpacing(0)

        self.window = QWidget()
        self.window.resizeEvent = self.resizeEvent
        self.window.keyPressEvent = self.keyPressEvent

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        self.window.setLayout(grid)

        self.minimap = MiniMap()
        grid.addWidget(self.minimap, 0, 1, 1, 1)

        self.main = ImageDisplay()
        grid.addWidget(self.main, 0, 0, 3, 1)

        self.cursordisplay = CursorDisplay()
        grid.addWidget(self.cursordisplay, 1, 1, 1, 1)

        self.box = DirList()
        grid.addWidget(self.box, 2, 1, 2, 1)

        self.histogram = ImageHistogram()
        grid.addWidget(self.histogram, 3, 0, 1, 1)

        self.menubar = MenuBar(self)
        overlord_layout.addWidget(self.menubar)
        overlord_layout.addWidget(self.window)

        self.box.main = self.main
        self.box.list.app = self

        self.main.histogram = self.histogram
        self.histogram.main = self.main

        self.minimap.main = self.main
        self.main.minimap = self.minimap

        self.main.cursordisplay = self.cursordisplay

        self.handlers = {
            Qt.Key_Escape: self.overlord.close,
            Qt.Key_Equal: self.main.increase_zoom,
            Qt.Key_Minus: self.main.decrease_zoom,
            Qt.Key_Down: self.box.list.selection_down,
            Qt.Key_Up: self.box.list.selection_up,
            Qt.Key_Return: self.box.list.select,
            Qt.Key_Right: self.box.list.select,
            Qt.Key_Backspace: self.box.list.back,
            Qt.Key_Left: self.box.list.back,
        }

        self.window.setFocusPolicy(Qt.ClickFocus)

        if filename is not None:
            self.open(filename)

        self.overlord.show()
        self.exec_()

    def open(self, path, hdu=None):
        with open(path, 'rb') as input_file:
            self.hdulist = fits.open(input_file)
            if hdu is None:
                hdu = 0
                while self.hdulist[hdu].data is None:
                    hdu += 1
        self.set_hdu(hdu)

    def set_hdu(self, hdu):
        image = self.hdulist[hdu].data.astype(np.float32)
        self.main.image = image
        self.header = repr(self.hdulist[hdu].header)
        self.menubar.set_hdulist(self.hdulist)

    def open_dialog(self):
        filename = QFileDialog.getOpenFileName(self.main, 'Open file', '.')
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
        self.main._refresh_queue.append(self.main.reslice)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Display a fits file')
    parser.add_argument('filename', help='path to or name of file to open')
    args = parser.parse_args()
    QtFits(args.filename)
