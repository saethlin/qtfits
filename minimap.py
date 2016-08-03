import numpy as np
from PyQt5.QtWidgets import QLabel, QSizePolicy
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPolygon
from PyQt5.QtCore import Qt, QPoint

from imagedisplay import ImageDisplay
from resources import zoom


class MiniMap(QLabel):

    SIZE = 200

    def __init__(self):
        super(MiniMap, self).__init__()
        self.main = None
        self.conversion = None
        self._image = None
        self.scaled = None
        self.painter = QPainter()
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, new):
        self.conversion = MiniMap.SIZE/max(new.shape)
        self._image = zoom(new, self.conversion)

    def reclip(self, black, white):
        clipped = (self.image - black).clip(0, white - black)
        scaled = (clipped / clipped.max() * 255).astype(np.uint8)
        height, width = scaled.shape
        self.qimage = QImage(bytes(scaled.data), width, height, width, QImage.Format_Grayscale8)

    def refresh(self):
        pixmap = QPixmap(self.qimage)
        self.painter.begin(pixmap)
        self.painter.setBrush(Qt.red)
        self.painter.setPen(Qt.red)

        scale = self.conversion / self.main.zoom

        top = scale * (self.main.view_y - self.main.height()/2)
        bot = scale * (self.main.view_y + self.main.height()/2)
        left = scale * (self.main.view_x - self.main.width()/2)
        right = scale * (self.main.view_x + self.main.width()/2)

        top = int(round(top))
        bot = int(round(bot))-1
        left = int(round(left))
        right = int(round(right))-1

        self.painter.drawLine(left, top, right, top)
        self.painter.drawLine(right, top, right, bot)
        self.painter.drawLine(right, bot, left, bot)
        self.painter.drawLine(left, bot, left, top)

        self.setPixmap(pixmap)
        self.painter.end()

    def mousePressEvent(self, event):
        self.main.view_x = event.x()/self.conversion*self.main.zoom
        self.main.view_y = event.y()/self.conversion*self.main.zoom
        self.main.refresh_display(ImageDisplay.CLIP)

    def mouseMoveEvent(self, event):
        self.mousePressEvent(event)

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.main.increase_zoom()
        elif event.angleDelta().y() < 0:
            self.main.decrease_zoom()
