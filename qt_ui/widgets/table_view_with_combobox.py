from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, QTimer, QItemSelectionModel, QSize, QRect
from PyQt5.QtGui import QCursor, QMouseEvent
from PyQt5.QtWidgets import QTableView, QStyledItemDelegate, QWidget, QComboBox, QStyleOptionComboBox, QApplication, \
    QStyle, QStyleOptionButton, QTreeView
import functools

# open combobox immediately on first mouse press
# from https://github.com/pierrebai/QtAdditions/blob/ae77ff845265ea4ef279e678c64d036330feca8a/src/QTableWidgetWithComboBox.cpp


class ComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, text_and_data, parent=None):
        super(ComboBoxDelegate, self).__init__(parent)
        self.text_and_data = text_and_data

    def createEditor(self, parent: QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> QWidget:
        cb = QComboBox(parent)
        for text, data in self.text_and_data:
            cb.addItem(text, data)

        def set_data(i):
            self.commitData.emit(cb)
            self.closeEditor.emit(cb)
        cb.currentIndexChanged.connect(set_data)

        return cb

    def setEditorData(self, editor: QWidget, index: QtCore.QModelIndex) -> None:
        combobox: QComboBox = editor
        combobox.setCurrentIndex(combobox.findData(index.data(Qt.EditRole)))
        combobox.showPopup()

    def setModelData(self, editor: QWidget, model: QtCore.QAbstractItemModel, index: QtCore.QModelIndex) -> None:
        combobox: QComboBox = editor
        model.setData(index, combobox.currentData(), Qt.EditRole)

    def paint(self, painter: 'QtGui.QPainter', option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> None:
        if not (index.flags() & Qt.ItemIsEditable):
            return super(ComboBoxDelegate, self).paint(painter, option, index)

        box = QStyleOptionComboBox()
        box.state = option.state
        box.rect = option.rect
        box.currentText = index.data(Qt.DisplayRole)

        QApplication.style().drawComplexControl(QStyle.CC_ComboBox, box, painter)
        QApplication.style().drawControl(QStyle.CE_ComboBoxLabel, box, painter)

    def sizeHint(self, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> QtCore.QSize:
        box = QStyleOptionComboBox()
        box.state = option.state
        box.rect = option.rect

        size = QSize(0, 0)
        for text, data in self.text_and_data:
            box.currentText = text
            rect = QApplication.style().itemTextRect(option.fontMetrics, option.rect, Qt.AlignCenter, True, text)
            size = size.expandedTo(QApplication.style().sizeFromContents(QStyle.CT_ComboBox, box, rect.size(), option.widget))

        return size


class TableViewWithComboBox(QTableView):
    def __init__(self, parent):
        super(TableViewWithComboBox, self).__init__(parent)

    # immediately open the combobox on first mouse press
    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        if e.button() == Qt.LeftButton:
            index = self.indexAt(e.pos())

            delegate = self.itemDelegateForColumn(index.column())
            if isinstance(delegate, ComboBoxDelegate):
                selection = self.selectionModel()
                if selection:
                    other_index = self.model().index(index.row(), index.column())
                    selection.setCurrentIndex(other_index, QItemSelectionModel.ClearAndSelect)

                timer = QTimer()
                timer.timeout.connect(functools.partial(self.edit, index))
                timer.setSingleShot(True)
                timer.start(1)
                self.timer = timer  # prevent timer release (scope)
                e.setAccepted(True)
                return

        super(TableViewWithComboBox, self).mousePressEvent(e)


class TreeViewWithComboBox(QTreeView):
    def __init__(self, parent):
        super(TreeViewWithComboBox, self).__init__(parent)

    # immediately open the combobox on first mouse press
    def mousePressEvent(self, e: QtGui.QMouseEvent) -> None:
        if e.button() == Qt.LeftButton:
            index = self.indexAt(e.pos())

            delegate = self.itemDelegateForColumn(index.column())
            if isinstance(delegate, ComboBoxDelegate):
                selection = self.selectionModel()
                if selection:
                    other_index = self.model().index(index.row(), index.column())
                    selection.setCurrentIndex(other_index, QItemSelectionModel.ClearAndSelect)

                timer = QTimer()
                timer.timeout.connect(functools.partial(self.edit, index))
                timer.setSingleShot(True)
                timer.start(1)
                self.timer = timer  # prevent timer release (scope)
                e.setAccepted(True)
                return

        super(TreeViewWithComboBox, self).mousePressEvent(e)


# TODO: expand to support multiple buttons
class ButtonDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(ButtonDelegate, self).__init__(parent)

        self.mouse_hover = []
        self.button_size = 20  # minimum

    def button_rect(self, button_index, parent_rect: QRect):
        button_width = parent_rect.height()
        rect = parent_rect.translated(button_index * button_width, 0)
        rect.setWidth(button_width)
        return rect

    def createEditor(self, parent: QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> QWidget:
        return None

    def editorEvent(self, event: QtCore.QEvent, model: QtCore.QAbstractItemModel, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> bool:
        if isinstance(event, QMouseEvent):
            event: QMouseEvent

            # calculate if mouse hovers over button
            mouse_hover = [
                self.button_rect(0, option.rect).contains(event.pos())
            ]
            if mouse_hover != self.mouse_hover:
                self.mouse_hover = mouse_hover
                model.dataChanged.emit(index, index)

            if event.button() == Qt.LeftButton:
                if event.type() == QtCore.QEvent.Type.MouseButtonRelease:
                    if mouse_hover[0]:
                        model.removeRow(index.row(), index.parent())

        return False

    def paint(self, painter: 'QtGui.QPainter', option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> None:
        is_removable = index.data(Qt.DisplayRole)
        if is_removable:
            button = QStyleOptionButton()
            button.rect = self.button_rect(0, option.rect)
            button.iconSize = button.rect.size()
            button.icon = QtGui.QIcon(":/restim/trash.svg")
            button.state = option.state
            cursor = QCursor.pos()
            if button.rect.contains(option.styleObject.viewport().mapFromGlobal(cursor)):
                button.features = button.DefaultButton
            else:
                button.features = button.Flat

            QApplication.style().drawControl(QStyle.CE_PushButton, button, painter)

    def sizeHint(self, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> QtCore.QSize:
        return QSize(self.button_size, self.button_size)
