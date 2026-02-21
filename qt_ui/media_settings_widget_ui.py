# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mediasettingswidget.ui'
##
## Created by: Qt User Interface Compiler version 6.9.3
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDoubleSpinBox,
    QFormLayout, QFrame, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

from qt_ui.widgets.table_view_with_combobox import TreeViewWithComboBox
import restim_rc

class Ui_MediaSettingsWidget(object):
    def setupUi(self, MediaSettingsWidget):
        if not MediaSettingsWidget.objectName():
            MediaSettingsWidget.setObjectName(u"MediaSettingsWidget")
        MediaSettingsWidget.resize(664, 477)
        self.verticalLayout = QVBoxLayout(MediaSettingsWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.frame = QFrame(MediaSettingsWidget)
        self.frame.setObjectName(u"frame")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMinimumSize(QSize(150, 0))
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.formLayout = QFormLayout(self.frame)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.widget = QWidget(self.frame)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.widget)
        self.label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.label)

        self.comboBox = QComboBox(self.widget)
        self.comboBox.setObjectName(u"comboBox")

        self.horizontalLayout.addWidget(self.comboBox)

        self.connection_status = QLabel(self.widget)
        self.connection_status.setObjectName(u"connection_status")

        self.horizontalLayout.addWidget(self.connection_status)


        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.widget)

        self.widget_2 = QWidget(self.frame)
        self.widget_2.setObjectName(u"widget_2")
        self.formLayout_2 = QFormLayout(self.widget_2)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.formLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label_2 = QLabel(self.widget_2)
        self.label_2.setObjectName(u"label_2")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.lineEdit = QLineEdit(self.widget_2)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setReadOnly(True)

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lineEdit)

        self.label_3 = QLabel(self.widget_2)
        self.label_3.setObjectName(u"label_3")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_3)

        self.media_offset_spinbox = QDoubleSpinBox(self.widget_2)
        self.media_offset_spinbox.setObjectName(u"media_offset_spinbox")
        self.media_offset_spinbox.setMinimum(-999999.000000000000000)
        self.media_offset_spinbox.setMaximum(999999.000000000000000)
        self.media_offset_spinbox.setSingleStep(0.100000000000000)

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.media_offset_spinbox)


        self.formLayout.setWidget(1, QFormLayout.ItemRole.SpanningRole, self.widget_2)


        self.verticalLayout.addWidget(self.frame)

        self.stop_audio_automatically_checkbox = QCheckBox(MediaSettingsWidget)
        self.stop_audio_automatically_checkbox.setObjectName(u"stop_audio_automatically_checkbox")

        self.verticalLayout.addWidget(self.stop_audio_automatically_checkbox)

        self.treeView = TreeViewWithComboBox(MediaSettingsWidget)
        self.treeView.setObjectName(u"treeView")

        self.verticalLayout.addWidget(self.treeView)

        self.widget_3 = QWidget(MediaSettingsWidget)
        self.widget_3.setObjectName(u"widget_3")
        self.horizontalLayout_2 = QHBoxLayout(self.widget_3)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.add_funscript_button = QPushButton(self.widget_3)
        self.add_funscript_button.setObjectName(u"add_funscript_button")

        self.horizontalLayout_2.addWidget(self.add_funscript_button)

        self.bake_audio_button = QPushButton(self.widget_3)
        self.bake_audio_button.setObjectName(u"bake_audio_button")

        self.horizontalLayout_2.addWidget(self.bake_audio_button)

        self.additional_search_paths_button = QPushButton(self.widget_3)
        self.additional_search_paths_button.setObjectName(u"additional_search_paths_button")

        self.horizontalLayout_2.addWidget(self.additional_search_paths_button)

        self.reload_scripts_button = QPushButton(self.widget_3)
        self.reload_scripts_button.setObjectName(u"reload_scripts_button")

        self.horizontalLayout_2.addWidget(self.reload_scripts_button)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)


        self.verticalLayout.addWidget(self.widget_3)


        self.retranslateUi(MediaSettingsWidget)

        QMetaObject.connectSlotsByName(MediaSettingsWidget)
    # setupUi

    def retranslateUi(self, MediaSettingsWidget):
        MediaSettingsWidget.setWindowTitle(QCoreApplication.translate("MediaSettingsWidget", u"Form", None))
        self.label.setText(QCoreApplication.translate("MediaSettingsWidget", u"Media player", None))
        self.connection_status.setText(QCoreApplication.translate("MediaSettingsWidget", u"TextLabel", None))
        self.label_2.setText(QCoreApplication.translate("MediaSettingsWidget", u"File:", None))
#if QT_CONFIG(tooltip)
        self.label_3.setToolTip(QCoreApplication.translate("MediaSettingsWidget", u"Reduce offset to play signal earlier\n"
"Increase offset to delay signal", None))
#endif // QT_CONFIG(tooltip)
        self.label_3.setText(QCoreApplication.translate("MediaSettingsWidget", u"offset [s] (?)", None))
        self.stop_audio_automatically_checkbox.setText(QCoreApplication.translate("MediaSettingsWidget", u"Stop audio when file changes", None))
        self.add_funscript_button.setText(QCoreApplication.translate("MediaSettingsWidget", u"Add funscript", None))
        self.bake_audio_button.setText(QCoreApplication.translate("MediaSettingsWidget", u"Bake audio", None))
        self.additional_search_paths_button.setText(QCoreApplication.translate("MediaSettingsWidget", u"Search paths", None))
        self.reload_scripts_button.setText(QCoreApplication.translate("MediaSettingsWidget", u"Reload scripts", None))
    # retranslateUi

