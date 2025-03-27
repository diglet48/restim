# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'funscriptconversiondialog.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QDoubleSpinBox, QFormLayout,
    QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QTextEdit,
    QToolButton, QWidget)

class Ui_FunscriptConversionDialog(object):
    def setupUi(self, FunscriptConversionDialog):
        if not FunscriptConversionDialog.objectName():
            FunscriptConversionDialog.setObjectName(u"FunscriptConversionDialog")
        FunscriptConversionDialog.resize(542, 429)
        self.gridLayout = QGridLayout(FunscriptConversionDialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.widget_2 = QWidget(FunscriptConversionDialog)
        self.widget_2.setObjectName(u"widget_2")
        self.formLayout = QFormLayout(self.widget_2)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setContentsMargins(-1, 0, 0, 0)
        self.pushButton = QPushButton(self.widget_2)
        self.pushButton.setObjectName(u"pushButton")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.pushButton)


        self.gridLayout.addWidget(self.widget_2, 3, 0, 1, 1)

        self.groupBox_2 = QGroupBox(FunscriptConversionDialog)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout_3 = QGridLayout(self.groupBox_2)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.lineEdit_funscript = QLineEdit(self.groupBox_2)
        self.lineEdit_funscript.setObjectName(u"lineEdit_funscript")

        self.gridLayout_3.addWidget(self.lineEdit_funscript, 0, 1, 1, 1)

        self.label = QLabel(self.groupBox_2)
        self.label.setObjectName(u"label")

        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 1)

        self.toolButton = QToolButton(self.groupBox_2)
        self.toolButton.setObjectName(u"toolButton")

        self.gridLayout_3.addWidget(self.toolButton, 0, 2, 1, 1)

        self.label_2 = QLabel(self.groupBox_2)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_3.addWidget(self.label_2, 1, 0, 1, 1)

        self.lineEdit_alpha = QLineEdit(self.groupBox_2)
        self.lineEdit_alpha.setObjectName(u"lineEdit_alpha")

        self.gridLayout_3.addWidget(self.lineEdit_alpha, 1, 1, 1, 1)

        self.label_3 = QLabel(self.groupBox_2)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_3.addWidget(self.label_3, 2, 0, 1, 1)

        self.lineEdit_beta = QLineEdit(self.groupBox_2)
        self.lineEdit_beta.setObjectName(u"lineEdit_beta")

        self.gridLayout_3.addWidget(self.lineEdit_beta, 2, 1, 1, 1)


        self.gridLayout.addWidget(self.groupBox_2, 0, 0, 1, 1)

        self.groupBox_3 = QGroupBox(FunscriptConversionDialog)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.formLayout_2 = QFormLayout(self.groupBox_3)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.label_4 = QLabel(self.groupBox_3)
        self.label_4.setObjectName(u"label_4")

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.label_4)

        self.random_direction_change_probability = QDoubleSpinBox(self.groupBox_3)
        self.random_direction_change_probability.setObjectName(u"random_direction_change_probability")
        self.random_direction_change_probability.setDecimals(0)
        self.random_direction_change_probability.setMaximum(100.000000000000000)
        self.random_direction_change_probability.setValue(5.000000000000000)

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.random_direction_change_probability)


        self.gridLayout.addWidget(self.groupBox_3, 1, 0, 1, 1)

        self.groupBox = QGroupBox(FunscriptConversionDialog)
        self.groupBox.setObjectName(u"groupBox")
        self.horizontalLayout = QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.textEdit = QTextEdit(self.groupBox)
        self.textEdit.setObjectName(u"textEdit")

        self.horizontalLayout.addWidget(self.textEdit)


        self.gridLayout.addWidget(self.groupBox, 4, 0, 1, 1)


        self.retranslateUi(FunscriptConversionDialog)

        QMetaObject.connectSlotsByName(FunscriptConversionDialog)
    # setupUi

    def retranslateUi(self, FunscriptConversionDialog):
        FunscriptConversionDialog.setWindowTitle(QCoreApplication.translate("FunscriptConversionDialog", u"Funscript conversion - 1d to 2d", None))
        self.pushButton.setText(QCoreApplication.translate("FunscriptConversionDialog", u"Convert", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("FunscriptConversionDialog", u"Files", None))
        self.label.setText(QCoreApplication.translate("FunscriptConversionDialog", u"Funscript", None))
        self.toolButton.setText(QCoreApplication.translate("FunscriptConversionDialog", u"...", None))
        self.label_2.setText(QCoreApplication.translate("FunscriptConversionDialog", u"Alpha axis", None))
        self.label_3.setText(QCoreApplication.translate("FunscriptConversionDialog", u"Beta axis", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("FunscriptConversionDialog", u"Options", None))
        self.label_4.setText(QCoreApplication.translate("FunscriptConversionDialog", u"Random direction change probability", None))
        self.random_direction_change_probability.setSuffix(QCoreApplication.translate("FunscriptConversionDialog", u"%", None))
        self.groupBox.setTitle(QCoreApplication.translate("FunscriptConversionDialog", u"log", None))
    # retranslateUi

