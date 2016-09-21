import numpy as np
try:
    from PyQt5.QtWidgets import QLabel, QDesktopWidget, QSizePolicy
    from PyQt5.QtGui import QImage, QPixmap, QPainter
    from PyQt5.QtCore import Qt, QTimer
except ImportError:
    from PyQt4.QtGui import QLabel, QDesktopWidget, QSizePolicy, QImage, QPixmap, QPainter
    from PyQt4.QtCore import Qt, QTimer

from resources import zoom


class ImageHistogram(QLabel):

    HEIGHT = 50

    def __init__(self):
        super(ImageHistogram, self).__init__()
        self.main = None
        self._image = None
        self.histogram_image = None
        self.lookup = None
        self.clicked = None
        self.black = None
        self.white = None
        self.qimage = None
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

        histogram = np.bincount(new.ravel().astype(int))[:-1]
        mask = histogram != 0
        self.lookup = np.arange(new.max())[mask]
        histogram = histogram[mask]

        histogram = histogram / histogram.max() * ImageHistogram.HEIGHT

        histogram.shape = 1, -1
        histogram = zoom(histogram, 1, screen_width/histogram.size)
        self.lookup = zoom(self.lookup[np.newaxis, :], 1, screen_width/self.lookup.size)[0]

        # Manual plotting
        coords = np.arange(0, ImageHistogram.HEIGHT)[::-1]
        coords = np.repeat(coords[:, np.newaxis], screen_width, axis=1)
        histogram = coords > histogram

        self.histogram_image = (histogram * 255).astype(np.uint8)
        self.resizeEvent(None)

    def draw_sliders(self):
        pixmap = QPixmap(self.qimage)
        self.painter.begin(pixmap)
        self.painter.setPen(Qt.red)

        # Find me the index where lookup table is closest to white and black levels
        self.black = np.abs(self.lookup - self.main.black).argmin() * self.width()/self.lookup.size
        self.white = np.abs(self.lookup - self.main.white).argmin() * self.width()/self.lookup.size

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
        lookup_position = int(round(event.x()/self.width()*self.lookup.size))

        if 0 < lookup_position < self.lookup.size:
            if self.clicked == 'black':
                new_black = self.lookup[lookup_position]
                if new_black != self.main.black and new_black < self.main.white:
                    self.main.black = new_black
                    self.draw_sliders()
            elif self.clicked == 'white':
                new_white = self.lookup[lookup_position]
                if new_white != self.main.white and new_white > self.main.black:
                    self.main.white = new_white
                    self.draw_sliders()
