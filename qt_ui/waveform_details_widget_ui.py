# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\designer\waveformdetailswidget.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_WaveformDetails(object):
    def setupUi(self, WaveformDetails):
        WaveformDetails.setObjectName("WaveformDetails")
        WaveformDetails.resize(553, 528)
        self.verticalLayout = QtWidgets.QVBoxLayout(WaveformDetails)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox_2 = QtWidgets.QGroupBox(WaveformDetails)
        self.groupBox_2.setObjectName("groupBox_2")
        self.formLayout = QtWidgets.QFormLayout(self.groupBox_2)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(self.groupBox_2)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.left_amplitude_label = QtWidgets.QLabel(self.groupBox_2)
        self.left_amplitude_label.setObjectName("left_amplitude_label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.left_amplitude_label)
        self.label_3 = QtWidgets.QLabel(self.groupBox_2)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.right_amplitude_label = QtWidgets.QLabel(self.groupBox_2)
        self.right_amplitude_label.setObjectName("right_amplitude_label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.right_amplitude_label)
        self.label_7 = QtWidgets.QLabel(self.groupBox_2)
        self.label_7.setObjectName("label_7")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_7)
        self.center_amplitude_label = QtWidgets.QLabel(self.groupBox_2)
        self.center_amplitude_label.setObjectName("center_amplitude_label")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.center_amplitude_label)
        self.label_5 = QtWidgets.QLabel(self.groupBox_2)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.phase_label = QtWidgets.QLabel(self.groupBox_2)
        self.phase_label.setObjectName("phase_label")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.phase_label)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.groupBox_3 = QtWidgets.QGroupBox(WaveformDetails)
        self.groupBox_3.setObjectName("groupBox_3")
        self.formLayout_2 = QtWidgets.QFormLayout(self.groupBox_3)
        self.formLayout_2.setObjectName("formLayout_2")
        self.label_9 = QtWidgets.QLabel(self.groupBox_3)
        self.label_9.setObjectName("label_9")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_9)
        self.alpha_label = QtWidgets.QLabel(self.groupBox_3)
        self.alpha_label.setObjectName("alpha_label")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.alpha_label)
        self.label_11 = QtWidgets.QLabel(self.groupBox_3)
        self.label_11.setObjectName("label_11")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_11)
        self.beta_label = QtWidgets.QLabel(self.groupBox_3)
        self.beta_label.setObjectName("beta_label")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.beta_label)
        self.verticalLayout.addWidget(self.groupBox_3)
        self.groupBox_5 = QtWidgets.QGroupBox(WaveformDetails)
        self.groupBox_5.setObjectName("groupBox_5")
        self.formLayout_5 = QtWidgets.QFormLayout(self.groupBox_5)
        self.formLayout_5.setObjectName("formLayout_5")
        self.label_8 = QtWidgets.QLabel(self.groupBox_5)
        self.label_8.setObjectName("label_8")
        self.formLayout_5.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_8)
        self.r_label = QtWidgets.QLabel(self.groupBox_5)
        self.r_label.setObjectName("r_label")
        self.formLayout_5.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.r_label)
        self.label_13 = QtWidgets.QLabel(self.groupBox_5)
        self.label_13.setObjectName("label_13")
        self.formLayout_5.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_13)
        self.theta_label = QtWidgets.QLabel(self.groupBox_5)
        self.theta_label.setObjectName("theta_label")
        self.formLayout_5.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.theta_label)
        self.verticalLayout.addWidget(self.groupBox_5)
        self.groupBox = QtWidgets.QGroupBox(WaveformDetails)
        self.groupBox.setObjectName("groupBox")
        self.formLayout_3 = QtWidgets.QFormLayout(self.groupBox)
        self.formLayout_3.setObjectName("formLayout_3")
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.neutral_label = QtWidgets.QLabel(self.groupBox)
        self.neutral_label.setObjectName("neutral_label")
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.neutral_label)
        self.label_6 = QtWidgets.QLabel(self.groupBox)
        self.label_6.setObjectName("label_6")
        self.formLayout_3.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_6)
        self.right_label = QtWidgets.QLabel(self.groupBox)
        self.right_label.setObjectName("right_label")
        self.formLayout_3.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.right_label)
        self.label_10 = QtWidgets.QLabel(self.groupBox)
        self.label_10.setObjectName("label_10")
        self.formLayout_3.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_10)
        self.left_label = QtWidgets.QLabel(self.groupBox)
        self.left_label.setObjectName("left_label")
        self.formLayout_3.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.left_label)
        self.verticalLayout.addWidget(self.groupBox)
        self.label_4 = QtWidgets.QLabel(WaveformDetails)
        self.label_4.setObjectName("label_4")
        self.verticalLayout.addWidget(self.label_4)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(WaveformDetails)
        QtCore.QMetaObject.connectSlotsByName(WaveformDetails)

    def retranslateUi(self, WaveformDetails):
        _translate = QtCore.QCoreApplication.translate
        WaveformDetails.setWindowTitle(_translate("WaveformDetails", "Form"))
        self.groupBox_2.setTitle(_translate("WaveformDetails", "Amplitude, Phase"))
        self.label.setText(_translate("WaveformDetails", "Left amplitude"))
        self.left_amplitude_label.setText(_translate("WaveformDetails", "TextLabel"))
        self.label_3.setText(_translate("WaveformDetails", "Right amplitude"))
        self.right_amplitude_label.setText(_translate("WaveformDetails", "TextLabel"))
        self.label_7.setText(_translate("WaveformDetails", "Center amplitude"))
        self.center_amplitude_label.setText(_translate("WaveformDetails", "TextLabel"))
        self.label_5.setText(_translate("WaveformDetails", "Phase"))
        self.phase_label.setText(_translate("WaveformDetails", "TextLabel"))
        self.groupBox_3.setTitle(_translate("WaveformDetails", "Alpha, Beta"))
        self.label_9.setText(_translate("WaveformDetails", "Alpha"))
        self.alpha_label.setText(_translate("WaveformDetails", "TextLabel"))
        self.label_11.setText(_translate("WaveformDetails", "Beta"))
        self.beta_label.setText(_translate("WaveformDetails", "TextLabel"))
        self.groupBox_5.setTitle(_translate("WaveformDetails", "R, Theta"))
        self.label_8.setText(_translate("WaveformDetails", "R"))
        self.r_label.setText(_translate("WaveformDetails", "TextLabel"))
        self.label_13.setText(_translate("WaveformDetails", "Theta"))
        self.theta_label.setText(_translate("WaveformDetails", "TextLabel"))
        self.groupBox.setTitle(_translate("WaveformDetails", "Amplitude at electrodes"))
        self.label_2.setText(_translate("WaveformDetails", "Neutral"))
        self.neutral_label.setText(_translate("WaveformDetails", "TextLabel"))
        self.label_6.setText(_translate("WaveformDetails", "R+"))
        self.right_label.setText(_translate("WaveformDetails", "TextLabel"))
        self.label_10.setText(_translate("WaveformDetails", "L+"))
        self.left_label.setText(_translate("WaveformDetails", "TextLabel"))
        self.label_4.setText(_translate("WaveformDetails", "Does not take calibration into account."))
