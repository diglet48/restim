# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'as5311settingswidget.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QDoubleSpinBox, QFormLayout,
    QGroupBox, QLabel, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

from pyqtgraph import GraphicsLayoutWidget

class Ui_AS5311SettingsWidget(object):
    def setupUi(self, AS5311SettingsWidget):
        if not AS5311SettingsWidget.objectName():
            AS5311SettingsWidget.setObjectName(u"AS5311SettingsWidget")
        AS5311SettingsWidget.resize(614, 644)
        self.verticalLayout = QVBoxLayout(AS5311SettingsWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(AS5311SettingsWidget)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.formLayout = QFormLayout(self.groupBox)
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.doubleSpinBox_range = QDoubleSpinBox(self.groupBox)
        self.doubleSpinBox_range.setObjectName(u"doubleSpinBox_range")
        self.doubleSpinBox_range.setMaximum(10000.000000000000000)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.doubleSpinBox_range)

        self.doubleSpinBox_reduction = QDoubleSpinBox(self.groupBox)
        self.doubleSpinBox_reduction.setObjectName(u"doubleSpinBox_reduction")
        self.doubleSpinBox_reduction.setMaximum(100.000000000000000)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.doubleSpinBox_reduction)


        self.verticalLayout.addWidget(self.groupBox)

        self.groupBox_3 = QGroupBox(AS5311SettingsWidget)
        self.groupBox_3.setObjectName(u"groupBox_3")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.groupBox_3.sizePolicy().hasHeightForWidth())
        self.groupBox_3.setSizePolicy(sizePolicy1)
        self.groupBox_3.setMaximumSize(QSize(16777215, 16777215))
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.checkBox = QCheckBox(self.groupBox_3)
        self.checkBox.setObjectName(u"checkBox")

        self.verticalLayout_2.addWidget(self.checkBox)

        self.graph = GraphicsLayoutWidget(self.groupBox_3)
        self.graph.setObjectName(u"graph")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(100)
        sizePolicy2.setHeightForWidth(self.graph.sizePolicy().hasHeightForWidth())
        self.graph.setSizePolicy(sizePolicy2)
        self.graph.setMinimumSize(QSize(0, 50))
        self.graph.setMaximumSize(QSize(16777215, 500))

        self.verticalLayout_2.addWidget(self.graph)

        self.verticalSpacer = QSpacerItem(20, 1, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)


        self.verticalLayout.addWidget(self.groupBox_3)


        self.retranslateUi(AS5311SettingsWidget)

        QMetaObject.connectSlotsByName(AS5311SettingsWidget)
    # setupUi

    def retranslateUi(self, AS5311SettingsWidget):
        AS5311SettingsWidget.setWindowTitle(QCoreApplication.translate("AS5311SettingsWidget", u"Form", None))
        self.groupBox.setTitle(QCoreApplication.translate("AS5311SettingsWidget", u"Movement", None))
        self.label.setText(QCoreApplication.translate("AS5311SettingsWidget", u"range (\u00b5m)", None))
        self.label_2.setText(QCoreApplication.translate("AS5311SettingsWidget", u"reduction (%)", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("AS5311SettingsWidget", u"Live update", None))
        self.checkBox.setText(QCoreApplication.translate("AS5311SettingsWidget", u"update", None))
    # retranslateUi

