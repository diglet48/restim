# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'focstimflashdialog.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QGridLayout,
    QGroupBox, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QTextBrowser, QToolButton, QVBoxLayout,
    QWidget)

class Ui_FocStimFlashDialog(object):
    def setupUi(self, FocStimFlashDialog):
        if not FocStimFlashDialog.objectName():
            FocStimFlashDialog.setObjectName(u"FocStimFlashDialog")
        FocStimFlashDialog.resize(522, 395)
        self.verticalLayout = QVBoxLayout(FocStimFlashDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(FocStimFlashDialog)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.focstim_port = QComboBox(self.groupBox)
        self.focstim_port.setObjectName(u"focstim_port")

        self.gridLayout.addWidget(self.focstim_port, 0, 1, 1, 1)

        self.firmware_path = QLineEdit(self.groupBox)
        self.firmware_path.setObjectName(u"firmware_path")

        self.gridLayout.addWidget(self.firmware_path, 1, 1, 1, 1)

        self.refresh = QToolButton(self.groupBox)
        self.refresh.setObjectName(u"refresh")

        self.gridLayout.addWidget(self.refresh, 0, 2, 1, 1)

        self.open = QToolButton(self.groupBox)
        self.open.setObjectName(u"open")

        self.gridLayout.addWidget(self.open, 1, 2, 1, 1)


        self.verticalLayout.addWidget(self.groupBox)

        self.label_3 = QLabel(FocStimFlashDialog)
        self.label_3.setObjectName(u"label_3")

        self.verticalLayout.addWidget(self.label_3)

        self.pushButton = QPushButton(FocStimFlashDialog)
        self.pushButton.setObjectName(u"pushButton")

        self.verticalLayout.addWidget(self.pushButton)

        self.textBrowser = QTextBrowser(FocStimFlashDialog)
        self.textBrowser.setObjectName(u"textBrowser")

        self.verticalLayout.addWidget(self.textBrowser)


        self.retranslateUi(FocStimFlashDialog)

        QMetaObject.connectSlotsByName(FocStimFlashDialog)
    # setupUi

    def retranslateUi(self, FocStimFlashDialog):
        FocStimFlashDialog.setWindowTitle(QCoreApplication.translate("FocStimFlashDialog", u"FOC-Stim firmware flasher", None))
        self.groupBox.setTitle(QCoreApplication.translate("FocStimFlashDialog", u"Settings", None))
        self.label.setText(QCoreApplication.translate("FocStimFlashDialog", u"Serial port", None))
        self.label_2.setText(QCoreApplication.translate("FocStimFlashDialog", u"Firmware", None))
        self.refresh.setText(QCoreApplication.translate("FocStimFlashDialog", u"Refresh", None))
        self.open.setText(QCoreApplication.translate("FocStimFlashDialog", u"Open...", None))
        self.label_3.setText(QCoreApplication.translate("FocStimFlashDialog", u"Only for FOC-Stim V4", None))
        self.pushButton.setText(QCoreApplication.translate("FocStimFlashDialog", u"Firmware update", None))
    # retranslateUi

