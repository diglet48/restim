# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'neostimsettingswidget.ui'
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
    QFrame, QGroupBox, QLabel, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_NeoStimSettingsWidget(object):
    def setupUi(self, NeoStimSettingsWidget):
        if not NeoStimSettingsWidget.objectName():
            NeoStimSettingsWidget.setObjectName(u"NeoStimSettingsWidget")
        NeoStimSettingsWidget.resize(638, 533)
        self.verticalLayout = QVBoxLayout(NeoStimSettingsWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(NeoStimSettingsWidget)
        self.groupBox.setObjectName(u"groupBox")
        self.formLayout = QFormLayout(self.groupBox)
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)

        self.voltage = QDoubleSpinBox(self.groupBox)
        self.voltage.setObjectName(u"voltage")
        self.voltage.setMinimum(2.000000000000000)
        self.voltage.setMaximum(10.000000000000000)
        self.voltage.setSingleStep(0.100000000000000)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.voltage)

        self.label_15 = QLabel(self.groupBox)
        self.label_15.setObjectName(u"label_15")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_15)

        self.duty_cycle_at_max_power = QDoubleSpinBox(self.groupBox)
        self.duty_cycle_at_max_power.setObjectName(u"duty_cycle_at_max_power")
        self.duty_cycle_at_max_power.setDecimals(0)
        self.duty_cycle_at_max_power.setMaximum(90.000000000000000)
        self.duty_cycle_at_max_power.setValue(50.000000000000000)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.duty_cycle_at_max_power)


        self.verticalLayout.addWidget(self.groupBox)

        self.groupBox_3 = QGroupBox(NeoStimSettingsWidget)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.formLayout_3 = QFormLayout(self.groupBox_3)
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.label_2 = QLabel(self.groupBox_3)
        self.label_2.setObjectName(u"label_2")

        self.formLayout_3.setWidget(0, QFormLayout.LabelRole, self.label_2)

        self.carrier_frequency = QDoubleSpinBox(self.groupBox_3)
        self.carrier_frequency.setObjectName(u"carrier_frequency")
        self.carrier_frequency.setDecimals(0)
        self.carrier_frequency.setMinimum(500.000000000000000)
        self.carrier_frequency.setMaximum(2000.000000000000000)
        self.carrier_frequency.setSingleStep(10.000000000000000)
        self.carrier_frequency.setValue(1000.000000000000000)

        self.formLayout_3.setWidget(0, QFormLayout.FieldRole, self.carrier_frequency)

        self.label_3 = QLabel(self.groupBox_3)
        self.label_3.setObjectName(u"label_3")

        self.formLayout_3.setWidget(1, QFormLayout.LabelRole, self.label_3)

        self.pulse_frequency = QDoubleSpinBox(self.groupBox_3)
        self.pulse_frequency.setObjectName(u"pulse_frequency")
        self.pulse_frequency.setMinimum(1.000000000000000)
        self.pulse_frequency.setMaximum(100.000000000000000)
        self.pulse_frequency.setValue(10.000000000000000)

        self.formLayout_3.setWidget(1, QFormLayout.FieldRole, self.pulse_frequency)


        self.verticalLayout.addWidget(self.groupBox_3)

        self.groupBox_2 = QGroupBox(NeoStimSettingsWidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.formLayout_2 = QFormLayout(self.groupBox_2)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.label_8 = QLabel(self.groupBox_2)
        self.label_8.setObjectName(u"label_8")

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.label_8)

        self.use_a = QCheckBox(self.groupBox_2)
        self.use_a.setObjectName(u"use_a")
        self.use_a.setChecked(True)

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.use_a)

        self.label_9 = QLabel(self.groupBox_2)
        self.label_9.setObjectName(u"label_9")

        self.formLayout_2.setWidget(1, QFormLayout.LabelRole, self.label_9)

        self.use_b = QCheckBox(self.groupBox_2)
        self.use_b.setObjectName(u"use_b")
        self.use_b.setChecked(True)

        self.formLayout_2.setWidget(1, QFormLayout.FieldRole, self.use_b)

        self.label_7 = QLabel(self.groupBox_2)
        self.label_7.setObjectName(u"label_7")

        self.formLayout_2.setWidget(2, QFormLayout.LabelRole, self.label_7)

        self.triplet_power = QDoubleSpinBox(self.groupBox_2)
        self.triplet_power.setObjectName(u"triplet_power")
        self.triplet_power.setMinimum(0.000000000000000)
        self.triplet_power.setMaximum(1.000000000000000)
        self.triplet_power.setSingleStep(0.010000000000000)
        self.triplet_power.setValue(0.860000000000000)

        self.formLayout_2.setWidget(2, QFormLayout.FieldRole, self.triplet_power)

        self.line = QFrame(self.groupBox_2)
        self.line.setObjectName(u"line")
        self.line.setMinimumSize(QSize(100, 0))
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.formLayout_2.setWidget(3, QFormLayout.SpanningRole, self.line)

        self.label_10 = QLabel(self.groupBox_2)
        self.label_10.setObjectName(u"label_10")

        self.formLayout_2.setWidget(4, QFormLayout.LabelRole, self.label_10)

        self.use_ab = QCheckBox(self.groupBox_2)
        self.use_ab.setObjectName(u"use_ab")
        self.use_ab.setChecked(False)

        self.formLayout_2.setWidget(4, QFormLayout.FieldRole, self.use_ab)

        self.label_11 = QLabel(self.groupBox_2)
        self.label_11.setObjectName(u"label_11")

        self.formLayout_2.setWidget(5, QFormLayout.LabelRole, self.label_11)

        self.use_ac = QCheckBox(self.groupBox_2)
        self.use_ac.setObjectName(u"use_ac")
        self.use_ac.setChecked(False)

        self.formLayout_2.setWidget(5, QFormLayout.FieldRole, self.use_ac)

        self.label_12 = QLabel(self.groupBox_2)
        self.label_12.setObjectName(u"label_12")

        self.formLayout_2.setWidget(6, QFormLayout.LabelRole, self.label_12)

        self.use_bc = QCheckBox(self.groupBox_2)
        self.use_bc.setObjectName(u"use_bc")
        self.use_bc.setChecked(False)

        self.formLayout_2.setWidget(6, QFormLayout.FieldRole, self.use_bc)

        self.line_2 = QFrame(self.groupBox_2)
        self.line_2.setObjectName(u"line_2")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line_2.sizePolicy().hasHeightForWidth())
        self.line_2.setSizePolicy(sizePolicy)
        self.line_2.setMinimumSize(QSize(100, 0))
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.formLayout_2.setWidget(7, QFormLayout.SpanningRole, self.line_2)

        self.label_13 = QLabel(self.groupBox_2)
        self.label_13.setObjectName(u"label_13")

        self.formLayout_2.setWidget(9, QFormLayout.LabelRole, self.label_13)

        self.emulate_ab_c = QCheckBox(self.groupBox_2)
        self.emulate_ab_c.setObjectName(u"emulate_ab_c")
        self.emulate_ab_c.setChecked(True)

        self.formLayout_2.setWidget(9, QFormLayout.FieldRole, self.emulate_ab_c)

        self.label_14 = QLabel(self.groupBox_2)
        self.label_14.setObjectName(u"label_14")

        self.formLayout_2.setWidget(10, QFormLayout.LabelRole, self.label_14)

        self.emulation_power = QDoubleSpinBox(self.groupBox_2)
        self.emulation_power.setObjectName(u"emulation_power")
        self.emulation_power.setMinimum(0.000000000000000)
        self.emulation_power.setMaximum(1.200000000000000)
        self.emulation_power.setSingleStep(0.010000000000000)
        self.emulation_power.setValue(1.000000000000000)

        self.formLayout_2.setWidget(10, QFormLayout.FieldRole, self.emulation_power)


        self.verticalLayout.addWidget(self.groupBox_2)

        self.groupBox_4 = QGroupBox(NeoStimSettingsWidget)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.formLayout_4 = QFormLayout(self.groupBox_4)
        self.formLayout_4.setObjectName(u"formLayout_4")
        self.label_4 = QLabel(self.groupBox_4)
        self.label_4.setObjectName(u"label_4")

        self.formLayout_4.setWidget(0, QFormLayout.LabelRole, self.label_4)

        self.inversion_time = QDoubleSpinBox(self.groupBox_4)
        self.inversion_time.setObjectName(u"inversion_time")
        self.inversion_time.setDecimals(0)
        self.inversion_time.setMinimum(1.000000000000000)
        self.inversion_time.setMaximum(500.000000000000000)
        self.inversion_time.setValue(100.000000000000000)

        self.formLayout_4.setWidget(0, QFormLayout.FieldRole, self.inversion_time)

        self.label_5 = QLabel(self.groupBox_4)
        self.label_5.setObjectName(u"label_5")

        self.formLayout_4.setWidget(1, QFormLayout.LabelRole, self.label_5)

        self.switch_time = QDoubleSpinBox(self.groupBox_4)
        self.switch_time.setObjectName(u"switch_time")
        self.switch_time.setDecimals(0)
        self.switch_time.setMinimum(100.000000000000000)
        self.switch_time.setMaximum(3000.000000000000000)
        self.switch_time.setValue(1000.000000000000000)

        self.formLayout_4.setWidget(1, QFormLayout.FieldRole, self.switch_time)

        self.label_6 = QLabel(self.groupBox_4)
        self.label_6.setObjectName(u"label_6")

        self.formLayout_4.setWidget(2, QFormLayout.LabelRole, self.label_6)

        self.defeat_randomization = QCheckBox(self.groupBox_4)
        self.defeat_randomization.setObjectName(u"defeat_randomization")

        self.formLayout_4.setWidget(2, QFormLayout.FieldRole, self.defeat_randomization)


        self.verticalLayout.addWidget(self.groupBox_4)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        QWidget.setTabOrder(self.voltage, self.duty_cycle_at_max_power)
        QWidget.setTabOrder(self.duty_cycle_at_max_power, self.carrier_frequency)
        QWidget.setTabOrder(self.carrier_frequency, self.pulse_frequency)
        QWidget.setTabOrder(self.pulse_frequency, self.use_a)
        QWidget.setTabOrder(self.use_a, self.use_b)
        QWidget.setTabOrder(self.use_b, self.use_ab)
        QWidget.setTabOrder(self.use_ab, self.use_ac)
        QWidget.setTabOrder(self.use_ac, self.use_bc)
        QWidget.setTabOrder(self.use_bc, self.emulate_ab_c)
        QWidget.setTabOrder(self.emulate_ab_c, self.inversion_time)
        QWidget.setTabOrder(self.inversion_time, self.switch_time)
        QWidget.setTabOrder(self.switch_time, self.defeat_randomization)

        self.retranslateUi(NeoStimSettingsWidget)

        QMetaObject.connectSlotsByName(NeoStimSettingsWidget)
    # setupUi

    def retranslateUi(self, NeoStimSettingsWidget):
        NeoStimSettingsWidget.setWindowTitle(QCoreApplication.translate("NeoStimSettingsWidget", u"Form", None))
        self.groupBox.setTitle(QCoreApplication.translate("NeoStimSettingsWidget", u"Power", None))
        self.label.setText(QCoreApplication.translate("NeoStimSettingsWidget", u"voltage [V]", None))
        self.label_15.setText(QCoreApplication.translate("NeoStimSettingsWidget", u"duty cycle at max volume [%]", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("NeoStimSettingsWidget", u"Feel", None))
        self.label_2.setText(QCoreApplication.translate("NeoStimSettingsWidget", u"\"carrier frequency\" [Hz]", None))
        self.label_3.setText(QCoreApplication.translate("NeoStimSettingsWidget", u"pulse frequency [Hz]", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("NeoStimSettingsWidget", u"debug", None))
        self.label_8.setText(QCoreApplication.translate("NeoStimSettingsWidget", u"use A-BC", None))
        self.use_a.setText("")
        self.label_9.setText(QCoreApplication.translate("NeoStimSettingsWidget", u"use B-AC", None))
        self.use_b.setText("")
#if QT_CONFIG(tooltip)
        self.label_7.setToolTip(QCoreApplication.translate("NeoStimSettingsWidget", u"<html><head/><body><p>Power of 3-electrode pulses vs 2-electrode pulses.</p><p>Theoretical value = sqrt(3)/2 = .86</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_7.setText(QCoreApplication.translate("NeoStimSettingsWidget", u"triplet power (?)", None))
        self.label_10.setText(QCoreApplication.translate("NeoStimSettingsWidget", u"use A-B", None))
        self.use_ab.setText("")
        self.label_11.setText(QCoreApplication.translate("NeoStimSettingsWidget", u"use A-C", None))
        self.use_ac.setText("")
        self.label_12.setText(QCoreApplication.translate("NeoStimSettingsWidget", u"use B-C", None))
        self.use_bc.setText("")
        self.label_13.setText(QCoreApplication.translate("NeoStimSettingsWidget", u"emulate C-AB using C-A and C-B", None))
        self.emulate_ab_c.setText("")
#if QT_CONFIG(tooltip)
        self.label_14.setToolTip(QCoreApplication.translate("NeoStimSettingsWidget", u"<html><head/><body><p>suggested value 0.9 to 1.0</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_14.setText(QCoreApplication.translate("NeoStimSettingsWidget", u"emulation power (?)", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("NeoStimSettingsWidget", u"DANGER ZONE", None))
#if QT_CONFIG(tooltip)
        self.label_4.setToolTip(QCoreApplication.translate("NeoStimSettingsWidget", u"<html><head/><body><p>Time betweel positive and negative pulse.</p><p>80\u00b5s-100\u00b5s for best theoretical efficiency.</p><p>Values below 30\u00b5s are unstable.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_4.setText(QCoreApplication.translate("NeoStimSettingsWidget", u"inversion time [\u00b5s] (?)", None))
#if QT_CONFIG(tooltip)
        self.label_5.setToolTip(QCoreApplication.translate("NeoStimSettingsWidget", u"<html><head/><body><p>Delay between two pulses with different triac configurations.</p><p>Values below 1000\u00b5s can result in misfiring, especially when voltage is high.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_5.setText(QCoreApplication.translate("NeoStimSettingsWidget", u"triac time [\u00b5s] (?)", None))
#if QT_CONFIG(tooltip)
        self.label_6.setToolTip(QCoreApplication.translate("NeoStimSettingsWidget", u"<html><head/><body><p>Improve viewing experience on the scope.</p><p>Improve smoothness.</p><p>Not sure if safe.</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label_6.setText(QCoreApplication.translate("NeoStimSettingsWidget", u"Defeat randomization (?)", None))
        self.defeat_randomization.setText("")
    # retranslateUi

