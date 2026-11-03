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

Converts an emoji into an icon for use in windows and for any use case.
"""

from PySide6.QtGui import QIcon, QPixmap, QPainter, QFont
from PySide6.QtCore import Qt, QRect


def emoji_icon(emoji, sizes=(16, 24, 32, 48, 64, 128, 256)):
    """Draws an emoji onto transparent images and returns them as a QIcon.

    Must be called after the QApplication has been created.
    """
    icon = QIcon()
    for size in sizes:
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)
        font = QFont()
        font.setFamilies(["Noto Color Emoji", "Segoe UI Emoji", "Apple Color Emoji", "Twemoji Mozilla"])
        font.setPixelSize(int(size * 0.8))
        painter.setFont(font)
        painter.drawText(QRect(0, 0, size, size), Qt.AlignmentFlag.AlignCenter, emoji)
        painter.end()

        icon.addPixmap(pixmap)
    return icon
