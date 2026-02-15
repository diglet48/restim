# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'fourphasesettingswidget.ui'
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
from PySide6.QtWidgets import (QApplication, QDoubleSpinBox, QFormLayout, QGroupBox,
    QLabel, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_FourPhaseSettingsWidget(object):
    def setupUi(self, FourPhaseSettingsWidget):
        if not FourPhaseSettingsWidget.objectName():
            FourPhaseSettingsWidget.setObjectName(u"FourPhaseSettingsWidget")
        FourPhaseSettingsWidget.resize(452, 410)
        self.verticalLayout = QVBoxLayout(FourPhaseSettingsWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(FourPhaseSettingsWidget)
        self.groupBox.setObjectName(u"groupBox")
        self.formLayout = QFormLayout(self.groupBox)
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)

        self.a_power = QDoubleSpinBox(self.groupBox)
        self.a_power.setObjectName(u"a_power")
        self.a_power.setKeyboardTracking(False)
        self.a_power.setMinimum(-10.000000000000000)
        self.a_power.setMaximum(10.000000000000000)
        self.a_power.setSingleStep(0.100000000000000)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.a_power)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_3)

        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_4)

        self.b_power = QDoubleSpinBox(self.groupBox)
        self.b_power.setObjectName(u"b_power")
        self.b_power.setKeyboardTracking(False)
        self.b_power.setMinimum(-10.000000000000000)
        self.b_power.setMaximum(10.000000000000000)
        self.b_power.setSingleStep(0.100000000000000)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.b_power)

        self.c_power = QDoubleSpinBox(self.groupBox)
        self.c_power.setObjectName(u"c_power")
        self.c_power.setKeyboardTracking(False)
        self.c_power.setMinimum(-10.000000000000000)
        self.c_power.setMaximum(10.000000000000000)
        self.c_power.setSingleStep(0.100000000000000)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.c_power)

        self.d_power = QDoubleSpinBox(self.groupBox)
        self.d_power.setObjectName(u"d_power")
        self.d_power.setKeyboardTracking(False)
        self.d_power.setMinimum(-10.000000000000000)
        self.d_power.setMaximum(10.000000000000000)
        self.d_power.setSingleStep(0.100000000000000)

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.d_power)

        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")

        self.formLayout.setWidget(4, QFormLayout.ItemRole.LabelRole, self.label_5)

        self.center_power = QDoubleSpinBox(self.groupBox)
        self.center_power.setObjectName(u"center_power")
        self.center_power.setEnabled(False)
        self.center_power.setKeyboardTracking(False)
        self.center_power.setMinimum(-10.000000000000000)
        self.center_power.setMaximum(10.000000000000000)
        self.center_power.setSingleStep(0.100000000000000)

        self.formLayout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.center_power)


        self.verticalLayout.addWidget(self.groupBox)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.retranslateUi(FourPhaseSettingsWidget)

        QMetaObject.connectSlotsByName(FourPhaseSettingsWidget)
    # setupUi

    def retranslateUi(self, FourPhaseSettingsWidget):
        FourPhaseSettingsWidget.setWindowTitle(QCoreApplication.translate("FourPhaseSettingsWidget", u"Form", None))
        self.groupBox.setTitle(QCoreApplication.translate("FourPhaseSettingsWidget", u"Calibration", None))
        self.label.setText(QCoreApplication.translate("FourPhaseSettingsWidget", u"A power [dB]", None))
        self.label_2.setText(QCoreApplication.translate("FourPhaseSettingsWidget", u"B power [dB]", None))
        self.label_3.setText(QCoreApplication.translate("FourPhaseSettingsWidget", u"C power [dB]", None))
        self.label_4.setText(QCoreApplication.translate("FourPhaseSettingsWidget", u"D power [dB]", None))
        self.label_5.setText(QCoreApplication.translate("FourPhaseSettingsWidget", u"Center power [dB]", None))
    # retranslateUi

