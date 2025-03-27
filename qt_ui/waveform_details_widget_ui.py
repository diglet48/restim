# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'waveformdetailswidget.ui'
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QGroupBox, QLabel,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_WaveformDetails(object):
    def setupUi(self, WaveformDetails):
        if not WaveformDetails.objectName():
            WaveformDetails.setObjectName(u"WaveformDetails")
        WaveformDetails.resize(553, 528)
        self.verticalLayout = QVBoxLayout(WaveformDetails)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox_2 = QGroupBox(WaveformDetails)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.formLayout = QFormLayout(self.groupBox_2)
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(self.groupBox_2)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)

        self.left_amplitude_label = QLabel(self.groupBox_2)
        self.left_amplitude_label.setObjectName(u"left_amplitude_label")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.left_amplitude_label)

        self.label_3 = QLabel(self.groupBox_2)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_3)

        self.right_amplitude_label = QLabel(self.groupBox_2)
        self.right_amplitude_label.setObjectName(u"right_amplitude_label")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.right_amplitude_label)

        self.label_7 = QLabel(self.groupBox_2)
        self.label_7.setObjectName(u"label_7")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_7)

        self.center_amplitude_label = QLabel(self.groupBox_2)
        self.center_amplitude_label.setObjectName(u"center_amplitude_label")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.center_amplitude_label)

        self.label_5 = QLabel(self.groupBox_2)
        self.label_5.setObjectName(u"label_5")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label_5)

        self.phase_label = QLabel(self.groupBox_2)
        self.phase_label.setObjectName(u"phase_label")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.phase_label)


        self.verticalLayout.addWidget(self.groupBox_2)

        self.groupBox_3 = QGroupBox(WaveformDetails)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.formLayout_2 = QFormLayout(self.groupBox_3)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.label_9 = QLabel(self.groupBox_3)
        self.label_9.setObjectName(u"label_9")

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.label_9)

        self.alpha_label = QLabel(self.groupBox_3)
        self.alpha_label.setObjectName(u"alpha_label")

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.alpha_label)

        self.label_11 = QLabel(self.groupBox_3)
        self.label_11.setObjectName(u"label_11")

        self.formLayout_2.setWidget(1, QFormLayout.LabelRole, self.label_11)

        self.beta_label = QLabel(self.groupBox_3)
        self.beta_label.setObjectName(u"beta_label")

        self.formLayout_2.setWidget(1, QFormLayout.FieldRole, self.beta_label)


        self.verticalLayout.addWidget(self.groupBox_3)

        self.groupBox_5 = QGroupBox(WaveformDetails)
        self.groupBox_5.setObjectName(u"groupBox_5")
        self.formLayout_5 = QFormLayout(self.groupBox_5)
        self.formLayout_5.setObjectName(u"formLayout_5")
        self.label_8 = QLabel(self.groupBox_5)
        self.label_8.setObjectName(u"label_8")

        self.formLayout_5.setWidget(0, QFormLayout.LabelRole, self.label_8)

        self.r_label = QLabel(self.groupBox_5)
        self.r_label.setObjectName(u"r_label")

        self.formLayout_5.setWidget(0, QFormLayout.FieldRole, self.r_label)

        self.label_13 = QLabel(self.groupBox_5)
        self.label_13.setObjectName(u"label_13")

        self.formLayout_5.setWidget(1, QFormLayout.LabelRole, self.label_13)

        self.theta_label = QLabel(self.groupBox_5)
        self.theta_label.setObjectName(u"theta_label")

        self.formLayout_5.setWidget(1, QFormLayout.FieldRole, self.theta_label)


        self.verticalLayout.addWidget(self.groupBox_5)

        self.groupBox = QGroupBox(WaveformDetails)
        self.groupBox.setObjectName(u"groupBox")
        self.formLayout_3 = QFormLayout(self.groupBox)
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.formLayout_3.setWidget(0, QFormLayout.LabelRole, self.label_2)

        self.neutral_label = QLabel(self.groupBox)
        self.neutral_label.setObjectName(u"neutral_label")

        self.formLayout_3.setWidget(0, QFormLayout.FieldRole, self.neutral_label)

        self.label_6 = QLabel(self.groupBox)
        self.label_6.setObjectName(u"label_6")

        self.formLayout_3.setWidget(2, QFormLayout.LabelRole, self.label_6)

        self.right_label = QLabel(self.groupBox)
        self.right_label.setObjectName(u"right_label")

        self.formLayout_3.setWidget(2, QFormLayout.FieldRole, self.right_label)

        self.label_10 = QLabel(self.groupBox)
        self.label_10.setObjectName(u"label_10")

        self.formLayout_3.setWidget(1, QFormLayout.LabelRole, self.label_10)

        self.left_label = QLabel(self.groupBox)
        self.left_label.setObjectName(u"left_label")

        self.formLayout_3.setWidget(1, QFormLayout.FieldRole, self.left_label)


        self.verticalLayout.addWidget(self.groupBox)

        self.label_4 = QLabel(WaveformDetails)
        self.label_4.setObjectName(u"label_4")

        self.verticalLayout.addWidget(self.label_4)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.retranslateUi(WaveformDetails)

        QMetaObject.connectSlotsByName(WaveformDetails)
    # setupUi

    def retranslateUi(self, WaveformDetails):
        WaveformDetails.setWindowTitle(QCoreApplication.translate("WaveformDetails", u"Form", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("WaveformDetails", u"Amplitude, Phase", None))
        self.label.setText(QCoreApplication.translate("WaveformDetails", u"Left amplitude", None))
        self.left_amplitude_label.setText(QCoreApplication.translate("WaveformDetails", u"TextLabel", None))
        self.label_3.setText(QCoreApplication.translate("WaveformDetails", u"Right amplitude", None))
        self.right_amplitude_label.setText(QCoreApplication.translate("WaveformDetails", u"TextLabel", None))
        self.label_7.setText(QCoreApplication.translate("WaveformDetails", u"Center amplitude", None))
        self.center_amplitude_label.setText(QCoreApplication.translate("WaveformDetails", u"TextLabel", None))
        self.label_5.setText(QCoreApplication.translate("WaveformDetails", u"Phase", None))
        self.phase_label.setText(QCoreApplication.translate("WaveformDetails", u"TextLabel", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("WaveformDetails", u"Alpha, Beta", None))
        self.label_9.setText(QCoreApplication.translate("WaveformDetails", u"Alpha", None))
        self.alpha_label.setText(QCoreApplication.translate("WaveformDetails", u"TextLabel", None))
        self.label_11.setText(QCoreApplication.translate("WaveformDetails", u"Beta", None))
        self.beta_label.setText(QCoreApplication.translate("WaveformDetails", u"TextLabel", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("WaveformDetails", u"R, Theta", None))
        self.label_8.setText(QCoreApplication.translate("WaveformDetails", u"R", None))
        self.r_label.setText(QCoreApplication.translate("WaveformDetails", u"TextLabel", None))
        self.label_13.setText(QCoreApplication.translate("WaveformDetails", u"Theta", None))
        self.theta_label.setText(QCoreApplication.translate("WaveformDetails", u"TextLabel", None))
        self.groupBox.setTitle(QCoreApplication.translate("WaveformDetails", u"Amplitude at electrodes", None))
        self.label_2.setText(QCoreApplication.translate("WaveformDetails", u"Neutral", None))
        self.neutral_label.setText(QCoreApplication.translate("WaveformDetails", u"TextLabel", None))
        self.label_6.setText(QCoreApplication.translate("WaveformDetails", u"R+", None))
        self.right_label.setText(QCoreApplication.translate("WaveformDetails", u"TextLabel", None))
        self.label_10.setText(QCoreApplication.translate("WaveformDetails", u"L+", None))
        self.left_label.setText(QCoreApplication.translate("WaveformDetails", u"TextLabel", None))
        self.label_4.setText(QCoreApplication.translate("WaveformDetails", u"Does not take calibration into account.", None))
    # retranslateUi

