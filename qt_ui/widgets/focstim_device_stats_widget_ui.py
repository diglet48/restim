# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'focstimdevicestatswidget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.3
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
from PySide6.QtWidgets import (QApplication, QFrame, QGridLayout, QGroupBox,
    QLabel, QSizePolicy, QVBoxLayout, QWidget)

class Ui_FocStimDeviceStatsWidget(object):
    def setupUi(self, FocStimDeviceStatsWidget):
        if not FocStimDeviceStatsWidget.objectName():
            FocStimDeviceStatsWidget.setObjectName(u"FocStimDeviceStatsWidget")
        FocStimDeviceStatsWidget.resize(221, 212)
        self.verticalLayout = QVBoxLayout(FocStimDeviceStatsWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.groupBox = QGroupBox(FocStimDeviceStatsWidget)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setFlat(False)
        self.verticalLayout_2 = QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.verticalLayout_2.addWidget(self.label)

        self.frame = QFrame(self.groupBox)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.NoFrame)
        self.gridLayout = QGridLayout(self.frame)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.label_4 = QLabel(self.frame)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)

        self.label_transformer = QLabel(self.frame)
        self.label_transformer.setObjectName(u"label_transformer")

        self.gridLayout.addWidget(self.label_transformer, 0, 1, 1, 1)

        self.label_3 = QLabel(self.frame)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)

        self.label_transformer_max = QLabel(self.frame)
        self.label_transformer_max.setObjectName(u"label_transformer_max")

        self.gridLayout.addWidget(self.label_transformer_max, 0, 2, 1, 1)

        self.label_voltage = QLabel(self.frame)
        self.label_voltage.setObjectName(u"label_voltage")

        self.gridLayout.addWidget(self.label_voltage, 2, 1, 1, 1)

        self.label_voltage_max = QLabel(self.frame)
        self.label_voltage_max.setObjectName(u"label_voltage_max")

        self.gridLayout.addWidget(self.label_voltage_max, 2, 2, 1, 1)


        self.verticalLayout_2.addWidget(self.frame)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout_2.addWidget(self.label_2)

        self.frame_2 = QFrame(self.groupBox)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.NoFrame)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.gridLayout_2 = QGridLayout(self.frame_2)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label_a = QLabel(self.frame_2)
        self.label_a.setObjectName(u"label_a")
        self.label_a.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_2.addWidget(self.label_a, 0, 0, 1, 1)

        self.label_c = QLabel(self.frame_2)
        self.label_c.setObjectName(u"label_c")
        self.label_c.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_2.addWidget(self.label_c, 0, 2, 1, 1)

        self.label_b = QLabel(self.frame_2)
        self.label_b.setObjectName(u"label_b")
        self.label_b.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_2.addWidget(self.label_b, 0, 1, 1, 1)

        self.label_d = QLabel(self.frame_2)
        self.label_d.setObjectName(u"label_d")
        self.label_d.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_2.addWidget(self.label_d, 0, 3, 1, 1)

        self.resistance_a = QLabel(self.frame_2)
        self.resistance_a.setObjectName(u"resistance_a")
        self.resistance_a.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_2.addWidget(self.resistance_a, 1, 0, 1, 1)

        self.resistance_b = QLabel(self.frame_2)
        self.resistance_b.setObjectName(u"resistance_b")
        self.resistance_b.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_2.addWidget(self.resistance_b, 1, 1, 1, 1)

        self.resistance_c = QLabel(self.frame_2)
        self.resistance_c.setObjectName(u"resistance_c")
        self.resistance_c.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_2.addWidget(self.resistance_c, 1, 2, 1, 1)

        self.resistance_d = QLabel(self.frame_2)
        self.resistance_d.setObjectName(u"resistance_d")
        self.resistance_d.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_2.addWidget(self.resistance_d, 1, 3, 1, 1)


        self.verticalLayout_2.addWidget(self.frame_2)


        self.verticalLayout.addWidget(self.groupBox)


        self.retranslateUi(FocStimDeviceStatsWidget)

        QMetaObject.connectSlotsByName(FocStimDeviceStatsWidget)
    # setupUi

    def retranslateUi(self, FocStimDeviceStatsWidget):
        FocStimDeviceStatsWidget.setWindowTitle(QCoreApplication.translate("FocStimDeviceStatsWidget", u"Form", None))
        self.groupBox.setTitle(QCoreApplication.translate("FocStimDeviceStatsWidget", u"Device stats", None))
#if QT_CONFIG(tooltip)
        self.label.setToolTip(QCoreApplication.translate("FocStimDeviceStatsWidget", u"<html><head/><body><p>How much of the device capabilities are used. Output power is limited to 100%.</p><p>To reduce transformer usage: use higher carrier frequency.</p><p>To reduce voltage usage: use lower carrier frequency.</p><p>Better electrodes will significantly reduce both.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label.setText(QCoreApplication.translate("FocStimDeviceStatsWidget", u"<html><head/><body><p><span style=\" font-size:12pt;\">Device usage (?)</span></p></body></html>", None))
        self.label_4.setText(QCoreApplication.translate("FocStimDeviceStatsWidget", u"Voltage:", None))
        self.label_transformer.setText(QCoreApplication.translate("FocStimDeviceStatsWidget", u"0%", None))
        self.label_3.setText(QCoreApplication.translate("FocStimDeviceStatsWidget", u"Transformer:", None))
        self.label_transformer_max.setText(QCoreApplication.translate("FocStimDeviceStatsWidget", u"max: 10%", None))
        self.label_voltage.setText(QCoreApplication.translate("FocStimDeviceStatsWidget", u"0%", None))
        self.label_voltage_max.setText(QCoreApplication.translate("FocStimDeviceStatsWidget", u"max: 12%", None))
        self.label_2.setText(QCoreApplication.translate("FocStimDeviceStatsWidget", u"<html><head/><body><p><span style=\" font-size:12pt;\">Skin resistance [Ohm]</span></p></body></html>", None))
        self.label_a.setText(QCoreApplication.translate("FocStimDeviceStatsWidget", u"A", None))
        self.label_c.setText(QCoreApplication.translate("FocStimDeviceStatsWidget", u"C", None))
        self.label_b.setText(QCoreApplication.translate("FocStimDeviceStatsWidget", u"B", None))
        self.label_d.setText(QCoreApplication.translate("FocStimDeviceStatsWidget", u"D", None))
        self.resistance_a.setText(QCoreApplication.translate("FocStimDeviceStatsWidget", u"100", None))
        self.resistance_b.setText(QCoreApplication.translate("FocStimDeviceStatsWidget", u"200", None))
        self.resistance_c.setText(QCoreApplication.translate("FocStimDeviceStatsWidget", u"300", None))
        self.resistance_d.setText(QCoreApplication.translate("FocStimDeviceStatsWidget", u"400", None))
    # retranslateUi

