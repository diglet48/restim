# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'safety_limits_foc.ui'
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
    QLabel, QSizePolicy, QSpacerItem, QTextBrowser,
    QVBoxLayout, QWidget, QWizardPage)

class Ui_WizardPageSafetyLimitsFOC(object):
    def setupUi(self, WizardPageSafetyLimitsFOC):
        if not WizardPageSafetyLimitsFOC.objectName():
            WizardPageSafetyLimitsFOC.setObjectName(u"WizardPageSafetyLimitsFOC")
        WizardPageSafetyLimitsFOC.resize(606, 424)
        self.verticalLayout = QVBoxLayout(WizardPageSafetyLimitsFOC)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox_2 = QGroupBox(WizardPageSafetyLimitsFOC)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.formLayout = QFormLayout(self.groupBox_2)
        self.formLayout.setObjectName(u"formLayout")
        self.label_2 = QLabel(self.groupBox_2)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.min_frequency_spinbox = QDoubleSpinBox(self.groupBox_2)
        self.min_frequency_spinbox.setObjectName(u"min_frequency_spinbox")
        self.min_frequency_spinbox.setDecimals(0)
        self.min_frequency_spinbox.setMaximum(2000.000000000000000)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.min_frequency_spinbox)

        self.label_3 = QLabel(self.groupBox_2)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_3)

        self.max_frequency_spinbox = QDoubleSpinBox(self.groupBox_2)
        self.max_frequency_spinbox.setObjectName(u"max_frequency_spinbox")
        self.max_frequency_spinbox.setDecimals(0)
        self.max_frequency_spinbox.setMaximum(2000.000000000000000)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.max_frequency_spinbox)

        self.textBrowser = QTextBrowser(self.groupBox_2)
        self.textBrowser.setObjectName(u"textBrowser")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.SpanningRole, self.textBrowser)


        self.verticalLayout.addWidget(self.groupBox_2)

        self.groupBox = QGroupBox(WizardPageSafetyLimitsFOC)
        self.groupBox.setObjectName(u"groupBox")
        self.formLayout_2 = QFormLayout(self.groupBox)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)

        self.waveform_ampltiude_ma_spinbox = QDoubleSpinBox(self.groupBox)
        self.waveform_ampltiude_ma_spinbox.setObjectName(u"waveform_ampltiude_ma_spinbox")
        self.waveform_ampltiude_ma_spinbox.setDecimals(0)
        self.waveform_ampltiude_ma_spinbox.setMaximum(150.000000000000000)

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.waveform_ampltiude_ma_spinbox)

        self.textBrowser_2 = QTextBrowser(self.groupBox)
        self.textBrowser_2.setObjectName(u"textBrowser_2")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.SpanningRole, self.textBrowser_2)


        self.verticalLayout.addWidget(self.groupBox)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.retranslateUi(WizardPageSafetyLimitsFOC)

        QMetaObject.connectSlotsByName(WizardPageSafetyLimitsFOC)
    # setupUi

    def retranslateUi(self, WizardPageSafetyLimitsFOC):
        WizardPageSafetyLimitsFOC.setWindowTitle(QCoreApplication.translate("WizardPageSafetyLimitsFOC", u"WizardPage", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("WizardPageSafetyLimitsFOC", u"Frequency", None))
        self.label_2.setText(QCoreApplication.translate("WizardPageSafetyLimitsFOC", u"Minimum frequency [Hz]", None))
        self.label_3.setText(QCoreApplication.translate("WizardPageSafetyLimitsFOC", u"Maximum frequency [Hz]", None))
        self.textBrowser.setHtml(QCoreApplication.translate("WizardPageSafetyLimitsFOC", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Default 500-2000Hz</p></body></html>", None))
        self.groupBox.setTitle(QCoreApplication.translate("WizardPageSafetyLimitsFOC", u"Output power", None))
        self.label.setText(QCoreApplication.translate("WizardPageSafetyLimitsFOC", u"Waveform amplitude [mA]", None))
        self.textBrowser_2.setHtml(QCoreApplication.translate("WizardPageSafetyLimitsFOC", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Default 120mA</p></body></html>", None))
    # retranslateUi

