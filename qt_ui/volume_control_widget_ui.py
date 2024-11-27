# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\designer\volumecontrolwidget.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_VolumeControlForm(object):
    def setupUi(self, VolumeControlForm):
        VolumeControlForm.setObjectName("VolumeControlForm")
        VolumeControlForm.resize(556, 450)
        self.verticalLayout = QtWidgets.QVBoxLayout(VolumeControlForm)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(VolumeControlForm)
        self.groupBox.setObjectName("groupBox")
        self.formLayout_2 = QtWidgets.QFormLayout(self.groupBox)
        self.formLayout_2.setObjectName("formLayout_2")
        self.label_volume = QtWidgets.QLabel(self.groupBox)
        self.label_volume.setObjectName("label_volume")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_volume)
        self.doubleSpinBox_volume = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.doubleSpinBox_volume.setDecimals(2)
        self.doubleSpinBox_volume.setMaximum(100.0)
        self.doubleSpinBox_volume.setSingleStep(0.1)
        self.doubleSpinBox_volume.setObjectName("doubleSpinBox_volume")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.doubleSpinBox_volume)
        self.label_target_volume = QtWidgets.QLabel(self.groupBox)
        self.label_target_volume.setObjectName("label_target_volume")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_target_volume)
        self.doubleSpinBox_target_volume = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.doubleSpinBox_target_volume.setMaximum(100.0)
        self.doubleSpinBox_target_volume.setSingleStep(0.1)
        self.doubleSpinBox_target_volume.setProperty("value", 100.0)
        self.doubleSpinBox_target_volume.setObjectName("doubleSpinBox_target_volume")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.doubleSpinBox_target_volume)
        self.label_rate = QtWidgets.QLabel(self.groupBox)
        self.label_rate.setObjectName("label_rate")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_rate)
        self.doubleSpinBox_rate = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.doubleSpinBox_rate.setMaximum(10000.0)
        self.doubleSpinBox_rate.setSingleStep(0.1)
        self.doubleSpinBox_rate.setProperty("value", 1.0)
        self.doubleSpinBox_rate.setObjectName("doubleSpinBox_rate")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.doubleSpinBox_rate)
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label)
        self.checkBox_ramp_enabled = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_ramp_enabled.setText("")
        self.checkBox_ramp_enabled.setObjectName("checkBox_ramp_enabled")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.checkBox_ramp_enabled)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(VolumeControlForm)
        self.groupBox_2.setObjectName("groupBox_2")
        self.formLayout = QtWidgets.QFormLayout(self.groupBox_2)
        self.formLayout.setObjectName("formLayout")
        self.label_2 = QtWidgets.QLabel(self.groupBox_2)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.doubleSpinBox_inactivity_threshold = QtWidgets.QDoubleSpinBox(self.groupBox_2)
        self.doubleSpinBox_inactivity_threshold.setMaximum(100.0)
        self.doubleSpinBox_inactivity_threshold.setSingleStep(0.1)
        self.doubleSpinBox_inactivity_threshold.setObjectName("doubleSpinBox_inactivity_threshold")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.doubleSpinBox_inactivity_threshold)
        self.label_3 = QtWidgets.QLabel(self.groupBox_2)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.doubleSpinBox_inactivity_volume = QtWidgets.QDoubleSpinBox(self.groupBox_2)
        self.doubleSpinBox_inactivity_volume.setMaximum(100.0)
        self.doubleSpinBox_inactivity_volume.setSingleStep(0.1)
        self.doubleSpinBox_inactivity_volume.setObjectName("doubleSpinBox_inactivity_volume")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.doubleSpinBox_inactivity_volume)
        self.label_4 = QtWidgets.QLabel(self.groupBox_2)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.doubleSpinBox_inactivity_ramp_time = QtWidgets.QDoubleSpinBox(self.groupBox_2)
        self.doubleSpinBox_inactivity_ramp_time.setMaximum(100.0)
        self.doubleSpinBox_inactivity_ramp_time.setSingleStep(0.1)
        self.doubleSpinBox_inactivity_ramp_time.setObjectName("doubleSpinBox_inactivity_ramp_time")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.doubleSpinBox_inactivity_ramp_time)
        self.verticalLayout.addWidget(self.groupBox_2)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(VolumeControlForm)
        QtCore.QMetaObject.connectSlotsByName(VolumeControlForm)
        VolumeControlForm.setTabOrder(self.doubleSpinBox_volume, self.doubleSpinBox_target_volume)
        VolumeControlForm.setTabOrder(self.doubleSpinBox_target_volume, self.doubleSpinBox_rate)
        VolumeControlForm.setTabOrder(self.doubleSpinBox_rate, self.checkBox_ramp_enabled)
        VolumeControlForm.setTabOrder(self.checkBox_ramp_enabled, self.doubleSpinBox_inactivity_threshold)
        VolumeControlForm.setTabOrder(self.doubleSpinBox_inactivity_threshold, self.doubleSpinBox_inactivity_ramp_time)
        VolumeControlForm.setTabOrder(self.doubleSpinBox_inactivity_ramp_time, self.doubleSpinBox_inactivity_volume)

    def retranslateUi(self, VolumeControlForm):
        _translate = QtCore.QCoreApplication.translate
        VolumeControlForm.setWindowTitle(_translate("VolumeControlForm", "Form"))
        self.groupBox.setTitle(_translate("VolumeControlForm", "Volume ramp"))
        self.label_volume.setText(_translate("VolumeControlForm", "Volume [%]"))
        self.label_target_volume.setText(_translate("VolumeControlForm", "Target volume [%]"))
        self.label_rate.setText(_translate("VolumeControlForm", "Rate [% / min]"))
        self.label.setText(_translate("VolumeControlForm", "Enable"))
        self.groupBox_2.setTitle(_translate("VolumeControlForm", "Lower volume during pauses"))
        self.label_2.setText(_translate("VolumeControlForm", "Inactivity threshold [seconds]"))
        self.label_3.setText(_translate("VolumeControlForm", "Reduce volume by [%]"))
        self.label_4.setText(_translate("VolumeControlForm", "Ramp time [seconds]"))
