# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'safety_limits.ui'
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
from PySide6.QtWidgets import (QApplication, QDoubleSpinBox, QFormLayout, QLabel,
    QSizePolicy, QTextBrowser, QWidget, QWizardPage)

class Ui_WizardPageSafetyLimits(object):
    def setupUi(self, WizardPageSafetyLimits):
        if not WizardPageSafetyLimits.objectName():
            WizardPageSafetyLimits.setObjectName(u"WizardPageSafetyLimits")
        WizardPageSafetyLimits.resize(556, 375)
        self.formLayout = QFormLayout(WizardPageSafetyLimits)
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(WizardPageSafetyLimits)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)

        self.label_2 = QLabel(WizardPageSafetyLimits)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.textBrowser = QTextBrowser(WizardPageSafetyLimits)
        self.textBrowser.setObjectName(u"textBrowser")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.SpanningRole, self.textBrowser)

        self.min_frequency_spinbox = QDoubleSpinBox(WizardPageSafetyLimits)
        self.min_frequency_spinbox.setObjectName(u"min_frequency_spinbox")
        self.min_frequency_spinbox.setDecimals(0)
        self.min_frequency_spinbox.setMinimum(1.000000000000000)
        self.min_frequency_spinbox.setMaximum(10000.000000000000000)
        self.min_frequency_spinbox.setValue(500.000000000000000)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.min_frequency_spinbox)

        self.max_frequency_spinbox = QDoubleSpinBox(WizardPageSafetyLimits)
        self.max_frequency_spinbox.setObjectName(u"max_frequency_spinbox")
        self.max_frequency_spinbox.setDecimals(0)
        self.max_frequency_spinbox.setMinimum(1.000000000000000)
        self.max_frequency_spinbox.setMaximum(10000.000000000000000)
        self.max_frequency_spinbox.setValue(1000.000000000000000)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.max_frequency_spinbox)


        self.retranslateUi(WizardPageSafetyLimits)

        QMetaObject.connectSlotsByName(WizardPageSafetyLimits)
    # setupUi

    def retranslateUi(self, WizardPageSafetyLimits):
        WizardPageSafetyLimits.setWindowTitle(QCoreApplication.translate("WizardPageSafetyLimits", u"WizardPage", None))
        WizardPageSafetyLimits.setTitle(QCoreApplication.translate("WizardPageSafetyLimits", u"Safety limits", None))
        self.label.setText(QCoreApplication.translate("WizardPageSafetyLimits", u"Minimum frequency [Hz]", None))
        self.label_2.setText(QCoreApplication.translate("WizardPageSafetyLimits", u"Maximum frequency [Hz]", None))
        self.textBrowser.setHtml(QCoreApplication.translate("WizardPageSafetyLimits", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:14pt;\">Recommended settings for audio-based devices:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:8pt;\">Safest: 500-1000</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; m"
                        "argin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:8pt;\">Probably safe: 500-1500</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:8.25pt;\">Pulse-based mode only: 500-1500+?</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'MS Shell Dlg 2'; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:8pt;\">Higher frequencies are less power-efficient and more likely to cause burns. </span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-fam"
                        "ily:'MS Shell Dlg 2'; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:8pt;\">With the pulse-based signal generator you can generate high frequency signals with low duty cycle, which are very power-efficient. I tested signals up to 8000Hz for short periods of time without negative effects. These frequencies should absolutely not be used with continuous waveforms.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'MS Shell Dlg 2'; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:14pt;\">Recommended settings for 312/2B:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; "
                        "margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:8pt;\">For 312/2B these settings have no safety implications.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:'MS Shell Dlg 2'; font-size:8pt;\">I have been told a frequency around 100hz works best with the 312.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:'MS Shell Dlg 2'; font-size:8.25pt;\"><br /></p></body></html>", None))
    # retranslateUi

