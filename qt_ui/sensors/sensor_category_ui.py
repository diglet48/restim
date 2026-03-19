# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'sensorcategory.ui'
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
from PySide6.QtWidgets import (QApplication, QButtonGroup, QFormLayout, QFrame,
    QLabel, QLineEdit, QRadioButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_SensorCategory(object):
    def setupUi(self, SensorCategory):
        if not SensorCategory.objectName():
            SensorCategory.setObjectName(u"SensorCategory")
        SensorCategory.resize(524, 367)
        self.verticalLayout = QVBoxLayout(SensorCategory)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label = QLabel(SensorCategory)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.frame = QFrame(SensorCategory)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.radio_device = QRadioButton(self.frame)
        self.buttonGroup = QButtonGroup(SensorCategory)
        self.buttonGroup.setObjectName(u"buttonGroup")
        self.buttonGroup.addButton(self.radio_device)
        self.radio_device.setObjectName(u"radio_device")
        self.radio_device.setChecked(True)

        self.verticalLayout_2.addWidget(self.radio_device)

        self.label_2 = QLabel(self.frame)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout_2.addWidget(self.label_2)

        self.label_device_url = QLabel(self.frame)
        self.label_device_url.setObjectName(u"label_device_url")

        self.verticalLayout_2.addWidget(self.label_device_url)


        self.verticalLayout.addWidget(self.frame)

        self.frame_2 = QFrame(SensorCategory)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.frame_2)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.radio_external = QRadioButton(self.frame_2)
        self.buttonGroup.addButton(self.radio_external)
        self.radio_external.setObjectName(u"radio_external")

        self.verticalLayout_3.addWidget(self.radio_external)

        self.label_4 = QLabel(self.frame_2)
        self.label_4.setObjectName(u"label_4")

        self.verticalLayout_3.addWidget(self.label_4)

        self.label_external_url = QLabel(self.frame_2)
        self.label_external_url.setObjectName(u"label_external_url")

        self.verticalLayout_3.addWidget(self.label_external_url)


        self.verticalLayout.addWidget(self.frame_2)

        self.frame_3 = QFrame(SensorCategory)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Shadow.Raised)
        self.formLayout = QFormLayout(self.frame_3)
        self.formLayout.setObjectName(u"formLayout")
        self.radio_pull_data = QRadioButton(self.frame_3)
        self.buttonGroup.addButton(self.radio_pull_data)
        self.radio_pull_data.setObjectName(u"radio_pull_data")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.SpanningRole, self.radio_pull_data)

        self.label_3 = QLabel(self.frame_3)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_3)

        self.line_restim_url = QLineEdit(self.frame_3)
        self.line_restim_url.setObjectName(u"line_restim_url")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.line_restim_url)

        self.label_status = QLabel(self.frame_3)
        self.label_status.setObjectName(u"label_status")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.label_status)


        self.verticalLayout.addWidget(self.frame_3)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.retranslateUi(SensorCategory)

        QMetaObject.connectSlotsByName(SensorCategory)
    # setupUi

    def retranslateUi(self, SensorCategory):
        SensorCategory.setWindowTitle(QCoreApplication.translate("SensorCategory", u"Form", None))
        self.label.setText(QCoreApplication.translate("SensorCategory", u"<html><head/><body><p><span style=\" font-size:16pt;\">Select sensor data source</span></p></body></html>", None))
        self.radio_device.setText(QCoreApplication.translate("SensorCategory", u"Local device", None))
        self.label_2.setText(QCoreApplication.translate("SensorCategory", u"Read sensor data directly from your estim device", None))
        self.label_device_url.setText(QCoreApplication.translate("SensorCategory", u"Data available at ...", None))
        self.radio_external.setText(QCoreApplication.translate("SensorCategory", u"External application", None))
        self.label_4.setText(QCoreApplication.translate("SensorCategory", u"Use an external application to transmit the sensor readings to Restim.", None))
        self.label_external_url.setText(QCoreApplication.translate("SensorCategory", u"Send data to ws://localhost:8081/sensors/as5311", None))
        self.radio_pull_data.setText(QCoreApplication.translate("SensorCategory", u"Other Restim instance", None))
        self.label_3.setText(QCoreApplication.translate("SensorCategory", u"URL:", None))
        self.label_status.setText(QCoreApplication.translate("SensorCategory", u"Status", None))
    # retranslateUi

