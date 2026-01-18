# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'additionalsearchpathsdialog.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QDialog, QDialogButtonBox,
    QHBoxLayout, QLabel, QListView, QPushButton,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_AdditionalSearchPathsDialog(object):
    def setupUi(self, AdditionalSearchPathsDialog):
        if not AdditionalSearchPathsDialog.objectName():
            AdditionalSearchPathsDialog.setObjectName(u"AdditionalSearchPathsDialog")
        AdditionalSearchPathsDialog.resize(556, 492)
        self.actionAdd = QAction(AdditionalSearchPathsDialog)
        self.actionAdd.setObjectName(u"actionAdd")
        self.actionRemove = QAction(AdditionalSearchPathsDialog)
        self.actionRemove.setObjectName(u"actionRemove")
        self.verticalLayout = QVBoxLayout(AdditionalSearchPathsDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.listView = QListView(AdditionalSearchPathsDialog)
        self.listView.setObjectName(u"listView")

        self.verticalLayout.addWidget(self.listView)

        self.widget = QWidget(AdditionalSearchPathsDialog)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.button_add = QPushButton(self.widget)
        self.button_add.setObjectName(u"button_add")

        self.horizontalLayout.addWidget(self.button_add)

        self.button_remove = QPushButton(self.widget)
        self.button_remove.setObjectName(u"button_remove")

        self.horizontalLayout.addWidget(self.button_remove)

        self.label = QLabel(self.widget)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addWidget(self.widget)

        self.buttonBox = QDialogButtonBox(AdditionalSearchPathsDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(AdditionalSearchPathsDialog)
        self.buttonBox.accepted.connect(AdditionalSearchPathsDialog.accept)
        self.buttonBox.rejected.connect(AdditionalSearchPathsDialog.reject)
        self.button_add.clicked.connect(self.actionAdd.trigger)
        self.button_remove.clicked.connect(self.actionRemove.trigger)

        QMetaObject.connectSlotsByName(AdditionalSearchPathsDialog)
    # setupUi

    def retranslateUi(self, AdditionalSearchPathsDialog):
        AdditionalSearchPathsDialog.setWindowTitle(QCoreApplication.translate("AdditionalSearchPathsDialog", u"Extra search paths", None))
        self.actionAdd.setText(QCoreApplication.translate("AdditionalSearchPathsDialog", u"Add", None))
        self.actionRemove.setText(QCoreApplication.translate("AdditionalSearchPathsDialog", u"Remove", None))
        self.button_add.setText(QCoreApplication.translate("AdditionalSearchPathsDialog", u"Add", None))
        self.button_remove.setText(QCoreApplication.translate("AdditionalSearchPathsDialog", u"Remove selected", None))
        self.label.setText(QCoreApplication.translate("AdditionalSearchPathsDialog", u"Check entries to search subdirectories", None))
    # retranslateUi

