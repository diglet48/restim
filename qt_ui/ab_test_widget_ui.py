# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'abtestwidget.ui'
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
from PySide6.QtWidgets import (QApplication, QDoubleSpinBox, QGridLayout, QGroupBox,
    QLabel, QSizePolicy, QSpacerItem, QVBoxLayout,
    QWidget)

class Ui_ABTestWidget(object):
    def setupUi(self, ABTestWidget):
        if not ABTestWidget.objectName():
            ABTestWidget.setObjectName(u"ABTestWidget")
        ABTestWidget.resize(566, 397)
        self.verticalLayout = QVBoxLayout(ABTestWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(ABTestWidget)
        self.groupBox.setObjectName(u"groupBox")
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(u"gridLayout")
        self.b_volume = QDoubleSpinBox(self.groupBox)
        self.b_volume.setObjectName(u"b_volume")
        self.b_volume.setKeyboardTracking(False)
        self.b_volume.setMaximum(100.000000000000000)
        self.b_volume.setSingleStep(0.100000000000000)
        self.b_volume.setValue(99.989999999999995)

        self.gridLayout.addWidget(self.b_volume, 1, 2, 1, 1)

        self.b_signal_label = QLabel(self.groupBox)
        self.b_signal_label.setObjectName(u"b_signal_label")
        self.b_signal_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.b_signal_label, 0, 2, 1, 1)

        self.b_carrier = QDoubleSpinBox(self.groupBox)
        self.b_carrier.setObjectName(u"b_carrier")
        self.b_carrier.setKeyboardTracking(False)
        self.b_carrier.setMinimum(1.000000000000000)
        self.b_carrier.setMaximum(9999999.000000000000000)
        self.b_carrier.setSingleStep(10.000000000000000)

        self.gridLayout.addWidget(self.b_carrier, 3, 2, 1, 1)

        self.label_10 = QLabel(self.groupBox)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout.addWidget(self.label_10, 9, 0, 1, 1)

        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 3, 0, 1, 1)

        self.a_volume = QDoubleSpinBox(self.groupBox)
        self.a_volume.setObjectName(u"a_volume")
        self.a_volume.setKeyboardTracking(False)
        self.a_volume.setMaximum(100.000000000000000)
        self.a_volume.setSingleStep(0.100000000000000)
        self.a_volume.setValue(100.000000000000000)

        self.gridLayout.addWidget(self.a_volume, 1, 1, 1, 1)

        self.label_6 = QLabel(self.groupBox)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout.addWidget(self.label_6, 4, 0, 1, 1)

        self.b_pulse_width = QDoubleSpinBox(self.groupBox)
        self.b_pulse_width.setObjectName(u"b_pulse_width")
        self.b_pulse_width.setKeyboardTracking(False)
        self.b_pulse_width.setSingleStep(0.100000000000000)

        self.gridLayout.addWidget(self.b_pulse_width, 5, 2, 1, 1)

        self.a_rise_time = QDoubleSpinBox(self.groupBox)
        self.a_rise_time.setObjectName(u"a_rise_time")
        self.a_rise_time.setKeyboardTracking(False)
        self.a_rise_time.setMaximum(100.000000000000000)
        self.a_rise_time.setSingleStep(0.100000000000000)

        self.gridLayout.addWidget(self.a_rise_time, 7, 1, 1, 1)

        self.b_rise_time = QDoubleSpinBox(self.groupBox)
        self.b_rise_time.setObjectName(u"b_rise_time")
        self.b_rise_time.setKeyboardTracking(False)
        self.b_rise_time.setMaximum(100.000000000000000)
        self.b_rise_time.setSingleStep(0.100000000000000)

        self.gridLayout.addWidget(self.b_rise_time, 7, 2, 1, 1)

        self.a_pulse_width = QDoubleSpinBox(self.groupBox)
        self.a_pulse_width.setObjectName(u"a_pulse_width")
        self.a_pulse_width.setKeyboardTracking(False)
        self.a_pulse_width.setSingleStep(0.100000000000000)

        self.gridLayout.addWidget(self.a_pulse_width, 5, 1, 1, 1)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)

        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)

        self.label_9 = QLabel(self.groupBox)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout.addWidget(self.label_9, 7, 0, 1, 1)

        self.a_duty_cycle = QLabel(self.groupBox)
        self.a_duty_cycle.setObjectName(u"a_duty_cycle")

        self.gridLayout.addWidget(self.a_duty_cycle, 9, 1, 1, 1)

        self.b_duty_cycle = QLabel(self.groupBox)
        self.b_duty_cycle.setObjectName(u"b_duty_cycle")

        self.gridLayout.addWidget(self.b_duty_cycle, 9, 2, 1, 1)

        self.a_carrier = QDoubleSpinBox(self.groupBox)
        self.a_carrier.setObjectName(u"a_carrier")
        self.a_carrier.setKeyboardTracking(False)
        self.a_carrier.setMinimum(1.000000000000000)
        self.a_carrier.setMaximum(9999999.000000000000000)
        self.a_carrier.setSingleStep(10.000000000000000)

        self.gridLayout.addWidget(self.a_carrier, 3, 1, 1, 1)

        self.b_pulse_frequency = QDoubleSpinBox(self.groupBox)
        self.b_pulse_frequency.setObjectName(u"b_pulse_frequency")
        self.b_pulse_frequency.setKeyboardTracking(False)

        self.gridLayout.addWidget(self.b_pulse_frequency, 4, 2, 1, 1)

        self.label_7 = QLabel(self.groupBox)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout.addWidget(self.label_7, 5, 0, 1, 1)

        self.a_signal_label = QLabel(self.groupBox)
        self.a_signal_label.setObjectName(u"a_signal_label")
        self.a_signal_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.a_signal_label, 0, 1, 1, 1)

        self.a_pulse_frequency = QDoubleSpinBox(self.groupBox)
        self.a_pulse_frequency.setObjectName(u"a_pulse_frequency")
        self.a_pulse_frequency.setKeyboardTracking(False)

        self.gridLayout.addWidget(self.a_pulse_frequency, 4, 1, 1, 1)

        self.label_8 = QLabel(self.groupBox)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout.addWidget(self.label_8, 8, 0, 1, 1)

        self.a_pulse_interval_random = QDoubleSpinBox(self.groupBox)
        self.a_pulse_interval_random.setObjectName(u"a_pulse_interval_random")
        self.a_pulse_interval_random.setKeyboardTracking(False)
        self.a_pulse_interval_random.setMaximum(100.000000000000000)

        self.gridLayout.addWidget(self.a_pulse_interval_random, 8, 1, 1, 1)

        self.b_pulse_interval_random = QDoubleSpinBox(self.groupBox)
        self.b_pulse_interval_random.setObjectName(u"b_pulse_interval_random")
        self.b_pulse_interval_random.setKeyboardTracking(False)
        self.b_pulse_interval_random.setMaximum(100.000000000000000)

        self.gridLayout.addWidget(self.b_pulse_interval_random, 8, 2, 1, 1)

        self.a_train_duration = QDoubleSpinBox(self.groupBox)
        self.a_train_duration.setObjectName(u"a_train_duration")
        self.a_train_duration.setKeyboardTracking(False)
        self.a_train_duration.setMaximum(100.000000000000000)
        self.a_train_duration.setSingleStep(0.100000000000000)

        self.gridLayout.addWidget(self.a_train_duration, 2, 1, 1, 1)

        self.b_train_duration = QDoubleSpinBox(self.groupBox)
        self.b_train_duration.setObjectName(u"b_train_duration")
        self.b_train_duration.setKeyboardTracking(False)
        self.b_train_duration.setMaximum(100.000000000000000)
        self.b_train_duration.setSingleStep(0.100000000000000)

        self.gridLayout.addWidget(self.b_train_duration, 2, 2, 1, 1)


        self.verticalLayout.addWidget(self.groupBox)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        QWidget.setTabOrder(self.a_volume, self.b_volume)
        QWidget.setTabOrder(self.b_volume, self.a_train_duration)
        QWidget.setTabOrder(self.a_train_duration, self.b_train_duration)
        QWidget.setTabOrder(self.b_train_duration, self.a_carrier)
        QWidget.setTabOrder(self.a_carrier, self.b_carrier)
        QWidget.setTabOrder(self.b_carrier, self.a_pulse_frequency)
        QWidget.setTabOrder(self.a_pulse_frequency, self.b_pulse_frequency)
        QWidget.setTabOrder(self.b_pulse_frequency, self.a_pulse_width)
        QWidget.setTabOrder(self.a_pulse_width, self.b_pulse_width)
        QWidget.setTabOrder(self.b_pulse_width, self.a_rise_time)
        QWidget.setTabOrder(self.a_rise_time, self.b_rise_time)

        self.retranslateUi(ABTestWidget)

        QMetaObject.connectSlotsByName(ABTestWidget)
    # setupUi

    def retranslateUi(self, ABTestWidget):
        ABTestWidget.setWindowTitle(QCoreApplication.translate("ABTestWidget", u"Form", None))
        self.groupBox.setTitle(QCoreApplication.translate("ABTestWidget", u"A/B testing", None))
        self.b_signal_label.setText(QCoreApplication.translate("ABTestWidget", u"B signal", None))
        self.label_10.setText(QCoreApplication.translate("ABTestWidget", u"Duty cycle", None))
        self.label_5.setText(QCoreApplication.translate("ABTestWidget", u"Carrier frequency [Hz]", None))
        self.label_6.setText(QCoreApplication.translate("ABTestWidget", u"Pulse frequency [Hz]", None))
        self.label_3.setText(QCoreApplication.translate("ABTestWidget", u"Pulse train duration [s]", None))
        self.label.setText(QCoreApplication.translate("ABTestWidget", u"Volume [%]", None))
        self.label_9.setText(QCoreApplication.translate("ABTestWidget", u"Pulse rise time [carrier cycles]", None))
        self.a_duty_cycle.setText(QCoreApplication.translate("ABTestWidget", u"TextLabel", None))
        self.b_duty_cycle.setText(QCoreApplication.translate("ABTestWidget", u"TextLabel", None))
        self.label_7.setText(QCoreApplication.translate("ABTestWidget", u"Pulse width [carrier cycles]", None))
        self.a_signal_label.setText(QCoreApplication.translate("ABTestWidget", u"A signal", None))
        self.label_8.setText(QCoreApplication.translate("ABTestWidget", u"Pulse interval random [%]", None))
    # retranslateUi

