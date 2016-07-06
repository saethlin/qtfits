import numpy as np
from PyQt5.QtWidgets import QLabel, QSizePolicy
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer

from resources import zoom


class ImageDisplay(QLabel):

    CLIP = 3
    ZOOM = 2
    SLICE = 1

    def __init__(self, minimap):
        super(ImageDisplay, self).__init__()
        self.minimap = minimap

        self._refresh_queue = 0
        self._image = None
        self._black = None
        self._white = None
        self.zoom = 1

        self.timer = QTimer(self)
        self.timer.setInterval(int(1/60*1000))
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.refresh_display)

        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, new):
        self._image = new
        self._black = np.median(new)
        self._white = np.percentile(self._image, 99.7)
        self.view_y = 0
        self.view_x = 0
        self.minimap.image = new
        self.refresh_display(ImageDisplay.CLIP)

    @property
    def black(self):
        return self._black

    @black.setter
    def black(self, new):
        self._black = new
        self.refresh_display(ImageDisplay.CLIP)

    @property
    def white(self):
        return self._white

    @white.setter
    def white(self, new):
        self._white = new
        self.refresh_display(ImageDisplay.CLIP)

    def increase_zoom(self):
        if self.zoom < 4:
            self.zoom *= 2
            self.refresh_display(ImageDisplay.ZOOM)

    def decrease_zoom(self):
        if self.zoom > 0.125:
            self.zoom /= 2
            if self.view_y + self.height() > self.image.shape[0] * self.zoom:
                self.view_y = self.image.shape[0] * self.zoom - self.height()
            if self.view_x + self.width() > self.image.shape[1] * self.zoom:
                self.view_x = self.image.shape[1] * self.zoom - self.width()

            if self.view_x < 0:
                self.view_x = 0
            if self.view_y < 0:
                self.view_y = 0

            self.refresh_display(ImageDisplay.ZOOM)

    def refresh_display(self, stage=-1):
        if self.timer.remainingTime() == -1:

            stage = max(stage, self._refresh_queue)

            if stage == -1:
                return

            if stage >= ImageDisplay.CLIP:
                clipped = (self.image - self.black).clip(0, self.white-self.black)
                self.scaled = (clipped/clipped.max()*255).astype(np.uint8)
                self.minimap.reclip(self.black, self.white)
            if stage >= ImageDisplay.ZOOM:
                if self.zoom >= 1:
                    self.zoomed = zoom(self.scaled, self.zoom)
                else:
                    self.zoomed = zoom(self.scaled, self.zoom)
            if stage >= ImageDisplay.SLICE:
                self.sliced = self.zoomed[self.view_y:self.height()+self.view_y, self.view_x:self.width()+self.view_x]

            height, width = self.sliced.shape
            image = QImage(bytes(self.sliced.data), width, height, width, QImage.Format_Grayscale8)
            pixmap = QPixmap(image)
            self.setPixmap(pixmap)

            self.minimap.refresh(self.view_y, self.view_x, self.height(), self.width(), self.zoom)

            self._refresh_queue = -1
            self.timer.start()

        else:
            self._refresh_queue = max(self._refresh_queue, stage)

    def mousePressEvent(self, event):
        self.last_x = event.x()
        self.last_y = event.y()

    def mouseMoveEvent(self, event):
        last_ypos = self.view_y
        last_xpos = self.view_x
        self.view_y += (self.last_y-event.y())
        self.view_x += (self.last_x-event.x())
        self.last_y = event.y()
        self.last_x = event.x()

        if self.view_y + self.height() > self.image.shape[0]*self.zoom:
            self.view_y = self.image.shape[0]*self.zoom - self.height()
        if self.image.shape[1]*self.zoom - self.view_x < self.width():
            self.view_x = self.image.shape[1]*self.zoom - self.width()

        if self.view_y < 0:
            self.view_y = 0
        if self.view_x < 0:
            self.view_x = 0

        moved = (last_ypos != self.view_y) or (last_xpos != self.view_x)
        if moved:
            self.refresh_display(ImageDisplay.SLICE)
