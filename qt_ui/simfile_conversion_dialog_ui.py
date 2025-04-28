# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'simfileconversiondialog.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
    QFormLayout, QGridLayout, QGroupBox, QLabel,
    QLineEdit, QPlainTextEdit, QPushButton, QSizePolicy,
    QToolButton, QVBoxLayout, QWidget)

class Ui_SimfileConversionDialog(object):
    def setupUi(self, SimfileConversionDialog):
        if not SimfileConversionDialog.objectName():
            SimfileConversionDialog.setObjectName(u"SimfileConversionDialog")
        SimfileConversionDialog.resize(539, 468)
        self.verticalLayout = QVBoxLayout(SimfileConversionDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(SimfileConversionDialog)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.lineEdit_funscript = QLineEdit(self.groupBox)
        self.lineEdit_funscript.setObjectName(u"lineEdit_funscript")
        self.lineEdit_funscript.setReadOnly(True)

        self.gridLayout.addWidget(self.lineEdit_funscript, 0, 1, 1, 1)

        self.toolButton = QToolButton(self.groupBox)
        self.toolButton.setObjectName(u"toolButton")

        self.gridLayout.addWidget(self.toolButton, 0, 2, 1, 1)


        self.verticalLayout.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(SimfileConversionDialog)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.formLayout = QFormLayout(self.groupBox_2)
        self.formLayout.setObjectName(u"formLayout")
        self.label_2 = QLabel(self.groupBox_2)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_2)

        self.comboBox_notes = QComboBox(self.groupBox_2)
        self.comboBox_notes.setObjectName(u"comboBox_notes")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.comboBox_notes)

        self.label_3 = QLabel(self.groupBox_2)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_3)

        self.comboBox_interpolation = QComboBox(self.groupBox_2)
        self.comboBox_interpolation.setObjectName(u"comboBox_interpolation")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.comboBox_interpolation)

        self.label_4 = QLabel(self.groupBox_2)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_4)

        self.checkBox_debug_scripts = QCheckBox(self.groupBox_2)
        self.checkBox_debug_scripts.setObjectName(u"checkBox_debug_scripts")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.checkBox_debug_scripts)


        self.verticalLayout.addWidget(self.groupBox_2)

        self.pushButton = QPushButton(SimfileConversionDialog)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setMaximumSize(QSize(100, 16777215))

        self.verticalLayout.addWidget(self.pushButton)

        self.groupBox_3 = QGroupBox(SimfileConversionDialog)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.plainTextEdit = QPlainTextEdit(self.groupBox_3)
        self.plainTextEdit.setObjectName(u"plainTextEdit")

        self.verticalLayout_2.addWidget(self.plainTextEdit)


        self.verticalLayout.addWidget(self.groupBox_3)


        self.retranslateUi(SimfileConversionDialog)

        QMetaObject.connectSlotsByName(SimfileConversionDialog)
    # setupUi

    def retranslateUi(self, SimfileConversionDialog):
        SimfileConversionDialog.setWindowTitle(QCoreApplication.translate("SimfileConversionDialog", u"Dialog", None))
        self.groupBox.setTitle(QCoreApplication.translate("SimfileConversionDialog", u"Files", None))
        self.label.setText(QCoreApplication.translate("SimfileConversionDialog", u"simfile", None))
        self.toolButton.setText(QCoreApplication.translate("SimfileConversionDialog", u"...", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("SimfileConversionDialog", u"Options", None))
        self.label_2.setText(QCoreApplication.translate("SimfileConversionDialog", u"Chart", None))
        self.label_3.setText(QCoreApplication.translate("SimfileConversionDialog", u"atk/sus/rel", None))
        self.label_4.setText(QCoreApplication.translate("SimfileConversionDialog", u"output debug scripts", None))
        self.checkBox_debug_scripts.setText("")
        self.pushButton.setText(QCoreApplication.translate("SimfileConversionDialog", u"convert", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("SimfileConversionDialog", u"Log", None))
    # retranslateUi

