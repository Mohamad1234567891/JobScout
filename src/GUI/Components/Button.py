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

Styled pill button that opens the given URL in the default browser.
"""

from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QCursor


class Button(QPushButton):
    def __init__(self, text, url_string, parent=None):
        super().__init__(text, parent)
        self.url_string = url_string
        self.clicked.connect(self.on_clicked)

        self.setFixedSize(110, 34)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setStyleSheet("""
            QPushButton {
                background-color: #1f3a52;
                color: #ffffff;
                font-size: 13px;
                font-weight: 600;
                border-radius: 17px;
                border: none;
                padding: 4px 10px;
            }
            QPushButton:hover {
                background-color: #2b4f70;
            }
            QPushButton:pressed {
                background-color: #142738;
            }
        """)

    def on_clicked(self):
        if self.url_string:
            QDesktopServices.openUrl(QUrl(self.url_string))
