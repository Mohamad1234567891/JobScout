"""
This file is part of JobScout, an open-source job-search and job-match
engine that scrapes LinkedIn and scores every posting against your profile.

Copyright (c) 2026 Muhammed Bekiroğlu and the JobScout contributors.

Original JobScout repository: https://github.com/Mohamad1234567891/JobScout

Muhammed Bekiroğlu (JobScout team leader and top contributor) YouTube channel:
    https://www.youtube.com/@ALShajaraComputerScienceInstit

Licensed under the Mozilla Public License 2.0 with Additional Attribution
Terms — see the LICENSE file.
-------------------------------------------------------------------------------------------------------------------------------

Small spinning loader shown while a search runs.
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QPen


class SmallLoader(QWidget):
    """Spinning arc that rotates at roughly 60 FPS while visible."""

    def __init__(self, size=28, parent=None):
        super().__init__(parent)
        self.size_val = size
        self.setFixedSize(size, size)
        self.angle = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._rotate)

        self.hide()  # starts hidden by default

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
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        pen = QPen()
        pen.setWidth(3)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)

        # Subtle background track
        pen.setColor(QColor(255, 255, 255, 40))
        painter.setPen(pen)
        margin = 3
        draw_size = self.size_val - (margin * 2)
        painter.drawEllipse(margin, margin, draw_size, draw_size)

        # Animated spinning arc (light blue / accent)
        pen.setColor(QColor("#38bdf8"))
        painter.setPen(pen)
        painter.drawArc(margin, margin, draw_size, draw_size, -self.angle * 16, 90 * 16)
