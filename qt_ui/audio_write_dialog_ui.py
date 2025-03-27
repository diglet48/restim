# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'audiowritedialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QComboBox, QCommandLinkButton,
    QDialog, QDialogButtonBox, QDoubleSpinBox, QFormLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QProgressBar, QSizePolicy, QTextBrowser, QToolButton,
    QVBoxLayout, QWidget)

class Ui_AudioWriteDialog(object):
    def setupUi(self, AudioWriteDialog):
        if not AudioWriteDialog.objectName():
            AudioWriteDialog.setObjectName(u"AudioWriteDialog")
        AudioWriteDialog.resize(634, 408)
        self.verticalLayout = QVBoxLayout(AudioWriteDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.textBrowser = QTextBrowser(AudioWriteDialog)
        self.textBrowser.setObjectName(u"textBrowser")

        self.verticalLayout.addWidget(self.textBrowser)

        self.groupBox = QGroupBox(AudioWriteDialog)
        self.groupBox.setObjectName(u"groupBox")
        self.formLayout = QFormLayout(self.groupBox)
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)

        self.duration_spinbox = QDoubleSpinBox(self.groupBox)
        self.duration_spinbox.setObjectName(u"duration_spinbox")
        self.duration_spinbox.setMaximum(100000.000000000000000)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.duration_spinbox)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_2)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_3)

        self.widget = QWidget(self.groupBox)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.file_edit = QLineEdit(self.widget)
        self.file_edit.setObjectName(u"file_edit")

        self.horizontalLayout.addWidget(self.file_edit)

        self.file_picker_button = QToolButton(self.widget)
        self.file_picker_button.setObjectName(u"file_picker_button")

        self.horizontalLayout.addWidget(self.file_picker_button)


        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.widget)

        self.samplerate_spinbox = QComboBox(self.groupBox)
        self.samplerate_spinbox.addItem("")
        self.samplerate_spinbox.addItem("")
        self.samplerate_spinbox.addItem("")
        self.samplerate_spinbox.addItem("")
        self.samplerate_spinbox.addItem("")
        self.samplerate_spinbox.addItem("")
        self.samplerate_spinbox.addItem("")
        self.samplerate_spinbox.addItem("")
        self.samplerate_spinbox.setObjectName(u"samplerate_spinbox")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.samplerate_spinbox)


        self.verticalLayout.addWidget(self.groupBox)

        self.widget_2 = QWidget(AudioWriteDialog)
        self.widget_2.setObjectName(u"widget_2")
        self.verticalLayout_2 = QVBoxLayout(self.widget_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.commandLinkButton = QCommandLinkButton(self.widget_2)
        self.commandLinkButton.setObjectName(u"commandLinkButton")

        self.verticalLayout_2.addWidget(self.commandLinkButton)

        self.progressBar = QProgressBar(self.widget_2)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setValue(0)

        self.verticalLayout_2.addWidget(self.progressBar)


        self.verticalLayout.addWidget(self.widget_2)

        self.buttonBox = QDialogButtonBox(AudioWriteDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(AudioWriteDialog)
        self.buttonBox.accepted.connect(AudioWriteDialog.accept)
        self.buttonBox.rejected.connect(AudioWriteDialog.reject)

        QMetaObject.connectSlotsByName(AudioWriteDialog)
    # setupUi

    def retranslateUi(self, AudioWriteDialog):
        AudioWriteDialog.setWindowTitle(QCoreApplication.translate("AudioWriteDialog", u"Create audio file", None))
        self.textBrowser.setHtml(QCoreApplication.translate("AudioWriteDialog", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'MS Shell Dlg 2'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Generate audio file (mp3).</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">- The currently loaded funscripts are used.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">- For axes with no funscript, the value from the GUI is used. This includes calibration settings, transform, carrier, pulse settings and vibration.</p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-righ"
                        "t:0px; -qt-block-indent:0; text-indent:0px;\">- Output volume is determined by funscript. Volume controls and volume ramp does NOT work.</p></body></html>", None))
        self.groupBox.setTitle(QCoreApplication.translate("AudioWriteDialog", u"Settings", None))
        self.label.setText(QCoreApplication.translate("AudioWriteDialog", u"Media duration [s]", None))
        self.label_2.setText(QCoreApplication.translate("AudioWriteDialog", u"Sample rate [samples/s]", None))
        self.label_3.setText(QCoreApplication.translate("AudioWriteDialog", u"Output file (wav, mp3, ...)", None))
        self.file_picker_button.setText(QCoreApplication.translate("AudioWriteDialog", u"...", None))
        self.samplerate_spinbox.setItemText(0, QCoreApplication.translate("AudioWriteDialog", u"8000", None))
        self.samplerate_spinbox.setItemText(1, QCoreApplication.translate("AudioWriteDialog", u"11025", None))
        self.samplerate_spinbox.setItemText(2, QCoreApplication.translate("AudioWriteDialog", u"16000", None))
        self.samplerate_spinbox.setItemText(3, QCoreApplication.translate("AudioWriteDialog", u"22050", None))
        self.samplerate_spinbox.setItemText(4, QCoreApplication.translate("AudioWriteDialog", u"44100", None))
        self.samplerate_spinbox.setItemText(5, QCoreApplication.translate("AudioWriteDialog", u"48000", None))
        self.samplerate_spinbox.setItemText(6, QCoreApplication.translate("AudioWriteDialog", u"88200", None))
        self.samplerate_spinbox.setItemText(7, QCoreApplication.translate("AudioWriteDialog", u"96000", None))

        self.commandLinkButton.setText(QCoreApplication.translate("AudioWriteDialog", u"Create audio file", None))
    # retranslateUi

