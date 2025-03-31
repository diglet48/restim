# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'focstim_waveform_select.ui'
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
from PySide6.QtWidgets import (QApplication, QRadioButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget, QWizardPage)

class Ui_WizardPageFocStim(object):
    def setupUi(self, WizardPageFocStim):
        if not WizardPageFocStim.objectName():
            WizardPageFocStim.setObjectName(u"WizardPageFocStim")
        WizardPageFocStim.resize(611, 497)
        self.verticalLayout = QVBoxLayout(WizardPageFocStim)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.three_phase_radio = QRadioButton(WizardPageFocStim)
        self.three_phase_radio.setObjectName(u"three_phase_radio")

        self.verticalLayout.addWidget(self.three_phase_radio)

        self.four_phase_radio = QRadioButton(WizardPageFocStim)
        self.four_phase_radio.setObjectName(u"four_phase_radio")

        self.verticalLayout.addWidget(self.four_phase_radio)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.retranslateUi(WizardPageFocStim)

        QMetaObject.connectSlotsByName(WizardPageFocStim)
    # setupUi

    def retranslateUi(self, WizardPageFocStim):
        WizardPageFocStim.setWindowTitle(QCoreApplication.translate("WizardPageFocStim", u"WizardPage", None))
        self.three_phase_radio.setText(QCoreApplication.translate("WizardPageFocStim", u"Three-phase", None))
        self.four_phase_radio.setText(QCoreApplication.translate("WizardPageFocStim", u"Four-phase", None))
    # retranslateUi

