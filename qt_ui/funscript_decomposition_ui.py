# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'funscriptdecompositiondialog.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QFormLayout,
    QGridLayout, QGroupBox, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QTextEdit, QToolButton,
    QVBoxLayout, QWidget)

class Ui_FunscriptDecompositionDialog(object):
    def setupUi(self, FunscriptDecompositionDialog):
        if not FunscriptDecompositionDialog.objectName():
            FunscriptDecompositionDialog.setObjectName(u"FunscriptDecompositionDialog")
        FunscriptDecompositionDialog.resize(601, 321)
        self.verticalLayout = QVBoxLayout(FunscriptDecompositionDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(FunscriptDecompositionDialog)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.lineEdit_funscript = QLineEdit(self.groupBox)
        self.lineEdit_funscript.setObjectName(u"lineEdit_funscript")

        self.gridLayout.addWidget(self.lineEdit_funscript, 0, 1, 1, 1)

        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.toolButton = QToolButton(self.groupBox)
        self.toolButton.setObjectName(u"toolButton")

        self.gridLayout.addWidget(self.toolButton, 0, 2, 1, 1)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.comboBox_action = QComboBox(self.groupBox)
        self.comboBox_action.setObjectName(u"comboBox_action")

        self.gridLayout.addWidget(self.comboBox_action, 1, 1, 1, 1)


        self.verticalLayout.addWidget(self.groupBox)

        self.widget = QWidget(FunscriptDecompositionDialog)
        self.widget.setObjectName(u"widget")
        self.formLayout = QFormLayout(self.widget)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setContentsMargins(-1, 0, 0, 0)
        self.pushButton = QPushButton(self.widget)
        self.pushButton.setObjectName(u"pushButton")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.pushButton)


        self.verticalLayout.addWidget(self.widget)

        self.groupBox_2 = QGroupBox(FunscriptDecompositionDialog)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout_2 = QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.textEdit = QTextEdit(self.groupBox_2)
        self.textEdit.setObjectName(u"textEdit")

        self.gridLayout_2.addWidget(self.textEdit, 0, 0, 1, 1)


        self.verticalLayout.addWidget(self.groupBox_2)


        self.retranslateUi(FunscriptDecompositionDialog)

        QMetaObject.connectSlotsByName(FunscriptDecompositionDialog)
    # setupUi

    def retranslateUi(self, FunscriptDecompositionDialog):
        FunscriptDecompositionDialog.setWindowTitle(QCoreApplication.translate("FunscriptDecompositionDialog", u"Dialog", None))
        self.groupBox.setTitle(QCoreApplication.translate("FunscriptDecompositionDialog", u"Files", None))
        self.label.setText(QCoreApplication.translate("FunscriptDecompositionDialog", u"Base funscript or video file", None))
        self.toolButton.setText(QCoreApplication.translate("FunscriptDecompositionDialog", u"...", None))
        self.label_2.setText(QCoreApplication.translate("FunscriptDecompositionDialog", u"Action", None))
        self.pushButton.setText(QCoreApplication.translate("FunscriptDecompositionDialog", u"Convert", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("FunscriptDecompositionDialog", u"log", None))
    # retranslateUi

