# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\designer\device_wizard\neostim_waveform_select.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_WizardPageNeoStim(object):
    def setupUi(self, WizardPageNeoStim):
        WizardPageNeoStim.setObjectName("WizardPageNeoStim")
        WizardPageNeoStim.resize(611, 497)
        self.verticalLayout = QtWidgets.QVBoxLayout(WizardPageNeoStim)
        self.verticalLayout.setObjectName("verticalLayout")
        self.three_phase_radio = QtWidgets.QRadioButton(WizardPageNeoStim)
        self.three_phase_radio.setObjectName("three_phase_radio")
        self.verticalLayout.addWidget(self.three_phase_radio)
        self.label = QtWidgets.QLabel(WizardPageNeoStim)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(WizardPageNeoStim)
        QtCore.QMetaObject.connectSlotsByName(WizardPageNeoStim)

    def retranslateUi(self, WizardPageNeoStim):
        _translate = QtCore.QCoreApplication.translate
        WizardPageNeoStim.setWindowTitle(_translate("WizardPageNeoStim", "WizardPage"))
        self.three_phase_radio.setText(_translate("WizardPageNeoStim", "Three-phase"))
        self.label.setText(_translate("WizardPageNeoStim", "<html><head/><body><p>A = neutral<br/>B = left<br/>C+D = right. Short these outputs together on your box.</p><p><br/></p></body></html>"))
