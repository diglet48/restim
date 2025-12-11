# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'aboutdialog.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QLabel, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        if not AboutDialog.objectName():
            AboutDialog.setObjectName(u"AboutDialog")
        AboutDialog.resize(352, 160)
        self.verticalLayout = QVBoxLayout(AboutDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(AboutDialog)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)


        self.retranslateUi(AboutDialog)

        QMetaObject.connectSlotsByName(AboutDialog)
    # setupUi

    def retranslateUi(self, AboutDialog):
        AboutDialog.setWindowTitle(QCoreApplication.translate("AboutDialog", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("AboutDialog", u"<html><head/><body><p><span style=\" font-size:18pt; font-weight:700;\">Restim</span></p><p>version: &lt;insert version here&gt;</p><p>homepage: <a href=\"https://github.com/diglet48/restim\"><span style=\" text-decoration: underline; color:#334327;\">https://github.com/diglet48/restim</span></a></p></body></html>", None))
    # retranslateUi

