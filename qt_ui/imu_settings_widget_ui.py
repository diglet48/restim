# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'imusettingswidget.ui'
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

from pyqtgraph import PlotWidget

class Ui_IMUSettingsWidget(object):
    def setupUi(self, IMUSettingsWidget):
        if not IMUSettingsWidget.objectName():
            IMUSettingsWidget.setObjectName(u"IMUSettingsWidget")
        IMUSettingsWidget.resize(614, 644)
        self.verticalLayout = QVBoxLayout(IMUSettingsWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(IMUSettingsWidget)
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

        self.doubleSpinBox_movement_in = QDoubleSpinBox(self.groupBox)
        self.doubleSpinBox_movement_in.setObjectName(u"doubleSpinBox_movement_in")
        self.doubleSpinBox_movement_in.setDecimals(1)
        self.doubleSpinBox_movement_in.setMinimum(-100.000000000000000)
        self.doubleSpinBox_movement_in.setSingleStep(0.100000000000000)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.doubleSpinBox_movement_in)

        self.doubleSpinBox_movement_out = QDoubleSpinBox(self.groupBox)
        self.doubleSpinBox_movement_out.setObjectName(u"doubleSpinBox_movement_out")
        self.doubleSpinBox_movement_out.setDecimals(1)
        self.doubleSpinBox_movement_out.setMinimum(-1.000000000000000)
        self.doubleSpinBox_movement_out.setMaximum(1.000000000000000)
        self.doubleSpinBox_movement_out.setSingleStep(0.100000000000000)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.doubleSpinBox_movement_out)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_2)


        self.verticalLayout.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(IMUSettingsWidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.formLayout_2 = QFormLayout(self.groupBox_2)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.label_3 = QLabel(self.groupBox_2)
        self.label_3.setObjectName(u"label_3")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_3)

        self.label_4 = QLabel(self.groupBox_2)
        self.label_4.setObjectName(u"label_4")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_4)

        self.doubleSpinBox_velocity_in = QDoubleSpinBox(self.groupBox_2)
        self.doubleSpinBox_velocity_in.setObjectName(u"doubleSpinBox_velocity_in")
        self.doubleSpinBox_velocity_in.setDecimals(0)
        self.doubleSpinBox_velocity_in.setMinimum(0.000000000000000)

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.doubleSpinBox_velocity_in)

        self.doubleSpinBox_intensity_increase = QDoubleSpinBox(self.groupBox_2)
        self.doubleSpinBox_intensity_increase.setObjectName(u"doubleSpinBox_intensity_increase")
        self.doubleSpinBox_intensity_increase.setMinimum(-100.000000000000000)
        self.doubleSpinBox_intensity_increase.setMaximum(100.000000000000000)
        self.doubleSpinBox_intensity_increase.setSingleStep(0.100000000000000)

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.doubleSpinBox_intensity_increase)


        self.verticalLayout.addWidget(self.groupBox_2)

        self.groupBox_3 = QGroupBox(IMUSettingsWidget)
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

        self.graph = PlotWidget(self.groupBox_3)
        self.graph.setObjectName(u"graph")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(100)
        sizePolicy2.setHeightForWidth(self.graph.sizePolicy().hasHeightForWidth())
        self.graph.setSizePolicy(sizePolicy2)
        self.graph.setMinimumSize(QSize(0, 50))
        self.graph.setMaximumSize(QSize(16777215, 300))

        self.verticalLayout_2.addWidget(self.graph)

        self.verticalSpacer = QSpacerItem(20, 1, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)


        self.verticalLayout.addWidget(self.groupBox_3)


        self.retranslateUi(IMUSettingsWidget)

        QMetaObject.connectSlotsByName(IMUSettingsWidget)
    # setupUi

    def retranslateUi(self, IMUSettingsWidget):
        IMUSettingsWidget.setWindowTitle(QCoreApplication.translate("IMUSettingsWidget", u"Form", None))
        self.groupBox.setTitle(QCoreApplication.translate("IMUSettingsWidget", u"Movement", None))
        self.label.setText(QCoreApplication.translate("IMUSettingsWidget", u"Device amplitude [cm]", None))
        self.label_2.setText(QCoreApplication.translate("IMUSettingsWidget", u"Alpha amplitude", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("IMUSettingsWidget", u"Velocity", None))
        self.label_3.setText(QCoreApplication.translate("IMUSettingsWidget", u"Device speed [cm/s]", None))
#if QT_CONFIG(tooltip)
        self.label_4.setToolTip(QCoreApplication.translate("IMUSettingsWidget", u"positive: increase when moving\n"
"negative: decrease when moving", None))
#endif // QT_CONFIG(tooltip)
        self.label_4.setText(QCoreApplication.translate("IMUSettingsWidget", u"Intensity increase [%] (?)", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("IMUSettingsWidget", u"Live update", None))
        self.checkBox.setText(QCoreApplication.translate("IMUSettingsWidget", u"update", None))
    # retranslateUi

