# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'waveform_select.ui'
##
## Created by: Qt User Interface Compiler version 6.8.3
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
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import (QApplication, QLabel, QRadioButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget, QWizardPage)
import restim_rc

class Ui_WizardPageWaveformType(object):
    def setupUi(self, WizardPageWaveformType):
        if not WizardPageWaveformType.objectName():
            WizardPageWaveformType.setObjectName(u"WizardPageWaveformType")
        WizardPageWaveformType.resize(555, 492)
        self.verticalLayout = QVBoxLayout(WizardPageWaveformType)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.pulse_based_radio = QRadioButton(WizardPageWaveformType)
        self.pulse_based_radio.setObjectName(u"pulse_based_radio")
        self.pulse_based_radio.setChecked(True)

        self.verticalLayout.addWidget(self.pulse_based_radio)

        self.label_3 = QLabel(WizardPageWaveformType)
        self.label_3.setObjectName(u"label_3")

        self.verticalLayout.addWidget(self.label_3)

        self.svg_pulse = QSvgWidget(WizardPageWaveformType)
        self.svg_pulse.setObjectName(u"svg_pulse")
        self.svg_pulse.setMinimumSize(QSize(0, 100))

        self.verticalLayout.addWidget(self.svg_pulse)

        self.continuous_radio = QRadioButton(WizardPageWaveformType)
        self.continuous_radio.setObjectName(u"continuous_radio")

        self.verticalLayout.addWidget(self.continuous_radio)

        self.label_4 = QLabel(WizardPageWaveformType)
        self.label_4.setObjectName(u"label_4")

        self.verticalLayout.addWidget(self.label_4)

        self.svg_continuous = QSvgWidget(WizardPageWaveformType)
        self.svg_continuous.setObjectName(u"svg_continuous")
        self.svg_continuous.setMinimumSize(QSize(0, 100))

        self.verticalLayout.addWidget(self.svg_continuous)

        self.a_b_radio = QRadioButton(WizardPageWaveformType)
        self.a_b_radio.setObjectName(u"a_b_radio")

        self.verticalLayout.addWidget(self.a_b_radio)

        self.label_5 = QLabel(WizardPageWaveformType)
        self.label_5.setObjectName(u"label_5")

        self.verticalLayout.addWidget(self.label_5)

        self.verticalSpacer = QSpacerItem(20, 95, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.retranslateUi(WizardPageWaveformType)

        QMetaObject.connectSlotsByName(WizardPageWaveformType)
    # setupUi

    def retranslateUi(self, WizardPageWaveformType):
        WizardPageWaveformType.setWindowTitle(QCoreApplication.translate("WizardPageWaveformType", u"WizardPage", None))
        WizardPageWaveformType.setTitle(QCoreApplication.translate("WizardPageWaveformType", u"Select generation algorithm", None))
        self.pulse_based_radio.setText(QCoreApplication.translate("WizardPageWaveformType", u"Pulse-based", None))
        self.label_3.setText(QCoreApplication.translate("WizardPageWaveformType", u"Power-efficient waveform. Slower numbing.", None))
        self.continuous_radio.setText(QCoreApplication.translate("WizardPageWaveformType", u"Continuous", None))
        self.label_4.setText(QCoreApplication.translate("WizardPageWaveformType", u"Classic waveform. Best for 312/2B. Low power-efficiency.", None))
        self.a_b_radio.setText(QCoreApplication.translate("WizardPageWaveformType", u"A/B testing", None))
        self.label_5.setText(QCoreApplication.translate("WizardPageWaveformType", u"Experimental waveform, for science.", None))
    # retranslateUi

