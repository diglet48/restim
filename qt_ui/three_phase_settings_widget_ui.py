# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'threephasesettingswidget.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QFormLayout, QGroupBox, QLabel, QPushButton,
    QSizePolicy, QSpacerItem, QStackedWidget, QVBoxLayout,
    QWidget)

from qt_ui.widgets.phase_widget import PhaseWidgetCalibration

class Ui_ThreePhaseSettingsWidget(object):
    def setupUi(self, ThreePhaseSettingsWidget):
        if not ThreePhaseSettingsWidget.objectName():
            ThreePhaseSettingsWidget.setObjectName(u"ThreePhaseSettingsWidget")
        ThreePhaseSettingsWidget.resize(592, 660)
        self.verticalLayout = QVBoxLayout(ThreePhaseSettingsWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(ThreePhaseSettingsWidget)
        self.groupBox.setObjectName(u"groupBox")
        self.formLayout = QFormLayout(self.groupBox)
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_2)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_3)

        self.neutral = QDoubleSpinBox(self.groupBox)
        self.neutral.setObjectName(u"neutral")
        self.neutral.setMinimum(-15.000000000000000)
        self.neutral.setMaximum(15.000000000000000)
        self.neutral.setSingleStep(0.100000000000000)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.neutral)

        self.right = QDoubleSpinBox(self.groupBox)
        self.right.setObjectName(u"right")
        self.right.setMinimum(-15.000000000000000)
        self.right.setMaximum(15.000000000000000)
        self.right.setSingleStep(0.100000000000000)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.right)

        self.center = QDoubleSpinBox(self.groupBox)
        self.center.setObjectName(u"center")
        self.center.setMinimum(-15.000000000000000)
        self.center.setMaximum(15.000000000000000)
        self.center.setSingleStep(0.100000000000000)

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.center)

        self.phase_widget_calibration = PhaseWidgetCalibration(self.groupBox)
        self.phase_widget_calibration.setObjectName(u"phase_widget_calibration")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.phase_widget_calibration)

        self.label_10 = QLabel(self.groupBox)
        self.label_10.setObjectName(u"label_10")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label_10)


        self.verticalLayout.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(ThreePhaseSettingsWidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.groupBox_2.setCheckable(True)
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.combobox_type = QComboBox(self.groupBox_2)
        self.combobox_type.addItem("")
        self.combobox_type.addItem("")
        self.combobox_type.setObjectName(u"combobox_type")

        self.verticalLayout_2.addWidget(self.combobox_type)

        self.stackedWidget = QStackedWidget(self.groupBox_2)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.formLayout_4 = QFormLayout(self.page)
        self.formLayout_4.setObjectName(u"formLayout_4")
        self.label_4 = QLabel(self.page)
        self.label_4.setObjectName(u"label_4")

        self.formLayout_4.setWidget(1, QFormLayout.LabelRole, self.label_4)

        self.rotation = QDoubleSpinBox(self.page)
        self.rotation.setObjectName(u"rotation")
        self.rotation.setDecimals(0)
        self.rotation.setMinimum(-360.000000000000000)
        self.rotation.setMaximum(360.000000000000000)
        self.rotation.setSingleStep(10.000000000000000)

        self.formLayout_4.setWidget(1, QFormLayout.FieldRole, self.rotation)

        self.label_5 = QLabel(self.page)
        self.label_5.setObjectName(u"label_5")

        self.formLayout_4.setWidget(2, QFormLayout.LabelRole, self.label_5)

        self.mirror = QCheckBox(self.page)
        self.mirror.setObjectName(u"mirror")

        self.formLayout_4.setWidget(2, QFormLayout.FieldRole, self.mirror)

        self.label_6 = QLabel(self.page)
        self.label_6.setObjectName(u"label_6")

        self.formLayout_4.setWidget(3, QFormLayout.LabelRole, self.label_6)

        self.limit_top = QDoubleSpinBox(self.page)
        self.limit_top.setObjectName(u"limit_top")
        self.limit_top.setMinimum(-1.000000000000000)
        self.limit_top.setMaximum(1.000000000000000)
        self.limit_top.setSingleStep(0.100000000000000)
        self.limit_top.setValue(1.000000000000000)

        self.formLayout_4.setWidget(3, QFormLayout.FieldRole, self.limit_top)

        self.label_7 = QLabel(self.page)
        self.label_7.setObjectName(u"label_7")

        self.formLayout_4.setWidget(4, QFormLayout.LabelRole, self.label_7)

        self.limit_bottom = QDoubleSpinBox(self.page)
        self.limit_bottom.setObjectName(u"limit_bottom")
        self.limit_bottom.setMinimum(-1.000000000000000)
        self.limit_bottom.setMaximum(1.000000000000000)
        self.limit_bottom.setSingleStep(0.100000000000000)
        self.limit_bottom.setValue(-1.000000000000000)

        self.formLayout_4.setWidget(4, QFormLayout.FieldRole, self.limit_bottom)

        self.label_8 = QLabel(self.page)
        self.label_8.setObjectName(u"label_8")

        self.formLayout_4.setWidget(5, QFormLayout.LabelRole, self.label_8)

        self.limit_left = QDoubleSpinBox(self.page)
        self.limit_left.setObjectName(u"limit_left")
        self.limit_left.setMinimum(-1.000000000000000)
        self.limit_left.setMaximum(1.000000000000000)
        self.limit_left.setSingleStep(0.100000000000000)
        self.limit_left.setValue(-1.000000000000000)

        self.formLayout_4.setWidget(5, QFormLayout.FieldRole, self.limit_left)

        self.label_9 = QLabel(self.page)
        self.label_9.setObjectName(u"label_9")

        self.formLayout_4.setWidget(6, QFormLayout.LabelRole, self.label_9)

        self.limit_right = QDoubleSpinBox(self.page)
        self.limit_right.setObjectName(u"limit_right")
        self.limit_right.setMinimum(-1.000000000000000)
        self.limit_right.setMaximum(1.000000000000000)
        self.limit_right.setSingleStep(0.100000000000000)
        self.limit_right.setValue(1.000000000000000)

        self.formLayout_4.setWidget(6, QFormLayout.FieldRole, self.limit_right)

        self.reset_defaults_button = QPushButton(self.page)
        self.reset_defaults_button.setObjectName(u"reset_defaults_button")

        self.formLayout_4.setWidget(7, QFormLayout.LabelRole, self.reset_defaults_button)

        self.stackedWidget.addWidget(self.page)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.formLayout_2 = QFormLayout(self.page_2)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.label_12 = QLabel(self.page_2)
        self.label_12.setObjectName(u"label_12")

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.label_12)

        self.mapToEdge_start = QDoubleSpinBox(self.page_2)
        self.mapToEdge_start.setObjectName(u"mapToEdge_start")
        self.mapToEdge_start.setMinimum(-360.000000000000000)
        self.mapToEdge_start.setMaximum(360.000000000000000)
        self.mapToEdge_start.setSingleStep(10.000000000000000)

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.mapToEdge_start)

        self.label_13 = QLabel(self.page_2)
        self.label_13.setObjectName(u"label_13")

        self.formLayout_2.setWidget(1, QFormLayout.LabelRole, self.label_13)

        self.mapToEdge_length = QDoubleSpinBox(self.page_2)
        self.mapToEdge_length.setObjectName(u"mapToEdge_length")
        self.mapToEdge_length.setMaximum(360.000000000000000)
        self.mapToEdge_length.setSingleStep(10.000000000000000)

        self.formLayout_2.setWidget(1, QFormLayout.FieldRole, self.mapToEdge_length)

        self.label_14 = QLabel(self.page_2)
        self.label_14.setObjectName(u"label_14")

        self.formLayout_2.setWidget(2, QFormLayout.LabelRole, self.label_14)

        self.mapToEdge_invert = QCheckBox(self.page_2)
        self.mapToEdge_invert.setObjectName(u"mapToEdge_invert")

        self.formLayout_2.setWidget(2, QFormLayout.FieldRole, self.mapToEdge_invert)

        self.stackedWidget.addWidget(self.page_2)

        self.verticalLayout_2.addWidget(self.stackedWidget)


        self.verticalLayout.addWidget(self.groupBox_2)

        self.groupBox_3 = QGroupBox(ThreePhaseSettingsWidget)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.formLayout_3 = QFormLayout(self.groupBox_3)
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.label_11 = QLabel(self.groupBox_3)
        self.label_11.setObjectName(u"label_11")

        self.formLayout_3.setWidget(0, QFormLayout.LabelRole, self.label_11)

        self.exponent = QDoubleSpinBox(self.groupBox_3)
        self.exponent.setObjectName(u"exponent")
        self.exponent.setMaximum(1.000000000000000)
        self.exponent.setSingleStep(0.100000000000000)

        self.formLayout_3.setWidget(0, QFormLayout.FieldRole, self.exponent)


        self.verticalLayout.addWidget(self.groupBox_3)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.retranslateUi(ThreePhaseSettingsWidget)

        self.stackedWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(ThreePhaseSettingsWidget)
    # setupUi

    def retranslateUi(self, ThreePhaseSettingsWidget):
        ThreePhaseSettingsWidget.setWindowTitle(QCoreApplication.translate("ThreePhaseSettingsWidget", u"Form", None))
        self.groupBox.setTitle(QCoreApplication.translate("ThreePhaseSettingsWidget", u"Calibration", None))
        self.label.setText(QCoreApplication.translate("ThreePhaseSettingsWidget", u"Neutral power [dB]", None))
        self.label_2.setText(QCoreApplication.translate("ThreePhaseSettingsWidget", u"Right power [dB]", None))
        self.label_3.setText(QCoreApplication.translate("ThreePhaseSettingsWidget", u"Center power [dB]", None))
        self.label_10.setText(QCoreApplication.translate("ThreePhaseSettingsWidget", u"Click to 0.1 adjust", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("ThreePhaseSettingsWidget", u"Adjust limits", None))
        self.combobox_type.setItemText(0, QCoreApplication.translate("ThreePhaseSettingsWidget", u"Scale", None))
        self.combobox_type.setItemText(1, QCoreApplication.translate("ThreePhaseSettingsWidget", u"Map to edge", None))

        self.label_4.setText(QCoreApplication.translate("ThreePhaseSettingsWidget", u"Top rotation [degrees]", None))
        self.label_5.setText(QCoreApplication.translate("ThreePhaseSettingsWidget", u"Mirror", None))
        self.mirror.setText("")
        self.label_6.setText(QCoreApplication.translate("ThreePhaseSettingsWidget", u"top limit", None))
        self.label_7.setText(QCoreApplication.translate("ThreePhaseSettingsWidget", u"bottom limit", None))
        self.label_8.setText(QCoreApplication.translate("ThreePhaseSettingsWidget", u"left limit", None))
        self.label_9.setText(QCoreApplication.translate("ThreePhaseSettingsWidget", u"right limit", None))
        self.reset_defaults_button.setText(QCoreApplication.translate("ThreePhaseSettingsWidget", u"reset defaults", None))
        self.label_12.setText(QCoreApplication.translate("ThreePhaseSettingsWidget", u"Arc start [deg]", None))
        self.label_13.setText(QCoreApplication.translate("ThreePhaseSettingsWidget", u"Arc length [deg]", None))
        self.label_14.setText(QCoreApplication.translate("ThreePhaseSettingsWidget", u"invert top/bottom", None))
        self.mapToEdge_invert.setText("")
        self.groupBox_3.setTitle(QCoreApplication.translate("ThreePhaseSettingsWidget", u"Advanced", None))
        self.label_11.setText(QCoreApplication.translate("ThreePhaseSettingsWidget", u"Exponent [0, 1]", None))
    # retranslateUi

