import numpy as np
from PyQt5.QtWidgets import QLabel, QDesktopWidget, QSizePolicy
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPolygon, QBrush
from PyQt5.QtCore import Qt, QTimer, QPoint

from resources import zoom
import time


class ImageHistogram(QLabel):

    HEIGHT = 50

    def __init__(self, parent):
        super(ImageHistogram, self).__init__()
        self.parent = parent
        self._image = None
        self.plot = None
        self.clicked = None
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self.painter = QPainter()

        self._refresh_queue = False
        self.timer = QTimer(self)
        self.timer.setInterval(int(1/60*1000))
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.resizer)

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, new):
        self._image = new
        screen_width = QDesktopWidget().screenGeometry().width()

        data = new.ravel()
        self.lower_bound, self.upper_bound = np.percentile(data[::100], [0.01, 99.95])
        data = data[(data > self.lower_bound) & (data < self.upper_bound)]

        # Rescale data
        data -= data.min()
        data *= screen_width/data.max()

        histogram = np.bincount(data.astype(int))[:-1]

        # Smooth out the histogram
        left = np.roll(histogram, -1)
        right = np.roll(histogram, 1)
        peak_mask = (histogram > left) & (histogram > right) & (left > 0) & (right > 0)
        histogram[peak_mask] = ((left + right) / 2)[peak_mask]

        histogram = histogram / histogram.max() * ImageHistogram.HEIGHT

        # Manual plotting
        coords = np.arange(0, ImageHistogram.HEIGHT)[::-1]
        coords = np.repeat(coords[:, np.newaxis], screen_width, axis=1)
        histogram = coords > histogram[np.newaxis, :]

        self.histogram_image = (histogram * 255).astype(np.uint8)

    def resizer(self):
        if self._refresh_queue:
            resized = zoom(self.histogram_image, 1, self.width()/self.histogram_image.shape[1])
            height, width = resized.shape
            self.qimage = QImage(bytes(resized), width, height, width, QImage.Format_Grayscale8)
            self.draw_sliders()

    def draw_sliders(self):
        pixmap = QPixmap(self.qimage)
        self.painter.begin(pixmap)
        self.painter.setBrush(Qt.red)
        self.painter.setPen(Qt.red)

        self.black = (self.parent.black - self.lower_bound) / (self.upper_bound - self.lower_bound) * self.width()
        self.white = (self.parent.white - self.lower_bound) / (self.upper_bound - self.lower_bound) * self.width()

        #points = [QPoint(self.black-5, self.height()),
        #          QPoint(self.black+5, self.height()),
        #          QPoint(self.black, self.height()-10)]
        #triangle = QPolygon(points)

        #self.painter.drawConvexPolygon(triangle)

        self.painter.drawLine(self.black, 0, self.black, self.height())
        self.painter.drawLine(self.white, 0, self.white, self.height())
        self.painter.end()
        self.setPixmap(pixmap)

    def resizeEvent(self, event):
        self._refresh_queue = True
        if self.timer.remainingTime() == -1:
            self.resizer()
            self.timer.start()

    def mousePressEvent(self, event):
        if abs(event.x() - self.black) < 4:
            self.clicked = 'black'
        elif abs(event.x() - self.white) < 4:
            self.clicked = 'white'

    def mouseReleaseEvent(self, event):
        self.clicked = None

    def mouseMoveEvent(self, event):
        if self.clicked == 'black':
            self.parent.black = (event.x() / self.width() * (self.upper_bound - self.lower_bound)) + self.lower_bound
            self.draw_sliders()
        elif self.clicked == 'white':
            self.parent.white = (event.x() / self.width() * (self.upper_bound - self.lower_bound)) + self.lower_bound
            self.draw_sliders()
