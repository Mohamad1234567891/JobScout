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

from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton
from PySide6.QtCore import QUrl,Qt
from PySide6.QtGui import QDesktopServices,QCursor

class Button(QPushButton):
    """Styled 'View Offer' button that opens the product URL in the default browser when clicked."""
    def __init__(self, text, urlString):
        QPushButton.__init__(self, text)
        self.urlString = urlString
        self.clicked.connect(self.OnClicked)


        #style using Qt,QCursor
        self.setFixedSize(110, 34)
        self.setCursor(QCursor(Qt.PointingHandCursor))
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


    def OnClicked(self):
        url = QUrl(self.urlString)
        QDesktopServices.openUrl(url)


