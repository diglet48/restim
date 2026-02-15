# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
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
    QGroupBox, QHBoxLayout, QMainWindow, QMenu,
    QMenuBar, QSizePolicy, QSpacerItem, QStackedWidget,
    QTabWidget, QToolBar, QVBoxLayout, QWidget)

from qt_ui.ab_test_widget import ABTestWidget
from qt_ui.carrier_settings_widget import CarrierSettingsWidget
from qt_ui.four_phase_settings_widget import FourPhaseSettingsWidget
from qt_ui.media_settings_widget import MediaSettingsWidget
from qt_ui.neostim_settings_widget import NeoStimSettingsWidget
from qt_ui.pulse_settings_widget import PulseSettingsWidget
from qt_ui.sensors_widget import SensorsWidget
from qt_ui.three_phase_settings_widget import ThreePhaseSettingsWidget
from qt_ui.vibration_settings_widget import VibrationSettingsWidget
from qt_ui.volume_control_widget import VolumeControlWidget
from qt_ui.waveform_details_widget import WaveformDetailsWidget
from qt_ui.widgets.fourphase_widget_individual_electrodes import FourphaseWidgetIndividualElectrodes
from qt_ui.widgets.threephase_widget import ThreephaseWidgetAlphaBeta
from qt_ui.widgets.volume_widget import VolumeWidget
import restim_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(843, 656)
        icon = QIcon()
        icon.addFile(u":/restim/favicon.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
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
        self.actionStart.setCheckable(False)
        icon4 = QIcon()
        icon4.addFile(u":/restim/play_poly.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionStart.setIcon(icon4)
        self.actionLog = QAction(MainWindow)
        self.actionLog.setObjectName(u"actionLog")
        self.actionLog.setCheckable(True)
        icon5 = QIcon()
        icon5.addFile(u":/restim/docs-1_poly.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionLog.setIcon(icon5)
        self.actionSimfile_conversion = QAction(MainWindow)
        self.actionSimfile_conversion.setObjectName(u"actionSimfile_conversion")
        self.actionFunscript_decomposition = QAction(MainWindow)
        self.actionFunscript_decomposition.setObjectName(u"actionFunscript_decomposition")
        self.actionFirmware_updater = QAction(MainWindow)
        self.actionFirmware_updater.setObjectName(u"actionFirmware_updater")
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.actionSensors = QAction(MainWindow)
        self.actionSensors.setObjectName(u"actionSensors")
        self.actionSensors.setCheckable(True)
        icon6 = QIcon()
        icon6.addFile(u":/restim/activity-1_poly.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionSensors.setIcon(icon6)
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
        self.horizontalLayout_2.setContentsMargins(-1, 0, -1, 0)
        self.left_frame = QFrame(self.page_control)
        self.left_frame.setObjectName(u"left_frame")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.left_frame.sizePolicy().hasHeightForWidth())
        self.left_frame.setSizePolicy(sizePolicy)
        self.left_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.left_frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.left_frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.stackedWidget_visual = QStackedWidget(self.left_frame)
        self.stackedWidget_visual.setObjectName(u"stackedWidget_visual")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.stackedWidget_visual.sizePolicy().hasHeightForWidth())
        self.stackedWidget_visual.setSizePolicy(sizePolicy1)
        self.stackedWidget_visual.setMinimumSize(QSize(200, 200))
        self.stackedWidget_visual.setMaximumSize(QSize(200, 200))
        self.stackedWidget_visual.setFrameShape(QFrame.Shape.NoFrame)
        self.stackedWidget_visual.setLineWidth(0)
        self.page_threephase = QWidget()
        self.page_threephase.setObjectName(u"page_threephase")
        self.graphicsView_threephase = ThreephaseWidgetAlphaBeta(self.page_threephase)
        self.graphicsView_threephase.setObjectName(u"graphicsView_threephase")
        self.graphicsView_threephase.setGeometry(QRect(0, 0, 200, 200))
        sizePolicy1.setHeightForWidth(self.graphicsView_threephase.sizePolicy().hasHeightForWidth())
        self.graphicsView_threephase.setSizePolicy(sizePolicy1)
        self.graphicsView_threephase.setMinimumSize(QSize(200, 200))
        self.graphicsView_threephase.setMaximumSize(QSize(200, 200))
        self.stackedWidget_visual.addWidget(self.page_threephase)
        self.page_fourphase = QWidget()
        self.page_fourphase.setObjectName(u"page_fourphase")
        self.graphicsView_fourphase = FourphaseWidgetIndividualElectrodes(self.page_fourphase)
        self.graphicsView_fourphase.setObjectName(u"graphicsView_fourphase")
        self.graphicsView_fourphase.setGeometry(QRect(0, 0, 200, 200))
        self.stackedWidget_visual.addWidget(self.page_fourphase)

        self.verticalLayout.addWidget(self.stackedWidget_visual)

        self.groupBox_volume = QGroupBox(self.left_frame)
        self.groupBox_volume.setObjectName(u"groupBox_volume")
        self.verticalLayout_7 = QVBoxLayout(self.groupBox_volume)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.progressBar_volume = VolumeWidget(self.groupBox_volume)
        self.progressBar_volume.setObjectName(u"progressBar_volume")
        self.progressBar_volume.setValue(24)

        self.verticalLayout_7.addWidget(self.progressBar_volume)

        self.doubleSpinBox_volume = QDoubleSpinBox(self.groupBox_volume)
        self.doubleSpinBox_volume.setObjectName(u"doubleSpinBox_volume")
        self.doubleSpinBox_volume.setKeyboardTracking(False)
        self.doubleSpinBox_volume.setDecimals(2)
        self.doubleSpinBox_volume.setMaximum(100.000000000000000)
        self.doubleSpinBox_volume.setSingleStep(0.100000000000000)

        self.verticalLayout_7.addWidget(self.doubleSpinBox_volume)


        self.verticalLayout.addWidget(self.groupBox_volume)

        self.groupBox_pattern = QGroupBox(self.left_frame)
        self.groupBox_pattern.setObjectName(u"groupBox_pattern")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_pattern)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.comboBox_patternSelect = QComboBox(self.groupBox_pattern)
        self.comboBox_patternSelect.addItem("")
        self.comboBox_patternSelect.addItem("")
        self.comboBox_patternSelect.addItem("")
        self.comboBox_patternSelect.addItem("")
        self.comboBox_patternSelect.addItem("")
        self.comboBox_patternSelect.setObjectName(u"comboBox_patternSelect")

        self.verticalLayout_2.addWidget(self.comboBox_patternSelect)

        self.doubleSpinBox = QDoubleSpinBox(self.groupBox_pattern)
        self.doubleSpinBox.setObjectName(u"doubleSpinBox")
        self.doubleSpinBox.setKeyboardTracking(False)
        self.doubleSpinBox.setSingleStep(0.100000000000000)
        self.doubleSpinBox.setValue(1.000000000000000)

        self.verticalLayout_2.addWidget(self.doubleSpinBox)


        self.verticalLayout.addWidget(self.groupBox_pattern)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.horizontalLayout_2.addWidget(self.left_frame)

        self.tabWidget = QTabWidget(self.page_control)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setEnabled(True)
        self.tab_threephase = ThreePhaseSettingsWidget()
        self.tab_threephase.setObjectName(u"tab_threephase")
        self.tabWidget.addTab(self.tab_threephase, "")
        self.tab_fourphase = FourPhaseSettingsWidget()
        self.tab_fourphase.setObjectName(u"tab_fourphase")
        self.tabWidget.addTab(self.tab_fourphase, "")
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
        self.page_sensors = SensorsWidget()
        self.page_sensors.setObjectName(u"page_sensors")
        self.stackedWidget.addWidget(self.page_sensors)

        self.horizontalLayout.addWidget(self.stackedWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 843, 33))
        self.menuSetup = QMenu(self.menuBar)
        self.menuSetup.setObjectName(u"menuSetup")
        self.menuTools = QMenu(self.menuBar)
        self.menuTools.setObjectName(u"menuTools")
        self.menuHelp = QMenu(self.menuBar)
        self.menuHelp.setObjectName(u"menuHelp")
        MainWindow.setMenuBar(self.menuBar)
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName(u"toolBar")
        self.toolBar.setMovable(False)
        self.toolBar.setIconSize(QSize(65, 48))
        self.toolBar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        MainWindow.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.toolBar)

        self.menuBar.addAction(self.menuSetup.menuAction())
        self.menuBar.addAction(self.menuTools.menuAction())
        self.menuBar.addAction(self.menuHelp.menuAction())
        self.menuSetup.addAction(self.actionDevice_selection_wizard)
        self.menuSetup.addAction(self.actionPreferences)
        self.menuTools.addAction(self.actionFunscript_conversion)
        self.menuTools.addAction(self.actionSimfile_conversion)
        self.menuTools.addAction(self.actionFunscript_decomposition)
        self.menuTools.addSeparator()
        self.menuTools.addAction(self.actionFirmware_updater)
        self.menuHelp.addAction(self.actionAbout)
        self.toolBar.addAction(self.actionControl)
        self.toolBar.addAction(self.actionMedia)
        self.toolBar.addAction(self.actionSensors)
        self.toolBar.addAction(self.actionStart)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(0)
        self.stackedWidget_visual.setCurrentIndex(1)
        self.tabWidget.setCurrentIndex(8)


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
        self.actionSimfile_conversion.setText(QCoreApplication.translate("MainWindow", u"Simfile conversion", None))
        self.actionFunscript_decomposition.setText(QCoreApplication.translate("MainWindow", u"Funscript decomposition", None))
        self.actionFirmware_updater.setText(QCoreApplication.translate("MainWindow", u"Firmware updater", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.actionSensors.setText(QCoreApplication.translate("MainWindow", u"Sensors", None))
#if QT_CONFIG(shortcut)
        self.actionSensors.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+3", None))
#endif // QT_CONFIG(shortcut)
        self.groupBox_volume.setTitle(QCoreApplication.translate("MainWindow", u"volume", None))
        self.groupBox_pattern.setTitle(QCoreApplication.translate("MainWindow", u"Pattern generator", None))
        self.comboBox_patternSelect.setItemText(0, QCoreApplication.translate("MainWindow", u"Mouse", None))
        self.comboBox_patternSelect.setItemText(1, QCoreApplication.translate("MainWindow", u"Circle", None))
        self.comboBox_patternSelect.setItemText(2, QCoreApplication.translate("MainWindow", u"A", None))
        self.comboBox_patternSelect.setItemText(3, QCoreApplication.translate("MainWindow", u"B", None))
        self.comboBox_patternSelect.setItemText(4, QCoreApplication.translate("MainWindow", u"C", None))

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_threephase), QCoreApplication.translate("MainWindow", u"3-phase", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_fourphase), QCoreApplication.translate("MainWindow", u"4-phase", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_carrier), QCoreApplication.translate("MainWindow", u"Carrier settings", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_pulse_settings), QCoreApplication.translate("MainWindow", u"Pulse settings", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_neostim), QCoreApplication.translate("MainWindow", u"NeoStim", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_a_b_testing), QCoreApplication.translate("MainWindow", u"A/B testing", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_volume), QCoreApplication.translate("MainWindow", u"Volume", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_vibrate), QCoreApplication.translate("MainWindow", u"Vibration", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_details), QCoreApplication.translate("MainWindow", u"Details", None))
        self.menuSetup.setTitle(QCoreApplication.translate("MainWindow", u"Setup", None))
        self.menuTools.setTitle(QCoreApplication.translate("MainWindow", u"Tools", None))
        self.menuHelp.setTitle(QCoreApplication.translate("MainWindow", u"Help", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
    # retranslateUi

