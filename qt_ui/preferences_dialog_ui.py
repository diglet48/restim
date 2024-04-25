# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\designer\preferencesdialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_PreferencesDialog(object):
    def setupUi(self, PreferencesDialog):
        PreferencesDialog.setObjectName("PreferencesDialog")
        PreferencesDialog.resize(685, 627)
        self.verticalLayout = QtWidgets.QVBoxLayout(PreferencesDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtWidgets.QTabWidget(PreferencesDialog)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_network = QtWidgets.QWidget()
        self.tab_network.setObjectName("tab_network")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.tab_network)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gb_websocket_server = QtWidgets.QGroupBox(self.tab_network)
        self.gb_websocket_server.setCheckable(True)
        self.gb_websocket_server.setObjectName("gb_websocket_server")
        self.formLayout_4 = QtWidgets.QFormLayout(self.gb_websocket_server)
        self.formLayout_4.setObjectName("formLayout_4")
        self.label = QtWidgets.QLabel(self.gb_websocket_server)
        self.label.setObjectName("label")
        self.formLayout_4.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.label_6 = QtWidgets.QLabel(self.gb_websocket_server)
        self.label_6.setObjectName("label_6")
        self.formLayout_4.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_6)
        self.websocket_localhost_only = QtWidgets.QCheckBox(self.gb_websocket_server)
        self.websocket_localhost_only.setText("")
        self.websocket_localhost_only.setObjectName("websocket_localhost_only")
        self.formLayout_4.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.websocket_localhost_only)
        self.websocket_port = QtWidgets.QSpinBox(self.gb_websocket_server)
        self.websocket_port.setMaximum(65535)
        self.websocket_port.setObjectName("websocket_port")
        self.formLayout_4.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.websocket_port)
        self.verticalLayout_2.addWidget(self.gb_websocket_server)
        self.gb_tcp_server = QtWidgets.QGroupBox(self.tab_network)
        self.gb_tcp_server.setCheckable(True)
        self.gb_tcp_server.setObjectName("gb_tcp_server")
        self.formLayout_2 = QtWidgets.QFormLayout(self.gb_tcp_server)
        self.formLayout_2.setObjectName("formLayout_2")
        self.label_3 = QtWidgets.QLabel(self.gb_tcp_server)
        self.label_3.setObjectName("label_3")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.label_10 = QtWidgets.QLabel(self.gb_tcp_server)
        self.label_10.setObjectName("label_10")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_10)
        self.tcp_localhost_only = QtWidgets.QCheckBox(self.gb_tcp_server)
        self.tcp_localhost_only.setText("")
        self.tcp_localhost_only.setObjectName("tcp_localhost_only")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.tcp_localhost_only)
        self.tcp_port = QtWidgets.QSpinBox(self.gb_tcp_server)
        self.tcp_port.setMaximum(65535)
        self.tcp_port.setObjectName("tcp_port")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.tcp_port)
        self.verticalLayout_2.addWidget(self.gb_tcp_server)
        self.gb_udp_server = QtWidgets.QGroupBox(self.tab_network)
        self.gb_udp_server.setFlat(False)
        self.gb_udp_server.setCheckable(True)
        self.gb_udp_server.setObjectName("gb_udp_server")
        self.formLayout = QtWidgets.QFormLayout(self.gb_udp_server)
        self.formLayout.setObjectName("formLayout")
        self.label_4 = QtWidgets.QLabel(self.gb_udp_server)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.label_11 = QtWidgets.QLabel(self.gb_udp_server)
        self.label_11.setObjectName("label_11")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_11)
        self.udp_localhost_only = QtWidgets.QCheckBox(self.gb_udp_server)
        self.udp_localhost_only.setText("")
        self.udp_localhost_only.setObjectName("udp_localhost_only")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.udp_localhost_only)
        self.udp_port = QtWidgets.QSpinBox(self.gb_udp_server)
        self.udp_port.setMaximum(65535)
        self.udp_port.setObjectName("udp_port")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.udp_port)
        self.verticalLayout_2.addWidget(self.gb_udp_server)
        self.gb_serial = QtWidgets.QGroupBox(self.tab_network)
        self.gb_serial.setCheckable(True)
        self.gb_serial.setObjectName("gb_serial")
        self.formLayout_6 = QtWidgets.QFormLayout(self.gb_serial)
        self.formLayout_6.setObjectName("formLayout_6")
        self.label_23 = QtWidgets.QLabel(self.gb_serial)
        self.label_23.setObjectName("label_23")
        self.formLayout_6.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_23)
        self.label_24 = QtWidgets.QLabel(self.gb_serial)
        self.label_24.setObjectName("label_24")
        self.formLayout_6.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_24)
        self.serial_auto_expand = QtWidgets.QCheckBox(self.gb_serial)
        self.serial_auto_expand.setText("")
        self.serial_auto_expand.setObjectName("serial_auto_expand")
        self.formLayout_6.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.serial_auto_expand)
        self.serial_port = QtWidgets.QLineEdit(self.gb_serial)
        self.serial_port.setObjectName("serial_port")
        self.formLayout_6.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.serial_port)
        self.verticalLayout_2.addWidget(self.gb_serial)
        self.gb_buttplug_wsdm = QtWidgets.QGroupBox(self.tab_network)
        self.gb_buttplug_wsdm.setCheckable(True)
        self.gb_buttplug_wsdm.setObjectName("gb_buttplug_wsdm")
        self.formLayout_7 = QtWidgets.QFormLayout(self.gb_buttplug_wsdm)
        self.formLayout_7.setObjectName("formLayout_7")
        self.label_25 = QtWidgets.QLabel(self.gb_buttplug_wsdm)
        self.label_25.setObjectName("label_25")
        self.formLayout_7.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_25)
        self.buttplug_wsdm_address = QtWidgets.QLineEdit(self.gb_buttplug_wsdm)
        self.buttplug_wsdm_address.setObjectName("buttplug_wsdm_address")
        self.formLayout_7.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.buttplug_wsdm_address)
        self.label_26 = QtWidgets.QLabel(self.gb_buttplug_wsdm)
        self.label_26.setObjectName("label_26")
        self.formLayout_7.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_26)
        self.buttplug_wsdm_auto_expand = QtWidgets.QCheckBox(self.gb_buttplug_wsdm)
        self.buttplug_wsdm_auto_expand.setText("")
        self.buttplug_wsdm_auto_expand.setObjectName("buttplug_wsdm_auto_expand")
        self.formLayout_7.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.buttplug_wsdm_auto_expand)
        self.verticalLayout_2.addWidget(self.gb_buttplug_wsdm)
        self.label_12 = QtWidgets.QLabel(self.tab_network)
        self.label_12.setObjectName("label_12")
        self.verticalLayout_2.addWidget(self.label_12)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.tabWidget.addTab(self.tab_network, "")
        self.tab_audio = QtWidgets.QWidget()
        self.tab_audio.setObjectName("tab_audio")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.tab_audio)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.groupBox = QtWidgets.QGroupBox(self.tab_audio)
        self.groupBox.setObjectName("groupBox")
        self.formLayout_3 = QtWidgets.QFormLayout(self.groupBox)
        self.formLayout_3.setObjectName("formLayout_3")
        self.label_7 = QtWidgets.QLabel(self.groupBox)
        self.label_7.setObjectName("label_7")
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_7)
        self.audio_api = QtWidgets.QComboBox(self.groupBox)
        self.audio_api.setObjectName("audio_api")
        self.formLayout_3.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.audio_api)
        self.label_8 = QtWidgets.QLabel(self.groupBox)
        self.label_8.setObjectName("label_8")
        self.formLayout_3.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_8)
        self.audio_output_device = QtWidgets.QComboBox(self.groupBox)
        self.audio_output_device.setObjectName("audio_output_device")
        self.formLayout_3.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.audio_output_device)
        self.label_9 = QtWidgets.QLabel(self.groupBox)
        self.label_9.setObjectName("label_9")
        self.formLayout_3.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_9)
        self.audio_latency = QtWidgets.QComboBox(self.groupBox)
        self.audio_latency.setObjectName("audio_latency")
        self.audio_latency.addItem("")
        self.audio_latency.addItem("")
        self.audio_latency.addItem("")
        self.audio_latency.addItem("")
        self.audio_latency.addItem("")
        self.audio_latency.addItem("")
        self.audio_latency.addItem("")
        self.audio_latency.addItem("")
        self.audio_latency.addItem("")
        self.audio_latency.addItem("")
        self.audio_latency.addItem("")
        self.audio_latency.addItem("")
        self.audio_latency.addItem("")
        self.formLayout_3.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.audio_latency)
        self.label_27 = QtWidgets.QLabel(self.groupBox)
        self.label_27.setObjectName("label_27")
        self.formLayout_3.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_27)
        self.audio_info = QtWidgets.QLabel(self.groupBox)
        self.audio_info.setObjectName("audio_info")
        self.formLayout_3.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.audio_info)
        self.verticalLayout_3.addWidget(self.groupBox)
        self.groupBox_4 = QtWidgets.QGroupBox(self.tab_audio)
        self.groupBox_4.setObjectName("groupBox_4")
        self.formLayout_8 = QtWidgets.QFormLayout(self.groupBox_4)
        self.formLayout_8.setObjectName("formLayout_8")
        self.label_28 = QtWidgets.QLabel(self.groupBox_4)
        self.label_28.setObjectName("label_28")
        self.formLayout_8.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_28)
        self.channel_count = QtWidgets.QSpinBox(self.groupBox_4)
        self.channel_count.setObjectName("channel_count")
        self.formLayout_8.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.channel_count)
        self.label_29 = QtWidgets.QLabel(self.groupBox_4)
        self.label_29.setObjectName("label_29")
        self.formLayout_8.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_29)
        self.channel_map = QtWidgets.QLineEdit(self.groupBox_4)
        self.channel_map.setObjectName("channel_map")
        self.formLayout_8.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.channel_map)
        self.commandLinkButton = QtWidgets.QCommandLinkButton(self.groupBox_4)
        self.commandLinkButton.setObjectName("commandLinkButton")
        self.formLayout_8.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.commandLinkButton)
        self.verticalLayout_3.addWidget(self.groupBox_4)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem1)
        self.tabWidget.addTab(self.tab_audio, "")
        self.tab_media_settings = QtWidgets.QWidget()
        self.tab_media_settings.setObjectName("tab_media_settings")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.tab_media_settings)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.groupBox_3 = QtWidgets.QGroupBox(self.tab_media_settings)
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox_3)
        self.gridLayout.setObjectName("gridLayout")
        self.mpc_address = QtWidgets.QLineEdit(self.groupBox_3)
        self.mpc_address.setObjectName("mpc_address")
        self.gridLayout.addWidget(self.mpc_address, 0, 1, 1, 1)
        self.label_31 = QtWidgets.QLabel(self.groupBox_3)
        self.label_31.setObjectName("label_31")
        self.gridLayout.addWidget(self.label_31, 0, 0, 1, 1)
        self.mpc_reload = QtWidgets.QToolButton(self.groupBox_3)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/restim/arrow-round_poly.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.mpc_reload.setIcon(icon)
        self.mpc_reload.setObjectName("mpc_reload")
        self.gridLayout.addWidget(self.mpc_reload, 0, 2, 1, 1)
        self.verticalLayout_6.addWidget(self.groupBox_3)
        self.groupBox_6 = QtWidgets.QGroupBox(self.tab_media_settings)
        self.groupBox_6.setObjectName("groupBox_6")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox_6)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_32 = QtWidgets.QLabel(self.groupBox_6)
        self.label_32.setObjectName("label_32")
        self.gridLayout_3.addWidget(self.label_32, 0, 0, 1, 1)
        self.heresphere_address = QtWidgets.QLineEdit(self.groupBox_6)
        self.heresphere_address.setObjectName("heresphere_address")
        self.gridLayout_3.addWidget(self.heresphere_address, 0, 1, 1, 1)
        self.heresphere_reload = QtWidgets.QToolButton(self.groupBox_6)
        self.heresphere_reload.setIcon(icon)
        self.heresphere_reload.setObjectName("heresphere_reload")
        self.gridLayout_3.addWidget(self.heresphere_reload, 0, 2, 1, 1)
        self.verticalLayout_6.addWidget(self.groupBox_6)
        self.groupBox_7 = QtWidgets.QGroupBox(self.tab_media_settings)
        self.groupBox_7.setObjectName("groupBox_7")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.groupBox_7)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.vlc_reload = QtWidgets.QToolButton(self.groupBox_7)
        self.vlc_reload.setIcon(icon)
        self.vlc_reload.setObjectName("vlc_reload")
        self.gridLayout_4.addWidget(self.vlc_reload, 0, 2, 1, 1)
        self.label_33 = QtWidgets.QLabel(self.groupBox_7)
        self.label_33.setObjectName("label_33")
        self.gridLayout_4.addWidget(self.label_33, 0, 0, 1, 1)
        self.vlc_address = QtWidgets.QLineEdit(self.groupBox_7)
        self.vlc_address.setObjectName("vlc_address")
        self.gridLayout_4.addWidget(self.vlc_address, 0, 1, 1, 1)
        self.label_34 = QtWidgets.QLabel(self.groupBox_7)
        self.label_34.setObjectName("label_34")
        self.gridLayout_4.addWidget(self.label_34, 1, 0, 1, 1)
        self.widget = QtWidgets.QWidget(self.groupBox_7)
        self.widget.setObjectName("widget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.vlc_username = QtWidgets.QLineEdit(self.widget)
        self.vlc_username.setObjectName("vlc_username")
        self.horizontalLayout_2.addWidget(self.vlc_username)
        self.vlc_password = QtWidgets.QLineEdit(self.widget)
        self.vlc_password.setObjectName("vlc_password")
        self.horizontalLayout_2.addWidget(self.vlc_password)
        self.gridLayout_4.addWidget(self.widget, 1, 1, 1, 1)
        self.verticalLayout_6.addWidget(self.groupBox_7)
        self.groupBox_2 = QtWidgets.QGroupBox(self.tab_media_settings)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.kodi_address = QtWidgets.QLineEdit(self.groupBox_2)
        self.kodi_address.setObjectName("kodi_address")
        self.gridLayout_2.addWidget(self.kodi_address, 0, 1, 1, 1)
        self.label_13 = QtWidgets.QLabel(self.groupBox_2)
        self.label_13.setObjectName("label_13")
        self.gridLayout_2.addWidget(self.label_13, 0, 0, 1, 1)
        self.kodi_reload = QtWidgets.QToolButton(self.groupBox_2)
        self.kodi_reload.setIcon(icon)
        self.kodi_reload.setObjectName("kodi_reload")
        self.gridLayout_2.addWidget(self.kodi_reload, 0, 2, 1, 1)
        self.verticalLayout_6.addWidget(self.groupBox_2)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_6.addItem(spacerItem2)
        self.tabWidget.addTab(self.tab_media_settings, "")
        self.tab_display = QtWidgets.QWidget()
        self.tab_display.setObjectName("tab_display")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.tab_display)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.groupBox_5 = QtWidgets.QGroupBox(self.tab_display)
        self.groupBox_5.setEnabled(True)
        self.groupBox_5.setObjectName("groupBox_5")
        self.formLayout_5 = QtWidgets.QFormLayout(self.groupBox_5)
        self.formLayout_5.setObjectName("formLayout_5")
        self.label_2 = QtWidgets.QLabel(self.groupBox_5)
        self.label_2.setObjectName("label_2")
        self.formLayout_5.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.label_5 = QtWidgets.QLabel(self.groupBox_5)
        self.label_5.setObjectName("label_5")
        self.formLayout_5.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.display_fps = QtWidgets.QSpinBox(self.groupBox_5)
        self.display_fps.setMaximum(1000)
        self.display_fps.setObjectName("display_fps")
        self.formLayout_5.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.display_fps)
        self.display_latency_ms = QtWidgets.QDoubleSpinBox(self.groupBox_5)
        self.display_latency_ms.setSuffix("")
        self.display_latency_ms.setMaximum(1000.0)
        self.display_latency_ms.setObjectName("display_latency_ms")
        self.formLayout_5.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.display_latency_ms)
        self.verticalLayout_4.addWidget(self.groupBox_5)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem3)
        self.tabWidget.addTab(self.tab_display, "")
        self.tab_funscript = QtWidgets.QWidget()
        self.tab_funscript.setObjectName("tab_funscript")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.tab_funscript)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.tableView = TableViewWithComboBox(self.tab_funscript)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableView.sizePolicy().hasHeightForWidth())
        self.tableView.setSizePolicy(sizePolicy)
        self.tableView.setObjectName("tableView")
        self.verticalLayout_7.addWidget(self.tableView)
        self.frame = QtWidgets.QFrame(self.tab_funscript)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.button_funscript_reset_defaults = QtWidgets.QPushButton(self.frame)
        self.button_funscript_reset_defaults.setObjectName("button_funscript_reset_defaults")
        self.horizontalLayout.addWidget(self.button_funscript_reset_defaults)
        self.verticalLayout_7.addWidget(self.frame)
        self.tabWidget.addTab(self.tab_funscript, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.buttonBox = QtWidgets.QDialogButtonBox(PreferencesDialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(PreferencesDialog)
        self.tabWidget.setCurrentIndex(2)
        QtCore.QMetaObject.connectSlotsByName(PreferencesDialog)
        PreferencesDialog.setTabOrder(self.udp_localhost_only, self.display_fps)
        PreferencesDialog.setTabOrder(self.display_fps, self.display_latency_ms)
        PreferencesDialog.setTabOrder(self.display_latency_ms, self.audio_api)
        PreferencesDialog.setTabOrder(self.audio_api, self.audio_output_device)
        PreferencesDialog.setTabOrder(self.audio_output_device, self.gb_websocket_server)
        PreferencesDialog.setTabOrder(self.gb_websocket_server, self.websocket_localhost_only)
        PreferencesDialog.setTabOrder(self.websocket_localhost_only, self.gb_tcp_server)
        PreferencesDialog.setTabOrder(self.gb_tcp_server, self.tcp_localhost_only)
        PreferencesDialog.setTabOrder(self.tcp_localhost_only, self.gb_udp_server)

    def retranslateUi(self, PreferencesDialog):
        _translate = QtCore.QCoreApplication.translate
        PreferencesDialog.setWindowTitle(_translate("PreferencesDialog", "Preferences"))
        self.gb_websocket_server.setTitle(_translate("PreferencesDialog", "Websocket server"))
        self.label.setText(_translate("PreferencesDialog", "Port"))
        self.label_6.setText(_translate("PreferencesDialog", "Localhost only"))
        self.gb_tcp_server.setTitle(_translate("PreferencesDialog", "TCP server"))
        self.label_3.setText(_translate("PreferencesDialog", "Port"))
        self.label_10.setText(_translate("PreferencesDialog", "Localhost only"))
        self.gb_udp_server.setTitle(_translate("PreferencesDialog", "UDP server"))
        self.label_4.setText(_translate("PreferencesDialog", "Port"))
        self.label_11.setText(_translate("PreferencesDialog", "Localhost only"))
        self.gb_serial.setTitle(_translate("PreferencesDialog", "Serial port"))
        self.label_23.setText(_translate("PreferencesDialog", "COM port"))
        self.label_24.setText(_translate("PreferencesDialog", "generate beta axis"))
        self.gb_buttplug_wsdm.setTitle(_translate("PreferencesDialog", "Buttplug (WSDM)"))
        self.label_25.setText(_translate("PreferencesDialog", "address"))
        self.label_26.setText(_translate("PreferencesDialog", "generate beta axis"))
        self.label_12.setText(_translate("PreferencesDialog", "Changes require restart"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_network), _translate("PreferencesDialog", "Network"))
        self.groupBox.setTitle(_translate("PreferencesDialog", "Audio"))
        self.label_7.setText(_translate("PreferencesDialog", "Audio API"))
        self.label_8.setText(_translate("PreferencesDialog", "Output Device"))
        self.label_9.setText(_translate("PreferencesDialog", "Latency"))
        self.audio_latency.setItemText(0, _translate("PreferencesDialog", "high"))
        self.audio_latency.setItemText(1, _translate("PreferencesDialog", "low"))
        self.audio_latency.setItemText(2, _translate("PreferencesDialog", "0.00"))
        self.audio_latency.setItemText(3, _translate("PreferencesDialog", "0.02"))
        self.audio_latency.setItemText(4, _translate("PreferencesDialog", "0.04"))
        self.audio_latency.setItemText(5, _translate("PreferencesDialog", "0.06"))
        self.audio_latency.setItemText(6, _translate("PreferencesDialog", "0.08"))
        self.audio_latency.setItemText(7, _translate("PreferencesDialog", "0.10"))
        self.audio_latency.setItemText(8, _translate("PreferencesDialog", "0.12"))
        self.audio_latency.setItemText(9, _translate("PreferencesDialog", "0.14"))
        self.audio_latency.setItemText(10, _translate("PreferencesDialog", "0.16"))
        self.audio_latency.setItemText(11, _translate("PreferencesDialog", "0.18"))
        self.audio_latency.setItemText(12, _translate("PreferencesDialog", "0.20"))
        self.label_27.setText(_translate("PreferencesDialog", "Info"))
        self.audio_info.setText(_translate("PreferencesDialog", "TextLabel"))
        self.groupBox_4.setTitle(_translate("PreferencesDialog", "4 and 5-phase device configuration"))
        self.label_28.setText(_translate("PreferencesDialog", "Channel count"))
        self.label_29.setText(_translate("PreferencesDialog", "Channel map"))
        self.commandLinkButton.setText(_translate("PreferencesDialog", "Test this device"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_audio), _translate("PreferencesDialog", "Audio"))
        self.groupBox_3.setTitle(_translate("PreferencesDialog", "MPC-HC"))
        self.label_31.setText(_translate("PreferencesDialog", "address:port"))
        self.mpc_reload.setText(_translate("PreferencesDialog", "..."))
        self.groupBox_6.setTitle(_translate("PreferencesDialog", "HereSphere"))
        self.label_32.setText(_translate("PreferencesDialog", "address:port"))
        self.heresphere_reload.setText(_translate("PreferencesDialog", "..."))
        self.groupBox_7.setTitle(_translate("PreferencesDialog", "VLC"))
        self.vlc_reload.setText(_translate("PreferencesDialog", "..."))
        self.label_33.setText(_translate("PreferencesDialog", "address:port"))
        self.label_34.setText(_translate("PreferencesDialog", "user/password"))
        self.groupBox_2.setTitle(_translate("PreferencesDialog", "Kodi"))
        self.label_13.setText(_translate("PreferencesDialog", "address:port"))
        self.kodi_reload.setText(_translate("PreferencesDialog", "..."))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_media_settings), _translate("PreferencesDialog", "Media sync"))
        self.groupBox_5.setTitle(_translate("PreferencesDialog", "Phase"))
        self.label_2.setText(_translate("PreferencesDialog", "max fps"))
        self.label_5.setText(_translate("PreferencesDialog", "display latency [ms]"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_display), _translate("PreferencesDialog", "Display"))
        self.button_funscript_reset_defaults.setText(_translate("PreferencesDialog", "Reset all to defaults"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_funscript), _translate("PreferencesDialog", "Funscript / T-Code"))
from qt_ui.widgets.table_view_with_combobox import TableViewWithComboBox
import restim_rc
