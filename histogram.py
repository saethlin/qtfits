import numpy as np
from PyQt5.QtWidgets import QLabel, QDesktopWidget, QSizePolicy
from PyQt5.QtGui import QImage, QPixmap, QPainter
from PyQt5.QtCore import Qt, QTimer

from resources import zoom


class ImageHistogram(QLabel):

    HEIGHT = 50

    def __init__(self):
        super(ImageHistogram, self).__init__()
        self.main = None
        self._image = None
        self.plot = None
        self.clicked = None
        self.painter = QPainter()
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self.setFocusPolicy(Qt.ClickFocus)
        self.setMinimumWidth(200)
        self.setToolTip('Current image histogram')

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
        self.lower_bound, self.upper_bound = np.percentile(data[::100], [0.001, 99.95])
        self.span = self.upper_bound - self.lower_bound
        data = data[(data >= self.lower_bound) & (data <= self.upper_bound)]

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
        self.resizeEvent(None)

    def draw_sliders(self):
        pixmap = QPixmap(self.qimage)
        self.painter.begin(pixmap)
        self.painter.setPen(Qt.red)

        self.black = (self.main.black - self.lower_bound) / self.span * self.width()
        self.white = (self.main.white - self.lower_bound) / self.span * self.width()

        self.painter.drawLine(self.black, 0, self.black, self.height())
        self.painter.drawLine(self.white, 0, self.white, self.height())
        self.painter.end()
        self.setPixmap(pixmap)

    def resizeEvent(self, event):
        if self.timer.remainingTime() == -1:
            self.resizer()
            self.timer.start()

    def resizer(self):
        resized = zoom(self.histogram_image, 1, self.width()/self.histogram_image.shape[1])
        height, width = resized.shape
        self.qimage = QImage(bytes(resized), width, height, width, QImage.Format_Grayscale8)
        self.draw_sliders()

    def mousePressEvent(self, event):
        if abs(event.x() - self.white) < 4:
            self.clicked = 'white'
        elif abs(event.x() - self.black) < 4:
            self.clicked = 'black'

    def mouseReleaseEvent(self, event):
        self.clicked = None

    def mouseMoveEvent(self, event):
        if self.clicked == 'black':
            new_black = (event.x() / self.width() * self.span) + self.lower_bound
            new_black = max(new_black, self.lower_bound)
            if new_black != self.main.black and new_black < self.main.white:
                self.main.black = new_black
                self.draw_sliders()
        elif self.clicked == 'white':
            new_white = (event.x() / self.width() * self.span) + self.lower_bound
            new_white = min(new_white, self.upper_bound - self.span/self.width())
            if new_white != self.main.white and new_white > self.main.black:
                self.main.white = new_white
                self.draw_sliders()
