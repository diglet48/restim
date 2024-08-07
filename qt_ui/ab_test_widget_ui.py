# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\designer\abtestwidget.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ABTestWidget(object):
    def setupUi(self, ABTestWidget):
        ABTestWidget.setObjectName("ABTestWidget")
        ABTestWidget.resize(566, 397)
        self.verticalLayout = QtWidgets.QVBoxLayout(ABTestWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(ABTestWidget)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.b_volume = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.b_volume.setMaximum(100.0)
        self.b_volume.setSingleStep(0.1)
        self.b_volume.setProperty("value", 99.99)
        self.b_volume.setObjectName("b_volume")
        self.gridLayout.addWidget(self.b_volume, 1, 2, 1, 1)
        self.b_signal_label = QtWidgets.QLabel(self.groupBox)
        self.b_signal_label.setAlignment(QtCore.Qt.AlignCenter)
        self.b_signal_label.setObjectName("b_signal_label")
        self.gridLayout.addWidget(self.b_signal_label, 0, 2, 1, 1)
        self.b_carrier = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.b_carrier.setMinimum(1.0)
        self.b_carrier.setMaximum(9999999.0)
        self.b_carrier.setSingleStep(10.0)
        self.b_carrier.setObjectName("b_carrier")
        self.gridLayout.addWidget(self.b_carrier, 3, 2, 1, 1)
        self.label_10 = QtWidgets.QLabel(self.groupBox)
        self.label_10.setObjectName("label_10")
        self.gridLayout.addWidget(self.label_10, 9, 0, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 3, 0, 1, 1)
        self.a_volume = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.a_volume.setMaximum(100.0)
        self.a_volume.setSingleStep(0.1)
        self.a_volume.setProperty("value", 100.0)
        self.a_volume.setObjectName("a_volume")
        self.gridLayout.addWidget(self.a_volume, 1, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.groupBox)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 4, 0, 1, 1)
        self.b_pulse_width = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.b_pulse_width.setSingleStep(0.1)
        self.b_pulse_width.setObjectName("b_pulse_width")
        self.gridLayout.addWidget(self.b_pulse_width, 5, 2, 1, 1)
        self.a_rise_time = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.a_rise_time.setMaximum(100.0)
        self.a_rise_time.setSingleStep(0.1)
        self.a_rise_time.setObjectName("a_rise_time")
        self.gridLayout.addWidget(self.a_rise_time, 7, 1, 1, 1)
        self.b_rise_time = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.b_rise_time.setMaximum(100.0)
        self.b_rise_time.setSingleStep(0.1)
        self.b_rise_time.setObjectName("b_rise_time")
        self.gridLayout.addWidget(self.b_rise_time, 7, 2, 1, 1)
        self.a_pulse_width = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.a_pulse_width.setSingleStep(0.1)
        self.a_pulse_width.setObjectName("a_pulse_width")
        self.gridLayout.addWidget(self.a_pulse_width, 5, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.label_9 = QtWidgets.QLabel(self.groupBox)
        self.label_9.setObjectName("label_9")
        self.gridLayout.addWidget(self.label_9, 7, 0, 1, 1)
        self.a_duty_cycle = QtWidgets.QLabel(self.groupBox)
        self.a_duty_cycle.setObjectName("a_duty_cycle")
        self.gridLayout.addWidget(self.a_duty_cycle, 9, 1, 1, 1)
        self.b_duty_cycle = QtWidgets.QLabel(self.groupBox)
        self.b_duty_cycle.setObjectName("b_duty_cycle")
        self.gridLayout.addWidget(self.b_duty_cycle, 9, 2, 1, 1)
        self.a_carrier = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.a_carrier.setMinimum(1.0)
        self.a_carrier.setMaximum(9999999.0)
        self.a_carrier.setSingleStep(10.0)
        self.a_carrier.setObjectName("a_carrier")
        self.gridLayout.addWidget(self.a_carrier, 3, 1, 1, 1)
        self.b_pulse_frequency = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.b_pulse_frequency.setObjectName("b_pulse_frequency")
        self.gridLayout.addWidget(self.b_pulse_frequency, 4, 2, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.groupBox)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 5, 0, 1, 1)
        self.a_signal_label = QtWidgets.QLabel(self.groupBox)
        self.a_signal_label.setAlignment(QtCore.Qt.AlignCenter)
        self.a_signal_label.setObjectName("a_signal_label")
        self.gridLayout.addWidget(self.a_signal_label, 0, 1, 1, 1)
        self.a_pulse_frequency = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.a_pulse_frequency.setObjectName("a_pulse_frequency")
        self.gridLayout.addWidget(self.a_pulse_frequency, 4, 1, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.groupBox)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 8, 0, 1, 1)
        self.a_pulse_interval_random = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.a_pulse_interval_random.setMaximum(100.0)
        self.a_pulse_interval_random.setObjectName("a_pulse_interval_random")
        self.gridLayout.addWidget(self.a_pulse_interval_random, 8, 1, 1, 1)
        self.b_pulse_interval_random = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.b_pulse_interval_random.setMaximum(100.0)
        self.b_pulse_interval_random.setObjectName("b_pulse_interval_random")
        self.gridLayout.addWidget(self.b_pulse_interval_random, 8, 2, 1, 1)
        self.a_train_duration = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.a_train_duration.setMaximum(100.0)
        self.a_train_duration.setSingleStep(0.1)
        self.a_train_duration.setObjectName("a_train_duration")
        self.gridLayout.addWidget(self.a_train_duration, 2, 1, 1, 1)
        self.b_train_duration = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.b_train_duration.setMaximum(100.0)
        self.b_train_duration.setSingleStep(0.1)
        self.b_train_duration.setObjectName("b_train_duration")
        self.gridLayout.addWidget(self.b_train_duration, 2, 2, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(ABTestWidget)
        QtCore.QMetaObject.connectSlotsByName(ABTestWidget)
        ABTestWidget.setTabOrder(self.a_volume, self.b_volume)
        ABTestWidget.setTabOrder(self.b_volume, self.a_train_duration)
        ABTestWidget.setTabOrder(self.a_train_duration, self.b_train_duration)
        ABTestWidget.setTabOrder(self.b_train_duration, self.a_carrier)
        ABTestWidget.setTabOrder(self.a_carrier, self.b_carrier)
        ABTestWidget.setTabOrder(self.b_carrier, self.a_pulse_frequency)
        ABTestWidget.setTabOrder(self.a_pulse_frequency, self.b_pulse_frequency)
        ABTestWidget.setTabOrder(self.b_pulse_frequency, self.a_pulse_width)
        ABTestWidget.setTabOrder(self.a_pulse_width, self.b_pulse_width)
        ABTestWidget.setTabOrder(self.b_pulse_width, self.a_rise_time)
        ABTestWidget.setTabOrder(self.a_rise_time, self.b_rise_time)

    def retranslateUi(self, ABTestWidget):
        _translate = QtCore.QCoreApplication.translate
        ABTestWidget.setWindowTitle(_translate("ABTestWidget", "Form"))
        self.groupBox.setTitle(_translate("ABTestWidget", "A/B testing"))
        self.b_signal_label.setText(_translate("ABTestWidget", "B signal"))
        self.label_10.setText(_translate("ABTestWidget", "Duty cycle"))
        self.label_5.setText(_translate("ABTestWidget", "Carrier frequency [Hz]"))
        self.label_6.setText(_translate("ABTestWidget", "Pulse frequency [Hz]"))
        self.label_3.setText(_translate("ABTestWidget", "Pulse train duration [s]"))
        self.label.setText(_translate("ABTestWidget", "Volume [%]"))
        self.label_9.setText(_translate("ABTestWidget", "Pulse rise time [carrier cycles]"))
        self.a_duty_cycle.setText(_translate("ABTestWidget", "TextLabel"))
        self.b_duty_cycle.setText(_translate("ABTestWidget", "TextLabel"))
        self.label_7.setText(_translate("ABTestWidget", "Pulse width [carrier cycles]"))
        self.a_signal_label.setText(_translate("ABTestWidget", "A signal"))
        self.label_8.setText(_translate("ABTestWidget", "Pulse interval random [%]"))
