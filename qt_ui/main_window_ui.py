# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.8.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QDoubleSpinBox, QFrame,
    QGroupBox, QHBoxLayout, QLabel, QMainWindow,
    QMenu, QMenuBar, QSizePolicy, QSpacerItem,
    QStackedWidget, QTabWidget, QToolBar, QVBoxLayout,
    QWidget)

from qt_ui.ab_test_widget import ABTestWidget
from qt_ui.carrier_settings_widget import CarrierSettingsWidget
from qt_ui.media_settings_widget import MediaSettingsWidget
from qt_ui.neostim_settings_widget import NeoStimSettingsWidget
from qt_ui.pulse_settings_widget import PulseSettingsWidget
from qt_ui.three_phase_settings_widget import ThreePhaseSettingsWidget
from qt_ui.vibration_settings_widget import VibrationSettingsWidget
from qt_ui.volume_control_widget import VolumeControlWidget
from qt_ui.waveform_details_widget import WaveformDetailsWidget
from qt_ui.widgets.phase_widget import (PhaseWidgetAlphaBeta, PhaseWidgetFocus)
from qt_ui.widgets.volume_widget import VolumeWidget
import restim_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(848, 635)
        icon = QIcon()
        icon.addFile(u"../../../.designer/resources/favicon.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        MainWindow.setWindowIcon(icon)
        self.actionFunscript_conversion = QAction(MainWindow)
        self.actionFunscript_conversion.setObjectName(u"actionFunscript_conversion")
        self.actionPreferences = QAction(MainWindow)
        self.actionPreferences.setObjectName(u"actionPreferences")
        self.actionDevice_selection_wizard = QAction(MainWindow)
        self.actionDevice_selection_wizard.setObjectName(u"actionDevice_selection_wizard")
        self.actionControl = QAction(MainWindow)
        self.actionControl.setObjectName(u"actionControl")
        self.actionControl.setCheckable(True)
        self.actionControl.setChecked(True)
        icon1 = QIcon()
        icon1.addFile(u":/restim/sliders_poly.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionControl.setIcon(icon1)
        self.actionMedia = QAction(MainWindow)
        self.actionMedia.setObjectName(u"actionMedia")
        self.actionMedia.setCheckable(True)
        icon2 = QIcon()
        icon2.addFile(u":/restim/film-1_poly.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionMedia.setIcon(icon2)
        self.actionDevice = QAction(MainWindow)
        self.actionDevice.setObjectName(u"actionDevice")
        self.actionDevice.setCheckable(True)
        icon3 = QIcon()
        icon3.addFile(u":/restim/plug-1_poly.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionDevice.setIcon(icon3)
        self.actionStart = QAction(MainWindow)
        self.actionStart.setObjectName(u"actionStart")
        icon4 = QIcon()
        icon4.addFile(u":/newPrefix/play_poly.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        icon4.addFile(u"../../../.designer/resources/stop-sign_poly.svg", QSize(), QIcon.Mode.Normal, QIcon.State.On)
        self.actionStart.setIcon(icon4)
        self.actionLog = QAction(MainWindow)
        self.actionLog.setObjectName(u"actionLog")
        self.actionLog.setCheckable(True)
        icon5 = QIcon()
        icon5.addFile(u":/restim/docs-1_poly.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionLog.setIcon(icon5)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.page_control = QWidget()
        self.page_control.setObjectName(u"page_control")
        self.horizontalLayout_2 = QHBoxLayout(self.page_control)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.frame = QFrame(self.page_control)
        self.frame.setObjectName(u"frame")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.graphicsView = PhaseWidgetAlphaBeta(self.frame)
        self.graphicsView.setObjectName(u"graphicsView")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.graphicsView.sizePolicy().hasHeightForWidth())
        self.graphicsView.setSizePolicy(sizePolicy1)
        self.graphicsView.setMinimumSize(QSize(200, 200))
        self.graphicsView.setMaximumSize(QSize(200, 200))

        self.verticalLayout.addWidget(self.graphicsView)

        self.groupBox_3 = QGroupBox(self.frame)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.verticalLayout_7 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.progressBar_volume = VolumeWidget(self.groupBox_3)
        self.progressBar_volume.setObjectName(u"progressBar_volume")
        self.progressBar_volume.setValue(24)

        self.verticalLayout_7.addWidget(self.progressBar_volume)

        self.doubleSpinBox_volume = QDoubleSpinBox(self.groupBox_3)
        self.doubleSpinBox_volume.setObjectName(u"doubleSpinBox_volume")
        self.doubleSpinBox_volume.setDecimals(2)
        self.doubleSpinBox_volume.setMaximum(100.000000000000000)
        self.doubleSpinBox_volume.setSingleStep(0.100000000000000)

        self.verticalLayout_7.addWidget(self.doubleSpinBox_volume)


        self.verticalLayout.addWidget(self.groupBox_3)

        self.groupBox = QGroupBox(self.frame)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.comboBox_patternSelect = QComboBox(self.groupBox)
        self.comboBox_patternSelect.addItem("")
        self.comboBox_patternSelect.addItem("")
        self.comboBox_patternSelect.addItem("")
        self.comboBox_patternSelect.addItem("")
        self.comboBox_patternSelect.addItem("")
        self.comboBox_patternSelect.setObjectName(u"comboBox_patternSelect")

        self.verticalLayout_2.addWidget(self.comboBox_patternSelect)

        self.doubleSpinBox = QDoubleSpinBox(self.groupBox)
        self.doubleSpinBox.setObjectName(u"doubleSpinBox")
        self.doubleSpinBox.setSingleStep(0.100000000000000)
        self.doubleSpinBox.setValue(1.000000000000000)

        self.verticalLayout_2.addWidget(self.doubleSpinBox)


        self.verticalLayout.addWidget(self.groupBox)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.horizontalLayout_2.addWidget(self.frame)

        self.tabWidget = QTabWidget(self.page_control)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setEnabled(True)
        self.tab_threephase = ThreePhaseSettingsWidget()
        self.tab_threephase.setObjectName(u"tab_threephase")
        self.tabWidget.addTab(self.tab_threephase, "")
        self.tab_focus = QWidget()
        self.tab_focus.setObjectName(u"tab_focus")
        self.tab_focus.setEnabled(True)
        self.graphicsView_focus = PhaseWidgetFocus(self.tab_focus)
        self.graphicsView_focus.setObjectName(u"graphicsView_focus")
        self.graphicsView_focus.setGeometry(QRect(60, 50, 256, 192))
        self.tabWidget.addTab(self.tab_focus, "")
        self.tab_carrier = CarrierSettingsWidget()
        self.tab_carrier.setObjectName(u"tab_carrier")
        self.tabWidget.addTab(self.tab_carrier, "")
        self.tab_pulse_settings = PulseSettingsWidget()
        self.tab_pulse_settings.setObjectName(u"tab_pulse_settings")
        self.tabWidget.addTab(self.tab_pulse_settings, "")
        self.tab_neostim = NeoStimSettingsWidget()
        self.tab_neostim.setObjectName(u"tab_neostim")
        self.tabWidget.addTab(self.tab_neostim, "")
        self.tab_a_b_testing = ABTestWidget()
        self.tab_a_b_testing.setObjectName(u"tab_a_b_testing")
        self.tabWidget.addTab(self.tab_a_b_testing, "")
        self.tab_volume = VolumeControlWidget()
        self.tab_volume.setObjectName(u"tab_volume")
        self.verticalLayout_6 = QVBoxLayout(self.tab_volume)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 6)
        self.tabWidget.addTab(self.tab_volume, "")
        self.tab_vibrate = VibrationSettingsWidget()
        self.tab_vibrate.setObjectName(u"tab_vibrate")
        self.tabWidget.addTab(self.tab_vibrate, "")
        self.tab_details = WaveformDetailsWidget()
        self.tab_details.setObjectName(u"tab_details")
        self.tabWidget.addTab(self.tab_details, "")

        self.horizontalLayout_2.addWidget(self.tabWidget)

        self.stackedWidget.addWidget(self.page_control)
        self.page_media = MediaSettingsWidget()
        self.page_media.setObjectName(u"page_media")
        self.stackedWidget.addWidget(self.page_media)
        self.page_device = QWidget()
        self.page_device.setObjectName(u"page_device")
        self.label_3 = QLabel(self.page_device)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(100, 90, 261, 31))
        self.stackedWidget.addWidget(self.page_device)
        self.page_log = QWidget()
        self.page_log.setObjectName(u"page_log")
        self.label_2 = QLabel(self.page_log)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(80, 70, 221, 31))
        self.stackedWidget.addWidget(self.page_log)

        self.horizontalLayout.addWidget(self.stackedWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 848, 33))
        self.menuTools = QMenu(self.menuBar)
        self.menuTools.setObjectName(u"menuTools")
        MainWindow.setMenuBar(self.menuBar)
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName(u"toolBar")
        self.toolBar.setMovable(False)
        self.toolBar.setIconSize(QSize(65, 48))
        self.toolBar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        MainWindow.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.toolBar)

        self.menuBar.addAction(self.menuTools.menuAction())
        self.menuTools.addAction(self.actionDevice_selection_wizard)
        self.menuTools.addAction(self.actionFunscript_conversion)
        self.menuTools.addAction(self.actionPreferences)
        self.toolBar.addAction(self.actionControl)
        self.toolBar.addAction(self.actionMedia)
        self.toolBar.addAction(self.actionStart)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(0)
        self.tabWidget.setCurrentIndex(4)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"restim", None))
        self.actionFunscript_conversion.setText(QCoreApplication.translate("MainWindow", u"Funscript conversion (1d -> 2d)", None))
        self.actionPreferences.setText(QCoreApplication.translate("MainWindow", u"Preferences", None))
        self.actionDevice_selection_wizard.setText(QCoreApplication.translate("MainWindow", u"Device selection", None))
        self.actionControl.setText(QCoreApplication.translate("MainWindow", u"Live Control", None))
#if QT_CONFIG(shortcut)
        self.actionControl.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+1", None))
#endif // QT_CONFIG(shortcut)
        self.actionMedia.setText(QCoreApplication.translate("MainWindow", u"Sync Media", None))
#if QT_CONFIG(shortcut)
        self.actionMedia.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+2", None))
#endif // QT_CONFIG(shortcut)
        self.actionDevice.setText(QCoreApplication.translate("MainWindow", u"Device", None))
#if QT_CONFIG(shortcut)
        self.actionDevice.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+3", None))
#endif // QT_CONFIG(shortcut)
        self.actionStart.setText(QCoreApplication.translate("MainWindow", u"Start", None))
        self.actionLog.setText(QCoreApplication.translate("MainWindow", u"Log", None))
#if QT_CONFIG(shortcut)
        self.actionLog.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+4", None))
#endif // QT_CONFIG(shortcut)
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"volume", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Pattern generator", None))
        self.comboBox_patternSelect.setItemText(0, QCoreApplication.translate("MainWindow", u"Mouse", None))
        self.comboBox_patternSelect.setItemText(1, QCoreApplication.translate("MainWindow", u"Circle", None))
        self.comboBox_patternSelect.setItemText(2, QCoreApplication.translate("MainWindow", u"A", None))
        self.comboBox_patternSelect.setItemText(3, QCoreApplication.translate("MainWindow", u"B", None))
        self.comboBox_patternSelect.setItemText(4, QCoreApplication.translate("MainWindow", u"C", None))

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_threephase), QCoreApplication.translate("MainWindow", u"3-phase", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_focus), QCoreApplication.translate("MainWindow", u"Focus", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_carrier), QCoreApplication.translate("MainWindow", u"Carrier settings", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_pulse_settings), QCoreApplication.translate("MainWindow", u"Pulse settings", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_neostim), QCoreApplication.translate("MainWindow", u"NeoStim", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_a_b_testing), QCoreApplication.translate("MainWindow", u"A/B testing", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_volume), QCoreApplication.translate("MainWindow", u"Volume", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_vibrate), QCoreApplication.translate("MainWindow", u"Vibration", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_details), QCoreApplication.translate("MainWindow", u"Details", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Restim doesn't have device configruation yet :(", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Restim doesn't have a log yet :(", None))
        self.menuTools.setTitle(QCoreApplication.translate("MainWindow", u"Tools", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
    # retranslateUi

