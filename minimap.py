import numpy as np
from PyQt5.QtWidgets import QLabel, QSizePolicy
from PyQt5.QtGui import QImage, QPixmap

from resources import zoom


class MiniMap(QLabel):

    SIZE = 200

    def __init__(self):
        super(MiniMap, self).__init__()
        self.conversion = None
        self._image = None
        self.scaled = None
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
        self.scaled = (clipped / clipped.max() * 255).astype(np.uint8)

    def refresh(self, y, x, height, width, zoom):
        stack = np.dstack((self.scaled,) * 3)
        scale = self.conversion / zoom

        top = scale * y
        bot = scale * (y + height)
        if bot > MiniMap.SIZE:
            bot = MiniMap.SIZE
        left = scale * x
        right = scale * (x + width)
        if right > MiniMap.SIZE:
            right = MiniMap.SIZE

        top = round(int(top))
        bot = round(int(bot))
        left = round(int(left))
        right = round(int(right))

        stack[top, left:right, 1] = 255
        stack[bot - 1, left:right, 1] = 255
        stack[top:bot, left, 1] = 255
        stack[top:bot, right - 1, 1] = 255

        height, width, channels = stack.shape
        image = QImage(bytes(stack.data), width, height, 3 * width, QImage.Format_RGB888)
        self.setPixmap(QPixmap(image))
