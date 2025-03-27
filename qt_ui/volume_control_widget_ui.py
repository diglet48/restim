# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'volumecontrolwidget.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QDoubleSpinBox, QFormLayout,
    QGroupBox, QLabel, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_VolumeControlForm(object):
    def setupUi(self, VolumeControlForm):
        if not VolumeControlForm.objectName():
            VolumeControlForm.setObjectName(u"VolumeControlForm")
        VolumeControlForm.resize(496, 518)
        self.verticalLayout = QVBoxLayout(VolumeControlForm)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(VolumeControlForm)
        self.groupBox.setObjectName(u"groupBox")
        self.formLayout_2 = QFormLayout(self.groupBox)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.label_volume = QLabel(self.groupBox)
        self.label_volume.setObjectName(u"label_volume")

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.label_volume)

        self.label_target_volume = QLabel(self.groupBox)
        self.label_target_volume.setObjectName(u"label_target_volume")

        self.formLayout_2.setWidget(1, QFormLayout.LabelRole, self.label_target_volume)

        self.doubleSpinBox_target_volume = QDoubleSpinBox(self.groupBox)
        self.doubleSpinBox_target_volume.setObjectName(u"doubleSpinBox_target_volume")
        self.doubleSpinBox_target_volume.setMaximum(100.000000000000000)
        self.doubleSpinBox_target_volume.setSingleStep(0.100000000000000)
        self.doubleSpinBox_target_volume.setValue(100.000000000000000)

        self.formLayout_2.setWidget(1, QFormLayout.FieldRole, self.doubleSpinBox_target_volume)

        self.label_rate = QLabel(self.groupBox)
        self.label_rate.setObjectName(u"label_rate")

        self.formLayout_2.setWidget(2, QFormLayout.LabelRole, self.label_rate)

        self.doubleSpinBox_rate = QDoubleSpinBox(self.groupBox)
        self.doubleSpinBox_rate.setObjectName(u"doubleSpinBox_rate")
        self.doubleSpinBox_rate.setMaximum(10000.000000000000000)
        self.doubleSpinBox_rate.setSingleStep(0.100000000000000)
        self.doubleSpinBox_rate.setValue(1.000000000000000)

        self.formLayout_2.setWidget(2, QFormLayout.FieldRole, self.doubleSpinBox_rate)

        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.formLayout_2.setWidget(3, QFormLayout.LabelRole, self.label)

        self.checkBox_ramp_enabled = QCheckBox(self.groupBox)
        self.checkBox_ramp_enabled.setObjectName(u"checkBox_ramp_enabled")

        self.formLayout_2.setWidget(3, QFormLayout.FieldRole, self.checkBox_ramp_enabled)

        self.label_6 = QLabel(self.groupBox)
        self.label_6.setObjectName(u"label_6")

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.label_6)


        self.verticalLayout.addWidget(self.groupBox)

        self.groupBox_2 = QGroupBox(VolumeControlForm)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.formLayout = QFormLayout(self.groupBox_2)
        self.formLayout.setObjectName(u"formLayout")
        self.label_2 = QLabel(self.groupBox_2)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_2)

        self.doubleSpinBox_inactivity_threshold = QDoubleSpinBox(self.groupBox_2)
        self.doubleSpinBox_inactivity_threshold.setObjectName(u"doubleSpinBox_inactivity_threshold")
        self.doubleSpinBox_inactivity_threshold.setMaximum(100.000000000000000)
        self.doubleSpinBox_inactivity_threshold.setSingleStep(0.100000000000000)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.doubleSpinBox_inactivity_threshold)

        self.label_3 = QLabel(self.groupBox_2)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_3)

        self.doubleSpinBox_inactivity_volume = QDoubleSpinBox(self.groupBox_2)
        self.doubleSpinBox_inactivity_volume.setObjectName(u"doubleSpinBox_inactivity_volume")
        self.doubleSpinBox_inactivity_volume.setMaximum(100.000000000000000)
        self.doubleSpinBox_inactivity_volume.setSingleStep(0.100000000000000)

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.doubleSpinBox_inactivity_volume)

        self.label_4 = QLabel(self.groupBox_2)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_4)

        self.doubleSpinBox_inactivity_ramp_time = QDoubleSpinBox(self.groupBox_2)
        self.doubleSpinBox_inactivity_ramp_time.setObjectName(u"doubleSpinBox_inactivity_ramp_time")
        self.doubleSpinBox_inactivity_ramp_time.setMaximum(100.000000000000000)
        self.doubleSpinBox_inactivity_ramp_time.setSingleStep(0.100000000000000)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.doubleSpinBox_inactivity_ramp_time)


        self.verticalLayout.addWidget(self.groupBox_2)

        self.groupBox_4 = QGroupBox(VolumeControlForm)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.formLayout_4 = QFormLayout(self.groupBox_4)
        self.formLayout_4.setObjectName(u"formLayout_4")
        self.label_7 = QLabel(self.groupBox_4)
        self.label_7.setObjectName(u"label_7")

        self.formLayout_4.setWidget(0, QFormLayout.LabelRole, self.label_7)

        self.doubleSpinBox_slow_start = QDoubleSpinBox(self.groupBox_4)
        self.doubleSpinBox_slow_start.setObjectName(u"doubleSpinBox_slow_start")
        self.doubleSpinBox_slow_start.setDecimals(1)
        self.doubleSpinBox_slow_start.setMaximum(100.000000000000000)
        self.doubleSpinBox_slow_start.setSingleStep(0.100000000000000)
        self.doubleSpinBox_slow_start.setValue(1.000000000000000)

        self.formLayout_4.setWidget(0, QFormLayout.FieldRole, self.doubleSpinBox_slow_start)


        self.verticalLayout.addWidget(self.groupBox_4)

        self.groupBox_3 = QGroupBox(VolumeControlForm)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.formLayout_3 = QFormLayout(self.groupBox_3)
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.label_5 = QLabel(self.groupBox_3)
        self.label_5.setObjectName(u"label_5")

        self.formLayout_3.setWidget(0, QFormLayout.LabelRole, self.label_5)

        self.doubleSpinBox_tau = QDoubleSpinBox(self.groupBox_3)
        self.doubleSpinBox_tau.setObjectName(u"doubleSpinBox_tau")
        self.doubleSpinBox_tau.setDecimals(0)
        self.doubleSpinBox_tau.setMinimum(0.000000000000000)
        self.doubleSpinBox_tau.setMaximum(1000.000000000000000)
        self.doubleSpinBox_tau.setValue(355.000000000000000)

        self.formLayout_3.setWidget(0, QFormLayout.FieldRole, self.doubleSpinBox_tau)


        self.verticalLayout.addWidget(self.groupBox_3)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        QWidget.setTabOrder(self.doubleSpinBox_target_volume, self.doubleSpinBox_rate)
        QWidget.setTabOrder(self.doubleSpinBox_rate, self.checkBox_ramp_enabled)
        QWidget.setTabOrder(self.checkBox_ramp_enabled, self.doubleSpinBox_inactivity_threshold)
        QWidget.setTabOrder(self.doubleSpinBox_inactivity_threshold, self.doubleSpinBox_inactivity_ramp_time)
        QWidget.setTabOrder(self.doubleSpinBox_inactivity_ramp_time, self.doubleSpinBox_inactivity_volume)

        self.retranslateUi(VolumeControlForm)

        QMetaObject.connectSlotsByName(VolumeControlForm)
    # setupUi

    def retranslateUi(self, VolumeControlForm):
        VolumeControlForm.setWindowTitle(QCoreApplication.translate("VolumeControlForm", u"Form", None))
        self.groupBox.setTitle(QCoreApplication.translate("VolumeControlForm", u"Volume ramp", None))
        self.label_volume.setText(QCoreApplication.translate("VolumeControlForm", u"Volume [%]", None))
        self.label_target_volume.setText(QCoreApplication.translate("VolumeControlForm", u"Target volume [%]", None))
        self.label_rate.setText(QCoreApplication.translate("VolumeControlForm", u"Rate [% / min]", None))
        self.label.setText(QCoreApplication.translate("VolumeControlForm", u"Enable", None))
        self.checkBox_ramp_enabled.setText("")
        self.label_6.setText(QCoreApplication.translate("VolumeControlForm", u"<html><head/><body><p><span style=\" font-style:italic;\">(moved to sidebar)</span></p></body></html>", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("VolumeControlForm", u"Lower volume during pauses", None))
        self.label_2.setText(QCoreApplication.translate("VolumeControlForm", u"Inactivity threshold [seconds]", None))
        self.label_3.setText(QCoreApplication.translate("VolumeControlForm", u"Reduce volume by [%]", None))
        self.label_4.setText(QCoreApplication.translate("VolumeControlForm", u"Ramp time [seconds]", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("VolumeControlForm", u"Slow start", None))
        self.label_7.setText(QCoreApplication.translate("VolumeControlForm", u"Ramp time [seconds]", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("VolumeControlForm", u"Volume-frequency adjustment (FOC-Stim only)", None))
#if QT_CONFIG(tooltip)
        self.label_5.setToolTip(QCoreApplication.translate("VolumeControlForm", u"<html><head/><body><p>Available on FOC-Stim only. Time constant of the nerves. </p><p>Automatically adjusts the volume when the carrier frequency changes.</p><p>Increase if lower frequencies feel too strong.</p><p>default = 355\u00b5s</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_5.setText(QCoreApplication.translate("VolumeControlForm", u"Tau [\u00b5s] (?)", None))
    # retranslateUi

