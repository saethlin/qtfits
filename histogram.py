import numpy as np
from PyQt5.QtWidgets import QLabel, QDesktopWidget, QSizePolicy
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer

from resources import zoom


class ImageHistogram(QLabel):

    HEIGHT = 50

    def __init__(self):
        super(ImageHistogram, self).__init__()
        self._image = None
        self.plot = None
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)

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
        lower_bound, upper_bound = np.percentile(data[::100], [0.01, 99.95])
        data = data[(data > lower_bound) & (data < upper_bound)]

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
            image = QImage(bytes(resized), width, height, width, QImage.Format_Grayscale8)
            pixmap = QPixmap(image)
            self.setPixmap(pixmap)
            self._refresh_queue = False

    def resizeEvent(self, event):
        self._refresh_queue = True
        if self.timer.remainingTime() == -1:
            self.resizer()
            self.timer.start()
