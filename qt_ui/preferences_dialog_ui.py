# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'preferencesdialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QAbstractItemView, QApplication, QCheckBox,
    QComboBox, QDialogButtonBox, QDoubleSpinBox, QFormLayout,
    QFrame, QGridLayout, QGroupBox, QHBoxLayout,
    QHeaderView, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QSpacerItem, QSpinBox, QTabWidget,
    QTableWidget, QTableWidgetItem, QToolButton, QVBoxLayout,
    QWidget)

from qt_ui.widgets.table_view_with_combobox import TableViewWithComboBox
import restim_rc

class Ui_PreferencesDialog(object):
    def setupUi(self, PreferencesDialog):
        if not PreferencesDialog.objectName():
            PreferencesDialog.setObjectName(u"PreferencesDialog")
        PreferencesDialog.resize(685, 627)
        self.verticalLayout = QVBoxLayout(PreferencesDialog)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.tabWidget = QTabWidget(PreferencesDialog)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab_network = QWidget()
        self.tab_network.setObjectName(u"tab_network")
        self.verticalLayout_2 = QVBoxLayout(self.tab_network)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.gb_websocket_server = QGroupBox(self.tab_network)
        self.gb_websocket_server.setObjectName(u"gb_websocket_server")
        self.gb_websocket_server.setCheckable(True)
        self.formLayout_4 = QFormLayout(self.gb_websocket_server)
        self.formLayout_4.setObjectName(u"formLayout_4")
        self.label = QLabel(self.gb_websocket_server)
        self.label.setObjectName(u"label")

        self.formLayout_4.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)

        self.label_6 = QLabel(self.gb_websocket_server)
        self.label_6.setObjectName(u"label_6")

        self.formLayout_4.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_6)

        self.websocket_localhost_only = QCheckBox(self.gb_websocket_server)
        self.websocket_localhost_only.setObjectName(u"websocket_localhost_only")

        self.formLayout_4.setWidget(1, QFormLayout.ItemRole.FieldRole, self.websocket_localhost_only)

        self.websocket_port = QSpinBox(self.gb_websocket_server)
        self.websocket_port.setObjectName(u"websocket_port")
        self.websocket_port.setMaximum(65535)

        self.formLayout_4.setWidget(0, QFormLayout.ItemRole.FieldRole, self.websocket_port)


        self.verticalLayout_2.addWidget(self.gb_websocket_server)

        self.gb_tcp_server = QGroupBox(self.tab_network)
        self.gb_tcp_server.setObjectName(u"gb_tcp_server")
        self.gb_tcp_server.setCheckable(True)
        self.formLayout_2 = QFormLayout(self.gb_tcp_server)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.label_3 = QLabel(self.gb_tcp_server)
        self.label_3.setObjectName(u"label_3")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_3)

        self.label_10 = QLabel(self.gb_tcp_server)
        self.label_10.setObjectName(u"label_10")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_10)

        self.tcp_localhost_only = QCheckBox(self.gb_tcp_server)
        self.tcp_localhost_only.setObjectName(u"tcp_localhost_only")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.tcp_localhost_only)

        self.tcp_port = QSpinBox(self.gb_tcp_server)
        self.tcp_port.setObjectName(u"tcp_port")
        self.tcp_port.setMaximum(65535)

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.tcp_port)


        self.verticalLayout_2.addWidget(self.gb_tcp_server)

        self.gb_udp_server = QGroupBox(self.tab_network)
        self.gb_udp_server.setObjectName(u"gb_udp_server")
        self.gb_udp_server.setFlat(False)
        self.gb_udp_server.setCheckable(True)
        self.formLayout = QFormLayout(self.gb_udp_server)
        self.formLayout.setObjectName(u"formLayout")
        self.label_4 = QLabel(self.gb_udp_server)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_4)

        self.label_11 = QLabel(self.gb_udp_server)
        self.label_11.setObjectName(u"label_11")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_11)

        self.udp_localhost_only = QCheckBox(self.gb_udp_server)
        self.udp_localhost_only.setObjectName(u"udp_localhost_only")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.udp_localhost_only)

        self.udp_port = QSpinBox(self.gb_udp_server)
        self.udp_port.setObjectName(u"udp_port")
        self.udp_port.setMaximum(65535)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.udp_port)


        self.verticalLayout_2.addWidget(self.gb_udp_server)

        self.gb_serial = QGroupBox(self.tab_network)
        self.gb_serial.setObjectName(u"gb_serial")
        self.gb_serial.setCheckable(True)
        self.formLayout_6 = QFormLayout(self.gb_serial)
        self.formLayout_6.setObjectName(u"formLayout_6")
        self.label_23 = QLabel(self.gb_serial)
        self.label_23.setObjectName(u"label_23")

        self.formLayout_6.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_23)

        self.label_24 = QLabel(self.gb_serial)
        self.label_24.setObjectName(u"label_24")

        self.formLayout_6.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_24)

        self.serial_auto_expand = QCheckBox(self.gb_serial)
        self.serial_auto_expand.setObjectName(u"serial_auto_expand")

        self.formLayout_6.setWidget(1, QFormLayout.ItemRole.FieldRole, self.serial_auto_expand)

        self.serial_port = QLineEdit(self.gb_serial)
        self.serial_port.setObjectName(u"serial_port")

        self.formLayout_6.setWidget(0, QFormLayout.ItemRole.FieldRole, self.serial_port)


        self.verticalLayout_2.addWidget(self.gb_serial)

        self.gb_buttplug_wsdm = QGroupBox(self.tab_network)
        self.gb_buttplug_wsdm.setObjectName(u"gb_buttplug_wsdm")
        self.gb_buttplug_wsdm.setCheckable(True)
        self.formLayout_7 = QFormLayout(self.gb_buttplug_wsdm)
        self.formLayout_7.setObjectName(u"formLayout_7")
        self.label_25 = QLabel(self.gb_buttplug_wsdm)
        self.label_25.setObjectName(u"label_25")

        self.formLayout_7.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_25)

        self.buttplug_wsdm_address = QLineEdit(self.gb_buttplug_wsdm)
        self.buttplug_wsdm_address.setObjectName(u"buttplug_wsdm_address")

        self.formLayout_7.setWidget(0, QFormLayout.ItemRole.FieldRole, self.buttplug_wsdm_address)

        self.label_26 = QLabel(self.gb_buttplug_wsdm)
        self.label_26.setObjectName(u"label_26")

        self.formLayout_7.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_26)

        self.buttplug_wsdm_auto_expand = QCheckBox(self.gb_buttplug_wsdm)
        self.buttplug_wsdm_auto_expand.setObjectName(u"buttplug_wsdm_auto_expand")

        self.formLayout_7.setWidget(1, QFormLayout.ItemRole.FieldRole, self.buttplug_wsdm_auto_expand)


        self.verticalLayout_2.addWidget(self.gb_buttplug_wsdm)

        self.label_12 = QLabel(self.tab_network)
        self.label_12.setObjectName(u"label_12")

        self.verticalLayout_2.addWidget(self.label_12)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_3)

        self.tabWidget.addTab(self.tab_network, "")
        self.tab_audio = QWidget()
        self.tab_audio.setObjectName(u"tab_audio")
        self.verticalLayout_3 = QVBoxLayout(self.tab_audio)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.groupBox = QGroupBox(self.tab_audio)
        self.groupBox.setObjectName(u"groupBox")
        self.formLayout_3 = QFormLayout(self.groupBox)
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.label_7 = QLabel(self.groupBox)
        self.label_7.setObjectName(u"label_7")

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_7)

        self.audio_api = QComboBox(self.groupBox)
        self.audio_api.setObjectName(u"audio_api")

        self.formLayout_3.setWidget(0, QFormLayout.ItemRole.FieldRole, self.audio_api)

        self.label_8 = QLabel(self.groupBox)
        self.label_8.setObjectName(u"label_8")

        self.formLayout_3.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_8)

        self.audio_output_device = QComboBox(self.groupBox)
        self.audio_output_device.setObjectName(u"audio_output_device")

        self.formLayout_3.setWidget(1, QFormLayout.ItemRole.FieldRole, self.audio_output_device)

        self.label_9 = QLabel(self.groupBox)
        self.label_9.setObjectName(u"label_9")

        self.formLayout_3.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_9)

        self.audio_latency = QComboBox(self.groupBox)
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
        self.audio_latency.setObjectName(u"audio_latency")

        self.formLayout_3.setWidget(2, QFormLayout.ItemRole.FieldRole, self.audio_latency)

        self.label_27 = QLabel(self.groupBox)
        self.label_27.setObjectName(u"label_27")

        self.formLayout_3.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_27)

        self.audio_info = QLabel(self.groupBox)
        self.audio_info.setObjectName(u"audio_info")

        self.formLayout_3.setWidget(3, QFormLayout.ItemRole.FieldRole, self.audio_info)


        self.verticalLayout_3.addWidget(self.groupBox)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self.tabWidget.addTab(self.tab_audio, "")
        self.tab_foc = QWidget()
        self.tab_foc.setObjectName(u"tab_foc")
        self.verticalLayout_5 = QVBoxLayout(self.tab_foc)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.groupBox_8 = QGroupBox(self.tab_foc)
        self.groupBox_8.setObjectName(u"groupBox_8")
        self.gridLayout_5 = QGridLayout(self.groupBox_8)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.focstim_teleplot_prefix = QLineEdit(self.groupBox_8)
        self.focstim_teleplot_prefix.setObjectName(u"focstim_teleplot_prefix")

        self.gridLayout_5.addWidget(self.focstim_teleplot_prefix, 2, 2, 1, 1)

        self.focstim_use_teleplot = QCheckBox(self.groupBox_8)
        self.focstim_use_teleplot.setObjectName(u"focstim_use_teleplot")

        self.gridLayout_5.addWidget(self.focstim_use_teleplot, 1, 2, 1, 1)

        self.label_16 = QLabel(self.groupBox_8)
        self.label_16.setObjectName(u"label_16")

        self.gridLayout_5.addWidget(self.label_16, 2, 0, 1, 1)

        self.refresh_serial_devices = QToolButton(self.groupBox_8)
        self.refresh_serial_devices.setObjectName(u"refresh_serial_devices")

        self.gridLayout_5.addWidget(self.refresh_serial_devices, 0, 3, 1, 1)

        self.label_18 = QLabel(self.groupBox_8)
        self.label_18.setObjectName(u"label_18")

        self.gridLayout_5.addWidget(self.label_18, 3, 0, 1, 1)

        self.focstim_port = QComboBox(self.groupBox_8)
        self.focstim_port.setObjectName(u"focstim_port")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.focstim_port.sizePolicy().hasHeightForWidth())
        self.focstim_port.setSizePolicy(sizePolicy)

        self.gridLayout_5.addWidget(self.focstim_port, 0, 2, 1, 1)

        self.label_15 = QLabel(self.groupBox_8)
        self.label_15.setObjectName(u"label_15")

        self.gridLayout_5.addWidget(self.label_15, 1, 0, 1, 1)

        self.label_14 = QLabel(self.groupBox_8)
        self.label_14.setObjectName(u"label_14")

        self.gridLayout_5.addWidget(self.label_14, 0, 0, 1, 1)

        self.focstim_dump_notifications = QCheckBox(self.groupBox_8)
        self.focstim_dump_notifications.setObjectName(u"focstim_dump_notifications")

        self.gridLayout_5.addWidget(self.focstim_dump_notifications, 3, 2, 1, 1)


        self.verticalLayout_5.addWidget(self.groupBox_8)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer_4)

        self.tabWidget.addTab(self.tab_foc, "")
        self.tab_neostim = QWidget()
        self.tab_neostim.setObjectName(u"tab_neostim")
        self.verticalLayout_8 = QVBoxLayout(self.tab_neostim)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.groupBox_4 = QGroupBox(self.tab_neostim)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.gridLayout_6 = QGridLayout(self.groupBox_4)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.neostim_refresh_serial_devices = QToolButton(self.groupBox_4)
        self.neostim_refresh_serial_devices.setObjectName(u"neostim_refresh_serial_devices")

        self.gridLayout_6.addWidget(self.neostim_refresh_serial_devices, 0, 2, 1, 1)

        self.label_17 = QLabel(self.groupBox_4)
        self.label_17.setObjectName(u"label_17")

        self.gridLayout_6.addWidget(self.label_17, 0, 0, 1, 1)

        self.neostim_port = QComboBox(self.groupBox_4)
        self.neostim_port.setObjectName(u"neostim_port")
        sizePolicy.setHeightForWidth(self.neostim_port.sizePolicy().hasHeightForWidth())
        self.neostim_port.setSizePolicy(sizePolicy)

        self.gridLayout_6.addWidget(self.neostim_port, 0, 1, 1, 1)


        self.verticalLayout_8.addWidget(self.groupBox_4)

        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_8.addItem(self.verticalSpacer_5)

        self.tabWidget.addTab(self.tab_neostim, "")
        self.tab_media_settings = QWidget()
        self.tab_media_settings.setObjectName(u"tab_media_settings")
        self.verticalLayout_6 = QVBoxLayout(self.tab_media_settings)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.groupBox_3 = QGroupBox(self.tab_media_settings)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.gridLayout = QGridLayout(self.groupBox_3)
        self.gridLayout.setObjectName(u"gridLayout")
        self.mpc_address = QLineEdit(self.groupBox_3)
        self.mpc_address.setObjectName(u"mpc_address")

        self.gridLayout.addWidget(self.mpc_address, 0, 1, 1, 1)

        self.label_31 = QLabel(self.groupBox_3)
        self.label_31.setObjectName(u"label_31")

        self.gridLayout.addWidget(self.label_31, 0, 0, 1, 1)

        self.mpc_reload = QToolButton(self.groupBox_3)
        self.mpc_reload.setObjectName(u"mpc_reload")
        icon = QIcon()
        icon.addFile(u":/restim/arrow-round_poly.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.mpc_reload.setIcon(icon)

        self.gridLayout.addWidget(self.mpc_reload, 0, 2, 1, 1)


        self.verticalLayout_6.addWidget(self.groupBox_3)

        self.groupBox_6 = QGroupBox(self.tab_media_settings)
        self.groupBox_6.setObjectName(u"groupBox_6")
        self.gridLayout_3 = QGridLayout(self.groupBox_6)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.label_32 = QLabel(self.groupBox_6)
        self.label_32.setObjectName(u"label_32")

        self.gridLayout_3.addWidget(self.label_32, 0, 0, 1, 1)

        self.heresphere_address = QLineEdit(self.groupBox_6)
        self.heresphere_address.setObjectName(u"heresphere_address")

        self.gridLayout_3.addWidget(self.heresphere_address, 0, 1, 1, 1)

        self.heresphere_reload = QToolButton(self.groupBox_6)
        self.heresphere_reload.setObjectName(u"heresphere_reload")
        self.heresphere_reload.setIcon(icon)

        self.gridLayout_3.addWidget(self.heresphere_reload, 0, 2, 1, 1)


        self.verticalLayout_6.addWidget(self.groupBox_6)

        self.groupBox_7 = QGroupBox(self.tab_media_settings)
        self.groupBox_7.setObjectName(u"groupBox_7")
        self.gridLayout_4 = QGridLayout(self.groupBox_7)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.vlc_reload = QToolButton(self.groupBox_7)
        self.vlc_reload.setObjectName(u"vlc_reload")
        self.vlc_reload.setIcon(icon)

        self.gridLayout_4.addWidget(self.vlc_reload, 0, 2, 1, 1)

        self.label_33 = QLabel(self.groupBox_7)
        self.label_33.setObjectName(u"label_33")

        self.gridLayout_4.addWidget(self.label_33, 0, 0, 1, 1)

        self.vlc_address = QLineEdit(self.groupBox_7)
        self.vlc_address.setObjectName(u"vlc_address")

        self.gridLayout_4.addWidget(self.vlc_address, 0, 1, 1, 1)

        self.label_34 = QLabel(self.groupBox_7)
        self.label_34.setObjectName(u"label_34")

        self.gridLayout_4.addWidget(self.label_34, 1, 0, 1, 1)

        self.widget = QWidget(self.groupBox_7)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout_2 = QHBoxLayout(self.widget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.vlc_username = QLineEdit(self.widget)
        self.vlc_username.setObjectName(u"vlc_username")

        self.horizontalLayout_2.addWidget(self.vlc_username)

        self.vlc_password = QLineEdit(self.widget)
        self.vlc_password.setObjectName(u"vlc_password")

        self.horizontalLayout_2.addWidget(self.vlc_password)


        self.gridLayout_4.addWidget(self.widget, 1, 1, 1, 1)


        self.verticalLayout_6.addWidget(self.groupBox_7)

        self.groupBox_2 = QGroupBox(self.tab_media_settings)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.gridLayout_2 = QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.kodi_address = QLineEdit(self.groupBox_2)
        self.kodi_address.setObjectName(u"kodi_address")

        self.gridLayout_2.addWidget(self.kodi_address, 0, 1, 1, 1)

        self.label_13 = QLabel(self.groupBox_2)
        self.label_13.setObjectName(u"label_13")

        self.gridLayout_2.addWidget(self.label_13, 0, 0, 1, 1)

        self.kodi_reload = QToolButton(self.groupBox_2)
        self.kodi_reload.setObjectName(u"kodi_reload")
        self.kodi_reload.setIcon(icon)

        self.gridLayout_2.addWidget(self.kodi_reload, 0, 2, 1, 1)


        self.verticalLayout_6.addWidget(self.groupBox_2)

        self.verticalSpacer_6 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer_6)

        self.tabWidget.addTab(self.tab_media_settings, "")
        self.tab_display = QWidget()
        self.tab_display.setObjectName(u"tab_display")
        self.verticalLayout_4 = QVBoxLayout(self.tab_display)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.groupBox_5 = QGroupBox(self.tab_display)
        self.groupBox_5.setObjectName(u"groupBox_5")
        self.groupBox_5.setEnabled(True)
        self.formLayout_5 = QFormLayout(self.groupBox_5)
        self.formLayout_5.setObjectName(u"formLayout_5")
        self.label_2 = QLabel(self.groupBox_5)
        self.label_2.setObjectName(u"label_2")

        self.formLayout_5.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.label_5 = QLabel(self.groupBox_5)
        self.label_5.setObjectName(u"label_5")

        self.formLayout_5.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_5)

        self.display_fps = QSpinBox(self.groupBox_5)
        self.display_fps.setObjectName(u"display_fps")
        self.display_fps.setMaximum(1000)

        self.formLayout_5.setWidget(0, QFormLayout.ItemRole.FieldRole, self.display_fps)

        self.display_latency_ms = QDoubleSpinBox(self.groupBox_5)
        self.display_latency_ms.setObjectName(u"display_latency_ms")
        self.display_latency_ms.setMaximum(1000.000000000000000)

        self.formLayout_5.setWidget(1, QFormLayout.ItemRole.FieldRole, self.display_latency_ms)


        self.verticalLayout_4.addWidget(self.groupBox_5)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer_2)

        self.tabWidget.addTab(self.tab_display, "")
        self.tab_funscript = QWidget()
        self.tab_funscript.setObjectName(u"tab_funscript")
        self.verticalLayout_7 = QVBoxLayout(self.tab_funscript)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.tableView = TableViewWithComboBox(self.tab_funscript)
        self.tableView.setObjectName(u"tableView")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.tableView.sizePolicy().hasHeightForWidth())
        self.tableView.setSizePolicy(sizePolicy1)

        self.verticalLayout_7.addWidget(self.tableView)

        self.frame = QFrame(self.tab_funscript)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.button_funscript_reset_defaults = QPushButton(self.frame)
        self.button_funscript_reset_defaults.setObjectName(u"button_funscript_reset_defaults")

        self.horizontalLayout.addWidget(self.button_funscript_reset_defaults)


        self.verticalLayout_7.addWidget(self.frame)

        self.tabWidget.addTab(self.tab_funscript, "")
        self.tab_patterns = QWidget()
        self.tab_patterns.setObjectName(u"tab_patterns")
        self.verticalLayout_9 = QVBoxLayout(self.tab_patterns)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.label_19 = QLabel(self.tab_patterns)
        self.label_19.setObjectName(u"label_19")
        self.label_19.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_19.setMargin(10)

        self.verticalLayout_9.addWidget(self.label_19)

        self.frame_9 = QFrame(self.tab_patterns)
        self.frame_9.setObjectName(u"frame_9")
        self.frame_9.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame_9.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_9)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.button_patterns_enable_all = QPushButton(self.frame_9)
        self.button_patterns_enable_all.setObjectName(u"button_patterns_enable_all")

        self.horizontalLayout_3.addWidget(self.button_patterns_enable_all)

        self.button_patterns_disable_all = QPushButton(self.frame_9)
        self.button_patterns_disable_all.setObjectName(u"button_patterns_disable_all")

        self.horizontalLayout_3.addWidget(self.button_patterns_disable_all)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)


        self.verticalLayout_9.addWidget(self.frame_9)

        self.patterns_table = QTableWidget(self.tab_patterns)
        if (self.patterns_table.columnCount() < 2):
            self.patterns_table.setColumnCount(2)
        __qtablewidgetitem = QTableWidgetItem()
        self.patterns_table.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.patterns_table.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        self.patterns_table.setObjectName(u"patterns_table")
        self.patterns_table.setAlternatingRowColors(True)
        self.patterns_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.patterns_table.verticalHeader().setVisible(False)

        self.verticalLayout_9.addWidget(self.patterns_table)

        self.tabWidget.addTab(self.tab_patterns, "")

        self.verticalLayout.addWidget(self.tabWidget)

        self.buttonBox = QDialogButtonBox(PreferencesDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Apply|QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)

        QWidget.setTabOrder(self.udp_localhost_only, self.display_fps)
        QWidget.setTabOrder(self.display_fps, self.display_latency_ms)
        QWidget.setTabOrder(self.display_latency_ms, self.audio_api)
        QWidget.setTabOrder(self.audio_api, self.audio_output_device)
        QWidget.setTabOrder(self.audio_output_device, self.gb_websocket_server)
        QWidget.setTabOrder(self.gb_websocket_server, self.websocket_localhost_only)
        QWidget.setTabOrder(self.websocket_localhost_only, self.gb_tcp_server)
        QWidget.setTabOrder(self.gb_tcp_server, self.tcp_localhost_only)
        QWidget.setTabOrder(self.tcp_localhost_only, self.gb_udp_server)

        self.retranslateUi(PreferencesDialog)

        self.tabWidget.setCurrentIndex(2)


        QMetaObject.connectSlotsByName(PreferencesDialog)
    # setupUi

    def retranslateUi(self, PreferencesDialog):
        PreferencesDialog.setWindowTitle(QCoreApplication.translate("PreferencesDialog", u"Preferences", None))
        self.gb_websocket_server.setTitle(QCoreApplication.translate("PreferencesDialog", u"Websocket server", None))
        self.label.setText(QCoreApplication.translate("PreferencesDialog", u"Port", None))
        self.label_6.setText(QCoreApplication.translate("PreferencesDialog", u"Localhost only", None))
        self.websocket_localhost_only.setText("")
        self.gb_tcp_server.setTitle(QCoreApplication.translate("PreferencesDialog", u"TCP server", None))
        self.label_3.setText(QCoreApplication.translate("PreferencesDialog", u"Port", None))
        self.label_10.setText(QCoreApplication.translate("PreferencesDialog", u"Localhost only", None))
        self.tcp_localhost_only.setText("")
        self.gb_udp_server.setTitle(QCoreApplication.translate("PreferencesDialog", u"UDP server", None))
        self.label_4.setText(QCoreApplication.translate("PreferencesDialog", u"Port", None))
        self.label_11.setText(QCoreApplication.translate("PreferencesDialog", u"Localhost only", None))
        self.udp_localhost_only.setText("")
        self.gb_serial.setTitle(QCoreApplication.translate("PreferencesDialog", u"Serial port", None))
        self.label_23.setText(QCoreApplication.translate("PreferencesDialog", u"COM port", None))
        self.label_24.setText(QCoreApplication.translate("PreferencesDialog", u"generate beta axis", None))
        self.serial_auto_expand.setText("")
        self.gb_buttplug_wsdm.setTitle(QCoreApplication.translate("PreferencesDialog", u"Buttplug (WSDM)", None))
        self.label_25.setText(QCoreApplication.translate("PreferencesDialog", u"address", None))
        self.label_26.setText(QCoreApplication.translate("PreferencesDialog", u"generate beta axis", None))
        self.buttplug_wsdm_auto_expand.setText("")
        self.label_12.setText(QCoreApplication.translate("PreferencesDialog", u"Changes require restart", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_network), QCoreApplication.translate("PreferencesDialog", u"Network", None))
        self.groupBox.setTitle(QCoreApplication.translate("PreferencesDialog", u"Audio", None))
        self.label_7.setText(QCoreApplication.translate("PreferencesDialog", u"Audio API", None))
        self.label_8.setText(QCoreApplication.translate("PreferencesDialog", u"Output Device", None))
        self.label_9.setText(QCoreApplication.translate("PreferencesDialog", u"Latency", None))
        self.audio_latency.setItemText(0, QCoreApplication.translate("PreferencesDialog", u"high", None))
        self.audio_latency.setItemText(1, QCoreApplication.translate("PreferencesDialog", u"low", None))
        self.audio_latency.setItemText(2, QCoreApplication.translate("PreferencesDialog", u"0.00", None))
        self.audio_latency.setItemText(3, QCoreApplication.translate("PreferencesDialog", u"0.02", None))
        self.audio_latency.setItemText(4, QCoreApplication.translate("PreferencesDialog", u"0.04", None))
        self.audio_latency.setItemText(5, QCoreApplication.translate("PreferencesDialog", u"0.06", None))
        self.audio_latency.setItemText(6, QCoreApplication.translate("PreferencesDialog", u"0.08", None))
        self.audio_latency.setItemText(7, QCoreApplication.translate("PreferencesDialog", u"0.10", None))
        self.audio_latency.setItemText(8, QCoreApplication.translate("PreferencesDialog", u"0.12", None))
        self.audio_latency.setItemText(9, QCoreApplication.translate("PreferencesDialog", u"0.14", None))
        self.audio_latency.setItemText(10, QCoreApplication.translate("PreferencesDialog", u"0.16", None))
        self.audio_latency.setItemText(11, QCoreApplication.translate("PreferencesDialog", u"0.18", None))
        self.audio_latency.setItemText(12, QCoreApplication.translate("PreferencesDialog", u"0.20", None))

        self.label_27.setText(QCoreApplication.translate("PreferencesDialog", u"Info", None))
        self.audio_info.setText(QCoreApplication.translate("PreferencesDialog", u"TextLabel", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_audio), QCoreApplication.translate("PreferencesDialog", u"Audio", None))
        self.groupBox_8.setTitle(QCoreApplication.translate("PreferencesDialog", u"FOC-Stim", None))
        self.focstim_use_teleplot.setText("")
#if QT_CONFIG(tooltip)
        self.label_16.setToolTip(QCoreApplication.translate("PreferencesDialog", u"Useful if you have multiple FOC-Stim boxes", None))
#endif // QT_CONFIG(tooltip)
        self.label_16.setText(QCoreApplication.translate("PreferencesDialog", u"teleplot prefix (?)", None))
        self.refresh_serial_devices.setText(QCoreApplication.translate("PreferencesDialog", u"Refresh", None))
        self.label_18.setText(QCoreApplication.translate("PreferencesDialog", u"Dump notifications to file", None))
        self.label_15.setText(QCoreApplication.translate("PreferencesDialog", u"Use teleplot", None))
        self.label_14.setText(QCoreApplication.translate("PreferencesDialog", u"Serial port", None))
        self.focstim_dump_notifications.setText("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_foc), QCoreApplication.translate("PreferencesDialog", u"FOC-Stim", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("PreferencesDialog", u"NeoStim", None))
        self.neostim_refresh_serial_devices.setText(QCoreApplication.translate("PreferencesDialog", u"Refresh", None))
        self.label_17.setText(QCoreApplication.translate("PreferencesDialog", u"Serial port", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_neostim), QCoreApplication.translate("PreferencesDialog", u"NeoStim", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("PreferencesDialog", u"MPC-HC", None))
        self.label_31.setText(QCoreApplication.translate("PreferencesDialog", u"address:port", None))
        self.mpc_reload.setText(QCoreApplication.translate("PreferencesDialog", u"...", None))
        self.groupBox_6.setTitle(QCoreApplication.translate("PreferencesDialog", u"HereSphere", None))
        self.label_32.setText(QCoreApplication.translate("PreferencesDialog", u"address:port", None))
        self.heresphere_reload.setText(QCoreApplication.translate("PreferencesDialog", u"...", None))
        self.groupBox_7.setTitle(QCoreApplication.translate("PreferencesDialog", u"VLC", None))
        self.vlc_reload.setText(QCoreApplication.translate("PreferencesDialog", u"...", None))
        self.label_33.setText(QCoreApplication.translate("PreferencesDialog", u"address:port", None))
        self.label_34.setText(QCoreApplication.translate("PreferencesDialog", u"user/password", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("PreferencesDialog", u"Kodi", None))
        self.label_13.setText(QCoreApplication.translate("PreferencesDialog", u"address:port", None))
        self.kodi_reload.setText(QCoreApplication.translate("PreferencesDialog", u"...", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_media_settings), QCoreApplication.translate("PreferencesDialog", u"Media sync", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("PreferencesDialog", u"Phase", None))
        self.label_2.setText(QCoreApplication.translate("PreferencesDialog", u"max fps", None))
        self.label_5.setText(QCoreApplication.translate("PreferencesDialog", u"display latency [ms]", None))
        self.display_latency_ms.setSuffix("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_display), QCoreApplication.translate("PreferencesDialog", u"Display", None))
        self.button_funscript_reset_defaults.setText(QCoreApplication.translate("PreferencesDialog", u"Reset all to defaults", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_funscript), QCoreApplication.translate("PreferencesDialog", u"Funscript / T-Code", None))
        self.label_19.setText(QCoreApplication.translate("PreferencesDialog", u"<html><head/><body><p><span style=\" font-size:12pt; font-weight:700;\">Threephase patterns</span></p></body></html>", None))
        self.button_patterns_enable_all.setText(QCoreApplication.translate("PreferencesDialog", u"Enable All", None))
        self.button_patterns_disable_all.setText(QCoreApplication.translate("PreferencesDialog", u"Disable All", None))
        ___qtablewidgetitem = self.patterns_table.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("PreferencesDialog", u"Pattern", None));
        ___qtablewidgetitem1 = self.patterns_table.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("PreferencesDialog", u"Enabled", None));
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_patterns), QCoreApplication.translate("PreferencesDialog", u"Patterns", None))
    # retranslateUi

