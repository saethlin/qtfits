import numpy as np
try:
    from PyQt5.QtWidgets import QLabel, QSizePolicy
    from PyQt5.QtGui import QImage, QPixmap
    from PyQt5.QtCore import Qt, QTimer
    GRAYSCALE = QImage.Format_Grayscale8
except ImportError:
    from PyQt4.QtGui import QLabel, QSizePolicy, QImage, QPixmap
    from PyQt4.QtCore import Qt, QTimer
    GRAYSCALE = QImage.Format_Indexed8

from resources import zoom


class ImageDisplay(QLabel):

    def __init__(self):
        super(ImageDisplay, self).__init__()
        self.minimap = None
        self._image = None
        self._black = None
        self._white = None
        self.slices = None, None
        self._refresh_queue = []
        self.zoom = 1
        self._view_x = self._view_y = 0
        self.scaled = self.zoomed = self.sliced = None
        self.last_y = self.last_x = None

        self.timer = QTimer(self)
        self.timer.setInterval(int(1/60*1000))
        self.timer.setSingleShot(False)
        self.timer.timeout.connect(self.refresh_display)
        self.timer.start()

        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setMouseTracking(True)
        self.setToolTip('Current image display')

        self._image = np.zeros((800, 500))

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, new):
        self._image = new
        self.black, self.white = np.percentile(self._image, [50, 99.7])
        self.view_y = self.image.shape[0]//2
        self.view_x = self.image.shape[1]//2
        self.zoom = 1
        self.minimap.image = new
        self.histogram.image = new
        self.zoomed = self._image

    @property
    def black(self):
        return self._black

    @black.setter
    def black(self, new):
        self._black = new
        self._refresh_queue.append(self.reclip)

    @property
    def white(self):
        return self._white

    @white.setter
    def white(self, new):
        self._white = new
        self._refresh_queue.append(self.reclip)

    @property
    def view_y(self):
        return self._view_y

    @view_y.setter
    def view_y(self, new):
        new = max(self.height()/2, new)
        new = min(new, self.zoom*self.image.shape[0] - self.height()/2)
        if new != self._view_y:
            self._view_y = int(round(new))
            self._refresh_queue.append(self.reslice)

    @property
    def view_x(self):
        return self._view_x

    @view_x.setter
    def view_x(self, new):
        new = max(self.width()/2, new)
        new = min(new, self.zoom*self.image.shape[1]-self.width()/2)
        if new != self._view_x:
            self._view_x = int(round(new))
            self._refresh_queue.append(self.reslice)

    def increase_zoom(self):
        if self.zoom < 8:
            self.zoom *= 2
            self.view_x *= 2
            self.view_y *= 2
            self._refresh_queue.append(self.rezoom)

    def decrease_zoom(self):
        if self.zoom > 0.125:
            self.zoom /= 2
            self.view_x /= 2
            self.view_y /= 2
            self._refresh_queue.append(self.rezoom)

    def reclip(self):
        clipped = (self.image - self.black).clip(0, self.white - self.black)
        self.scaled = (clipped / clipped.max() * 255).astype(np.uint8)
        self.minimap.reclip(self.black, self.white)

        self.rezoom()

    def rezoom(self):
        # If no clipping was done, it's much faster to resample the previous self.zoom
        zoom_change = self.zoom * self.image.shape[0] / self.zoomed.shape[0]

        if zoom_change < 1:
            self.zoomed = zoom(self.zoomed, zoom_change)
        else:
            self.zoomed = zoom(self.scaled, self.zoom)

        self.reslice()

    def reslice(self):
        slice_y = slice(max(0, self.view_y - self.height() // 2),
                        min(int(round(self.image.shape[0] * self.zoom)), self.view_y + self.height() // 2))
        slice_x = slice(max(0, self.view_x - self.width() // 2),
                        min(int(round(self.image.shape[1] * self.zoom)), self.view_x + self.width() // 2))
        self.slices = slice_y, slice_x
        self.sliced = self.zoomed[slice_y, slice_x]

        height, width = self.sliced.shape
        image = QImage(bytes(self.sliced.data), width, height, width, GRAYSCALE)
        self.setPixmap(QPixmap(image))

        self.minimap.refresh()

    def refresh_display(self):
        if self._refresh_queue:
            entry_points = [self.reclip, self.rezoom, self.reslice] # I think this should be a constant somewhere
            entry_point = min(self._refresh_queue, key=entry_points.index)
            entry_point()
            self._refresh_queue = []

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.last_x = event.x()
            self.last_y = event.y()

    def mouseMoveEvent(self, event):
        cursor_y = (self.view_y - self.height()//2 + event.y()) / self.zoom
        cursor_x = (self.view_x - self.width()//2 + event.x()) / self.zoom
        cursor_y = int(cursor_y)
        cursor_x = int(cursor_x)

        if (0 <= cursor_y < self.image.shape[0]) and (0 <= cursor_x < self.image.shape[1]):
            self.cursordisplay.set(x=cursor_x, y=cursor_y, value=self.image[cursor_y, cursor_x])

        if event.buttons() == Qt.LeftButton:
            last_ypos = self.view_y
            last_xpos = self.view_x
            self.view_y += (self.last_y-event.y())
            self.view_x += (self.last_x-event.x())
            self.last_y = event.y()
            self.last_x = event.x()

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self.increase_zoom()
        elif event.angleDelta().y() < 0:
            self.decrease_zoom()
