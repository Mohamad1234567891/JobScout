"""
This file is part of ShopWise, an open-source multi-region, multi-store
price-comparison and product-search engine.

Copyright (c) 2026 Muhammed Bekiroğlu and the ShopWise contributors.

Original ShopWise repository: https://github.com/Mohamad1234567891/ShopWise

Muhammed Bekiroğlu (ShopWise team leader and top contributor) YouTube channel:
    https://www.youtube.com/@ALShajaraComputerScienceInstit

Licensed under the Mozilla Public License 2.0 with Additional Attribution
Terms — see the LICENSE file.
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QPen


class SmallLoader(QWidget):
    """Small spinning loader shown while a search runs; starts hidden and rotates at roughly 60 FPS while visible."""
    def __init__(self, size: int = 28, parent=None):
        super().__init__(parent)
        self.size_val = size
        self.setFixedSize(size, size)
        self.angle = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._rotate)

        # Starts hidden by default
        self.hide()

    def start(self):
        self.angle = 0
        self.show()
        self.timer.start(16)  # ~60 FPS

    def close_loading(self):
        """Stops rotation and hides the loader."""
        self.timer.stop()
        self.hide()

    def stop(self):
        """Alias for close_loading."""
        self.close_loading()

    def _rotate(self):
        self.angle = (self.angle + 8) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen()
        pen.setWidth(3)
        pen.setCapStyle(Qt.RoundCap)

        # Subtle background track
        pen.setColor(QColor(255, 255, 255, 40))
        painter.setPen(pen)
        margin = 3
        draw_size = self.size_val - (margin * 2)
        painter.drawEllipse(margin, margin, draw_size, draw_size)

        # Animated spinning arc (Light blue / Accent)
        pen.setColor(QColor("#38bdf8"))
        painter.setPen(pen)
        painter.drawArc(margin, margin, draw_size, draw_size, -self.angle * 16, 90 * 16)