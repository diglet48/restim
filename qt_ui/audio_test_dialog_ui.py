# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\designer\audiotestdialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AudioTestDialog(object):
    def setupUi(self, AudioTestDialog):
        AudioTestDialog.setObjectName("AudioTestDialog")
        AudioTestDialog.resize(412, 605)
        self.verticalLayout = QtWidgets.QVBoxLayout(AudioTestDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(AudioTestDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.groupBox.setObjectName("groupBox")
        self.formLayout = QtWidgets.QFormLayout(self.groupBox)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.spinBox_channel_count = QtWidgets.QSpinBox(self.groupBox)
        self.spinBox_channel_count.setObjectName("spinBox_channel_count")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.spinBox_channel_count)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.doubleSpinBox_frequency = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.doubleSpinBox_frequency.setMinimum(500.0)
        self.doubleSpinBox_frequency.setMaximum(2000.0)
        self.doubleSpinBox_frequency.setObjectName("doubleSpinBox_frequency")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.doubleSpinBox_frequency)
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.doubleSpinBox_volume = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.doubleSpinBox_volume.setMaximum(100.0)
        self.doubleSpinBox_volume.setProperty("value", 50.0)
        self.doubleSpinBox_volume.setObjectName("doubleSpinBox_volume")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.doubleSpinBox_volume)
        self.commandLinkButton = QtWidgets.QCommandLinkButton(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.commandLinkButton.sizePolicy().hasHeightForWidth())
        self.commandLinkButton.setSizePolicy(sizePolicy)
        self.commandLinkButton.setObjectName("commandLinkButton")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.commandLinkButton)
        self.label_channel_map = QtWidgets.QLabel(self.groupBox)
        self.label_channel_map.setObjectName("label_channel_map")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.label_channel_map)
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.verticalLayout.addWidget(self.groupBox)
        self.plainTextEdit = QtWidgets.QPlainTextEdit(AudioTestDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.plainTextEdit.sizePolicy().hasHeightForWidth())
        self.plainTextEdit.setSizePolicy(sizePolicy)
        self.plainTextEdit.setMaximumSize(QtCore.QSize(16777215, 100))
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.verticalLayout.addWidget(self.plainTextEdit)
        self.groupBox_2 = QtWidgets.QGroupBox(AudioTestDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setMinimumSize(QtCore.QSize(0, 100))
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout.addWidget(self.groupBox_2)
        self.buttonBox = QtWidgets.QDialogButtonBox(AudioTestDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.NoButton)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(AudioTestDialog)
        self.buttonBox.accepted.connect(AudioTestDialog.accept)
        self.buttonBox.rejected.connect(AudioTestDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AudioTestDialog)

    def retranslateUi(self, AudioTestDialog):
        _translate = QtCore.QCoreApplication.translate
        AudioTestDialog.setWindowTitle(_translate("AudioTestDialog", "Audio device test"))
        self.groupBox.setTitle(_translate("AudioTestDialog", "Device"))
        self.label.setText(_translate("AudioTestDialog", "Channel count"))
        self.label_2.setText(_translate("AudioTestDialog", "Frequency [Hz]"))
        self.label_3.setText(_translate("AudioTestDialog", "Volume [%]"))
        self.commandLinkButton.setText(_translate("AudioTestDialog", "Start audio"))
        self.label_channel_map.setText(_translate("AudioTestDialog", "TextLabel"))
        self.label_5.setText(_translate("AudioTestDialog", "Channel map"))
        self.plainTextEdit.setPlainText(_translate("AudioTestDialog", "Instructions:\n"
"- Grab a multimeter\n"
"- Open the audio device. If that doesn\'t work, try a different channel count\n"
"- Use the multimeter to find out which output corresponds to which audio channel\n"
"- Copy the channel count and map to the settings dialog"))
        self.groupBox_2.setTitle(_translate("AudioTestDialog", "Channels"))
