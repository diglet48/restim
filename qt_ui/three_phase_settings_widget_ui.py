# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'threephasesettingswidget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.3
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
    QFormLayout, QFrame, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QPushButton, QSizePolicy,
    QSpacerItem, QStackedWidget, QToolButton, QVBoxLayout,
    QWidget)

from qt_ui.widgets.spinbox_with_progress_indicator import SpinBoxWithProgressIndicator
from qt_ui.widgets.threephase_widget import ThreephaseWidgetCalibration
import restim_rc

class Ui_ThreePhaseSettingsWidget(object):
    def setupUi(self, ThreePhaseSettingsWidget):
        if not ThreePhaseSettingsWidget.objectName():
            ThreePhaseSettingsWidget.setObjectName(u"ThreePhaseSettingsWidget")
        ThreePhaseSettingsWidget.resize(725, 868)
        self.gridLayout = QGridLayout(ThreePhaseSettingsWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.groupBox_5 = QGroupBox(ThreePhaseSettingsWidget)
        self.groupBox_5.setObjectName(u"groupBox_5")
        self.formLayout_6 = QFormLayout(self.groupBox_5)
        self.formLayout_6.setObjectName(u"formLayout_6")
        self.label_19 = QLabel(self.groupBox_5)
        self.label_19.setObjectName(u"label_19")

        self.formLayout_6.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_19)

        self.comboBox_interface = QComboBox(self.groupBox_5)
        self.comboBox_interface.setObjectName(u"comboBox_interface")

        self.formLayout_6.setWidget(0, QFormLayout.ItemRole.FieldRole, self.comboBox_interface)


        self.gridLayout.addWidget(self.groupBox_5, 0, 0, 1, 1)

        self.groupBox_classic = QGroupBox(ThreePhaseSettingsWidget)
        self.groupBox_classic.setObjectName(u"groupBox_classic")
        self.formLayout = QFormLayout(self.groupBox_classic)
        self.formLayout.setObjectName(u"formLayout")
        self.stackedWidget_2 = QStackedWidget(self.groupBox_classic)
        self.stackedWidget_2.setObjectName(u"stackedWidget_2")
        self.page_3 = QWidget()
        self.page_3.setObjectName(u"page_3")
        self.formLayout_3 = QFormLayout(self.page_3)
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.formLayout_3.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.page_3)
        self.label.setObjectName(u"label")

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)

        self.neutral = QDoubleSpinBox(self.page_3)
        self.neutral.setObjectName(u"neutral")
        self.neutral.setKeyboardTracking(False)
        self.neutral.setMinimum(-15.000000000000000)
        self.neutral.setMaximum(15.000000000000000)
        self.neutral.setSingleStep(0.100000000000000)

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.FieldRole, self.neutral)

        self.label_2 = QLabel(self.page_3)
        self.label_2.setObjectName(u"label_2")

        self.formLayout_3.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.right = QDoubleSpinBox(self.page_3)
        self.right.setObjectName(u"right")
        self.right.setKeyboardTracking(False)
        self.right.setMinimum(-15.000000000000000)
        self.right.setMaximum(15.000000000000000)
        self.right.setSingleStep(0.100000000000000)

        self.formLayout_3.setWidget(1, QFormLayout.ItemRole.FieldRole, self.right)

        self.stackedWidget_2.addWidget(self.page_3)
        self.page_4 = QWidget()
        self.page_4.setObjectName(u"page_4")
        self.formLayout_4 = QFormLayout(self.page_4)
        self.formLayout_4.setObjectName(u"formLayout_4")
        self.formLayout_4.setContentsMargins(0, 0, 0, 0)
        self.label_15 = QLabel(self.page_4)
        self.label_15.setObjectName(u"label_15")

        self.formLayout_4.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_15)

        self.a_power = SpinBoxWithProgressIndicator(self.page_4)
        self.a_power.setObjectName(u"a_power")
        self.a_power.setKeyboardTracking(False)
        self.a_power.setDecimals(2)
        self.a_power.setMinimum(-100.000000000000000)
        self.a_power.setMaximum(300.000000000000000)
        self.a_power.setSingleStep(0.100000000000000)

        self.formLayout_4.setWidget(0, QFormLayout.ItemRole.FieldRole, self.a_power)

        self.label_16 = QLabel(self.page_4)
        self.label_16.setObjectName(u"label_16")

        self.formLayout_4.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_16)

        self.b_power = SpinBoxWithProgressIndicator(self.page_4)
        self.b_power.setObjectName(u"b_power")
        self.b_power.setKeyboardTracking(False)
        self.b_power.setDecimals(2)
        self.b_power.setMinimum(-100.000000000000000)
        self.b_power.setMaximum(300.000000000000000)
        self.b_power.setSingleStep(0.100000000000000)

        self.formLayout_4.setWidget(1, QFormLayout.ItemRole.FieldRole, self.b_power)

        self.label_17 = QLabel(self.page_4)
        self.label_17.setObjectName(u"label_17")

        self.formLayout_4.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_17)

        self.c_power = SpinBoxWithProgressIndicator(self.page_4)
        self.c_power.setObjectName(u"c_power")
        self.c_power.setKeyboardTracking(False)
        self.c_power.setDecimals(2)
        self.c_power.setMinimum(-100.000000000000000)
        self.c_power.setMaximum(300.000000000000000)
        self.c_power.setSingleStep(0.100000000000000)

        self.formLayout_4.setWidget(2, QFormLayout.ItemRole.FieldRole, self.c_power)

        self.stackedWidget_2.addWidget(self.page_4)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.SpanningRole, self.stackedWidget_2)

        self.line = QFrame(self.groupBox_classic)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.SpanningRole, self.line)

        self.label_18 = QLabel(self.groupBox_classic)
        self.label_18.setObjectName(u"label_18")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_18)

        self.widget = QWidget(self.groupBox_classic)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.center_reduction = SpinBoxWithProgressIndicator(self.widget)
        self.center_reduction.setObjectName(u"center_reduction")
        self.center_reduction.setKeyboardTracking(False)
        self.center_reduction.setDecimals(1)
        self.center_reduction.setMinimum(0.000000000000000)
        self.center_reduction.setMaximum(20.000000000000000)

        self.horizontalLayout.addWidget(self.center_reduction)

        self.center_reduction_reset = QToolButton(self.widget)
        self.center_reduction_reset.setObjectName(u"center_reduction_reset")
        icon = QIcon()
        icon.addFile(u":/restim/arrow-round_poly.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.center_reduction_reset.setIcon(icon)

        self.horizontalLayout.addWidget(self.center_reduction_reset)


        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.widget)

        self.label_10 = QLabel(self.groupBox_classic)
        self.label_10.setObjectName(u"label_10")

        self.formLayout.setWidget(4, QFormLayout.ItemRole.LabelRole, self.label_10)

        self.phase_widget_calibration = ThreephaseWidgetCalibration(self.groupBox_classic)
        self.phase_widget_calibration.setObjectName(u"phase_widget_calibration")

        self.formLayout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.phase_widget_calibration)


        self.gridLayout.addWidget(self.groupBox_classic, 1, 0, 1, 1)

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
        self.gridLayout_2 = QGridLayout(self.page)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.reset_defaults_button = QPushButton(self.page)
        self.reset_defaults_button.setObjectName(u"reset_defaults_button")

        self.gridLayout_2.addWidget(self.reset_defaults_button, 3, 0, 1, 3)

        self.limit_right = QDoubleSpinBox(self.page)
        self.limit_right.setObjectName(u"limit_right")
        self.limit_right.setKeyboardTracking(False)
        self.limit_right.setMinimum(-1.000000000000000)
        self.limit_right.setMaximum(1.000000000000000)
        self.limit_right.setSingleStep(0.100000000000000)
        self.limit_right.setValue(1.000000000000000)

        self.gridLayout_2.addWidget(self.limit_right, 2, 2, 1, 1)

        self.mirror = QCheckBox(self.page)
        self.mirror.setObjectName(u"mirror")

        self.gridLayout_2.addWidget(self.mirror, 0, 2, 1, 1)

        self.limit_bottom = QDoubleSpinBox(self.page)
        self.limit_bottom.setObjectName(u"limit_bottom")
        self.limit_bottom.setKeyboardTracking(False)
        self.limit_bottom.setMinimum(-1.000000000000000)
        self.limit_bottom.setMaximum(1.000000000000000)
        self.limit_bottom.setSingleStep(0.100000000000000)
        self.limit_bottom.setValue(-1.000000000000000)

        self.gridLayout_2.addWidget(self.limit_bottom, 1, 2, 1, 1)

        self.limit_left = QDoubleSpinBox(self.page)
        self.limit_left.setObjectName(u"limit_left")
        self.limit_left.setKeyboardTracking(False)
        self.limit_left.setMinimum(-1.000000000000000)
        self.limit_left.setMaximum(1.000000000000000)
        self.limit_left.setSingleStep(0.100000000000000)
        self.limit_left.setValue(-1.000000000000000)

        self.gridLayout_2.addWidget(self.limit_left, 2, 1, 1, 1)

        self.label_6 = QLabel(self.page)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_2.addWidget(self.label_6, 1, 0, 1, 1)

        self.limit_top = QDoubleSpinBox(self.page)
        self.limit_top.setObjectName(u"limit_top")
        self.limit_top.setKeyboardTracking(False)
        self.limit_top.setMinimum(-1.000000000000000)
        self.limit_top.setMaximum(1.000000000000000)
        self.limit_top.setSingleStep(0.100000000000000)
        self.limit_top.setValue(1.000000000000000)

        self.gridLayout_2.addWidget(self.limit_top, 1, 1, 1, 1)

        self.label_4 = QLabel(self.page)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_2.addWidget(self.label_4, 0, 0, 1, 1)

        self.label_8 = QLabel(self.page)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_2.addWidget(self.label_8, 2, 0, 1, 1)

        self.rotation = QDoubleSpinBox(self.page)
        self.rotation.setObjectName(u"rotation")
        self.rotation.setKeyboardTracking(False)
        self.rotation.setDecimals(0)
        self.rotation.setMinimum(-360.000000000000000)
        self.rotation.setMaximum(360.000000000000000)
        self.rotation.setSingleStep(10.000000000000000)

        self.gridLayout_2.addWidget(self.rotation, 0, 1, 1, 1)

        self.stackedWidget.addWidget(self.page)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.formLayout_2 = QFormLayout(self.page_2)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.formLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label_12 = QLabel(self.page_2)
        self.label_12.setObjectName(u"label_12")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_12)

        self.mapToEdge_start = QDoubleSpinBox(self.page_2)
        self.mapToEdge_start.setObjectName(u"mapToEdge_start")
        self.mapToEdge_start.setKeyboardTracking(False)
        self.mapToEdge_start.setMinimum(-360.000000000000000)
        self.mapToEdge_start.setMaximum(360.000000000000000)
        self.mapToEdge_start.setSingleStep(10.000000000000000)

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.mapToEdge_start)

        self.label_13 = QLabel(self.page_2)
        self.label_13.setObjectName(u"label_13")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_13)

        self.mapToEdge_length = QDoubleSpinBox(self.page_2)
        self.mapToEdge_length.setObjectName(u"mapToEdge_length")
        self.mapToEdge_length.setKeyboardTracking(False)
        self.mapToEdge_length.setMaximum(360.000000000000000)
        self.mapToEdge_length.setSingleStep(10.000000000000000)

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.mapToEdge_length)

        self.label_14 = QLabel(self.page_2)
        self.label_14.setObjectName(u"label_14")

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_14)

        self.mapToEdge_invert = QCheckBox(self.page_2)
        self.mapToEdge_invert.setObjectName(u"mapToEdge_invert")

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.FieldRole, self.mapToEdge_invert)

        self.stackedWidget.addWidget(self.page_2)

        self.verticalLayout_2.addWidget(self.stackedWidget)


        self.gridLayout.addWidget(self.groupBox_2, 2, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 3, 0, 1, 1)


        self.retranslateUi(ThreePhaseSettingsWidget)

        self.stackedWidget_2.setCurrentIndex(1)
        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(ThreePhaseSettingsWidget)
    # setupUi

    def retranslateUi(self, ThreePhaseSettingsWidget):
        ThreePhaseSettingsWidget.setWindowTitle(QCoreApplication.translate("ThreePhaseSettingsWidget", u"Form", None))
        self.groupBox_5.setTitle("")
        self.label_19.setText(QCoreApplication.translate("ThreePhaseSettingsWidget", u"Interface", None))
        self.groupBox_classic.setTitle(QCoreApplication.translate("ThreePhaseSettingsWidget", u"Calibration", None))
        self.label.setText(QCoreApplication.translate("ThreePhaseSettingsWidget", u"<html><head/><body><p>Neutral power [dB] </p></body></html>", None))
        self.label_2.setText(QCoreApplication.translate("ThreePhaseSettingsWidget", u"Right power [dB]", None))
        self.label_15.setText(QCoreApplication.translate("ThreePhaseSettingsWidget", u"A power [dB]", None))
        self.label_16.setText(QCoreApplication.translate("ThreePhaseSettingsWidget", u"B power [dB]", None))
        self.label_17.setText(QCoreApplication.translate("ThreePhaseSettingsWidget", u"C power [dB]", None))
        self.label_18.setText(QCoreApplication.translate("ThreePhaseSettingsWidget", u"Center reduction [%]", None))
        self.center_reduction_reset.setText(QCoreApplication.translate("ThreePhaseSettingsWidget", u"...", None))
        self.label_10.setText(QCoreApplication.translate("ThreePhaseSettingsWidget", u"Click to 0.1 adjust", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("ThreePhaseSettingsWidget", u"Adjust limits", None))
        self.combobox_type.setItemText(0, QCoreApplication.translate("ThreePhaseSettingsWidget", u"Scale", None))
        self.combobox_type.setItemText(1, QCoreApplication.translate("ThreePhaseSettingsWidget", u"Map to edge", None))

        self.reset_defaults_button.setText(QCoreApplication.translate("ThreePhaseSettingsWidget", u"reset defaults", None))
        self.mirror.setText(QCoreApplication.translate("ThreePhaseSettingsWidget", u"Mirror", None))
        self.label_6.setText(QCoreApplication.translate("ThreePhaseSettingsWidget", u"Limits top, bottom", None))
        self.label_4.setText(QCoreApplication.translate("ThreePhaseSettingsWidget", u"Top rotation [degrees]", None))
        self.label_8.setText(QCoreApplication.translate("ThreePhaseSettingsWidget", u"Limits left, right", None))
        self.label_12.setText(QCoreApplication.translate("ThreePhaseSettingsWidget", u"Arc start [deg]", None))
        self.label_13.setText(QCoreApplication.translate("ThreePhaseSettingsWidget", u"Arc length [deg]", None))
        self.label_14.setText(QCoreApplication.translate("ThreePhaseSettingsWidget", u"invert top/bottom", None))
        self.mapToEdge_invert.setText("")
    # retranslateUi

