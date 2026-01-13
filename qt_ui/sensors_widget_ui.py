# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'sensorswidget.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QHBoxLayout, QHeaderView,
    QLabel, QSizePolicy, QStackedWidget, QTextBrowser,
    QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget)

class Ui_SensorsWidget(object):
    def setupUi(self, SensorsWidget):
        if not SensorsWidget.objectName():
            SensorsWidget.setObjectName(u"SensorsWidget")
        SensorsWidget.resize(762, 583)
        self.horizontalLayout = QHBoxLayout(SensorsWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.widget = QWidget(SensorsWidget)
        self.widget.setObjectName(u"widget")
        self.verticalLayout = QVBoxLayout(self.widget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(-1, 9, -1, -1)
        self.treeWidget = QTreeWidget(self.widget)
        self.treeWidget.headerItem().setText(0, "")
        __qtreewidgetitem = QTreeWidgetItem(self.treeWidget)
        QTreeWidgetItem(__qtreewidgetitem)
        QTreeWidgetItem(__qtreewidgetitem)
        __qtreewidgetitem1 = QTreeWidgetItem(self.treeWidget)
        QTreeWidgetItem(__qtreewidgetitem1)
        QTreeWidgetItem(__qtreewidgetitem1)
        QTreeWidgetItem(__qtreewidgetitem1)
        self.treeWidget.setObjectName(u"treeWidget")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.treeWidget.sizePolicy().hasHeightForWidth())
        self.treeWidget.setSizePolicy(sizePolicy)
        self.treeWidget.setMaximumSize(QSize(200, 16777215))

        self.verticalLayout.addWidget(self.treeWidget)

        self.checkBox = QCheckBox(self.widget)
        self.checkBox.setObjectName(u"checkBox")

        self.verticalLayout.addWidget(self.checkBox)

        self.label = QLabel(self.widget)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.textBrowser = QTextBrowser(self.widget)
        self.textBrowser.setObjectName(u"textBrowser")
        sizePolicy.setHeightForWidth(self.textBrowser.sizePolicy().hasHeightForWidth())
        self.textBrowser.setSizePolicy(sizePolicy)
        self.textBrowser.setMinimumSize(QSize(200, 0))
        self.textBrowser.setMaximumSize(QSize(200, 200))

        self.verticalLayout.addWidget(self.textBrowser)


        self.horizontalLayout.addWidget(self.widget)

        self.stackedWidget = QStackedWidget(SensorsWidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.page = QWidget()
        self.page.setObjectName(u"page")
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QWidget()
        self.page_2.setObjectName(u"page_2")
        self.stackedWidget.addWidget(self.page_2)

        self.horizontalLayout.addWidget(self.stackedWidget)


        self.retranslateUi(SensorsWidget)

        QMetaObject.connectSlotsByName(SensorsWidget)
    # setupUi

    def retranslateUi(self, SensorsWidget):
        SensorsWidget.setWindowTitle(QCoreApplication.translate("SensorsWidget", u"Form", None))
        ___qtreewidgetitem = self.treeWidget.headerItem()
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("SensorsWidget", u"Enabled", None));

        __sortingEnabled = self.treeWidget.isSortingEnabled()
        self.treeWidget.setSortingEnabled(False)
        ___qtreewidgetitem1 = self.treeWidget.topLevelItem(0)
        ___qtreewidgetitem1.setText(0, QCoreApplication.translate("SensorsWidget", u"IMU (6-axis)", None));
        ___qtreewidgetitem2 = ___qtreewidgetitem1.child(0)
        ___qtreewidgetitem2.setText(0, QCoreApplication.translate("SensorsWidget", u"blah", None));
        ___qtreewidgetitem3 = ___qtreewidgetitem1.child(1)
        ___qtreewidgetitem3.setText(0, QCoreApplication.translate("SensorsWidget", u"blah2", None));
        ___qtreewidgetitem4 = self.treeWidget.topLevelItem(1)
        ___qtreewidgetitem4.setText(0, QCoreApplication.translate("SensorsWidget", u"AS5311", None));
        ___qtreewidgetitem5 = ___qtreewidgetitem4.child(0)
        ___qtreewidgetitem5.setText(0, QCoreApplication.translate("SensorsWidget", u"absolute", None));
        ___qtreewidgetitem6 = ___qtreewidgetitem4.child(1)
        ___qtreewidgetitem6.setText(0, QCoreApplication.translate("SensorsWidget", u"low-pass", None));
        ___qtreewidgetitem7 = ___qtreewidgetitem4.child(2)
        ___qtreewidgetitem7.setText(0, QCoreApplication.translate("SensorsWidget", u"velocity", None));
        self.treeWidget.setSortingEnabled(__sortingEnabled)

        self.checkBox.setText(QCoreApplication.translate("SensorsWidget", u"Enabled", None))
        self.label.setText(QCoreApplication.translate("SensorsWidget", u"Description:", None))
    # retranslateUi

