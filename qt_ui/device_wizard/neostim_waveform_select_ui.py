# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'neostim_waveform_select.ui'
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
from PySide6.QtWidgets import (QApplication, QLabel, QRadioButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget, QWizardPage)

class Ui_WizardPageNeoStim(object):
    def setupUi(self, WizardPageNeoStim):
        if not WizardPageNeoStim.objectName():
            WizardPageNeoStim.setObjectName(u"WizardPageNeoStim")
        WizardPageNeoStim.resize(611, 497)
        self.verticalLayout = QVBoxLayout(WizardPageNeoStim)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.three_phase_radio = QRadioButton(WizardPageNeoStim)
        self.three_phase_radio.setObjectName(u"three_phase_radio")

        self.verticalLayout.addWidget(self.three_phase_radio)

        self.label = QLabel(WizardPageNeoStim)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.retranslateUi(WizardPageNeoStim)

        QMetaObject.connectSlotsByName(WizardPageNeoStim)
    # setupUi

    def retranslateUi(self, WizardPageNeoStim):
        WizardPageNeoStim.setWindowTitle(QCoreApplication.translate("WizardPageNeoStim", u"WizardPage", None))
        self.three_phase_radio.setText(QCoreApplication.translate("WizardPageNeoStim", u"Three-phase", None))
        self.label.setText(QCoreApplication.translate("WizardPageNeoStim", u"<html><head/><body><p>A = neutral<br/>B = left<br/>C+D = right. Short these outputs together on your box.</p><p><br/></p></body></html>", None))
    # retranslateUi

