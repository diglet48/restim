import os
import typing
import logging

from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt

import qt_ui.device_wizard
import qt_ui.device_wizard.axes
from qt_ui.device_wizard.axes import AxisEnum
from qt_ui.models.tree_item import TreeItem
from qt_ui.models.funscript_kit import FunscriptKitModel
from funscript.funscript import Funscript

logger = logging.getLogger('restim.script_mapping')


class HeaderTreeItem(TreeItem):
    def __init__(self, parent: TreeItem=None):
        super(HeaderTreeItem, self).__init__(parent)

    def data(self, column):
        items = ['resource', 'target', 'actions']
        return items[column]


class ResourceCategory(TreeItem):
    def __init__(self, name: str, parent: TreeItem=None):
        super(ResourceCategory, self).__init__(parent)

        self.name = name

    def data(self, column):
        if column == 0:
            return self.name
        return None

class FunscriptTreeItem(TreeItem):
    def __init__(self, full_path: str, parent: TreeItem=None):
        super(FunscriptTreeItem, self).__init__(parent)

        self.full_path = full_path
        self.file_name = os.path.basename(full_path)
        self.script_name = ''
        try:
            _, self.script_name, _ = self.file_name.split('.')
        except ValueError:
            pass
        self.axis = qt_ui.device_wizard.axes.AxisEnum.NONE
        self.is_removable = False
        self.used = False

        # load funscript immediately. This makes the UI feel sluggish on connecting/disconnecting
        # but has the advantage of not requiring any file IO when audio starts.
        self.script = Funscript.from_file(self.full_path)

    def data(self, column):
        if column == 0:
            return self.file_name
        if column == 1:
            return self.axis.display_name()
        if column == 2:
            return self.is_removable

    def edit_data(self, column):
        if column == 0:
            return self.file_name
        if column == 1:
            return self.axis
        if column == 2:
            return self.is_removable


class TCodeTreeItem(TreeItem):
    def __init__(self, axis: str, parent: TreeItem = None):
        super(TCodeTreeItem, self).__init__(parent)

        self.axis = axis

    def data(self, column):
        if column == 0:
            return self.axis
        return 'todo'


class ScriptMappingModel(QAbstractItemModel):
    def __init__(self):
        super(ScriptMappingModel, self).__init__()

        self._root = HeaderTreeItem()
        self._funscripts_manual = ResourceCategory('Funscripts (manual)', self._root)
        self._root.appendChild(self._funscripts_manual)
        self._funscripts_auto = ResourceCategory('Funscripts (auto-detected)', self._root)
        self._root.appendChild(self._funscripts_auto)

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if not index.isValid():
            return None

        if role == Qt.EditRole:
            item = index.internalPointer()
            return item.edit_data(index.column())
        elif role == Qt.DisplayRole:
            item = index.internalPointer()
            return item.data(index.column())
        else:
            return None

    def setData(self, index: QModelIndex, value: typing.Any, role: int = ...) -> bool:
        # print('setData', index.row(), index.column(), value)
        if role == Qt.EditRole:
            if isinstance(index.internalPointer(), FunscriptTreeItem):
                if index.column() == 1:
                    if index.internalPointer().axis != value:
                        # only emit signals if data actually changed
                        index.internalPointer().axis = value
                        self.refresh_active_files()
                        self.dataChanged.emit(index, index, [role])
                        return True
        return False

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags

        if index.column() == 0:
            if isinstance(index.internalPointer(), FunscriptTreeItem):
                if index.internalPointer().used:
                    return Qt.ItemIsEnabled
                else:
                    return Qt.NoItemFlags

            return Qt.ItemIsEnabled
        else:
            if isinstance(index.internalPointer(), ResourceCategory):
                return Qt.ItemIsEnabled
            return Qt.ItemIsEnabled |  Qt.ItemIsEditable
        # return super(TreeModel, self).flags(index)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> typing.Any:
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._root.data(section)
        return None

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self._root
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        return QModelIndex()

    def parent(self,  index: QModelIndex) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parentItem()

        if parentItem == self._root:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self._root
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return parent.internalPointer().columnCount()
        return self._root.columnCount()

    def removeRow(self, row: int, parent: QModelIndex = ...) -> bool:
        # print(parent.internalPointer(), row)
        self.beginRemoveRows(parent, row, row)
        parent.internalPointer().removeChild(row)
        self.endRemoveRows()
        self.dataChanged.emit(parent, parent, [Qt.EditRole])
        self.refresh_active_files()
        return True

    def add_funscript_resource_auto(self, item: FunscriptTreeItem):
        item.parent = self._funscripts_auto
        self._funscripts_auto.appendChild(item)

    def add_funscript_resource_manual(self, item: FunscriptTreeItem):
        item.parent = self._funscripts_manual
        item.is_removable = True
        self._funscripts_manual.appendChild(item)
        self.refresh_active_files()

    def funscript_conifg(self) -> list[FunscriptTreeItem]:
        return self._funscripts_manual.children + self._funscripts_auto.children

    def get_config_for_axis(self, axis: AxisEnum) -> FunscriptTreeItem | None:
        for funscript in self._funscripts_manual.children + self._funscripts_auto.children:
            if funscript.axis == axis:
                return funscript
        return None

    def refresh_active_files(self):
        used = {AxisEnum.NONE}
        for item in self._funscripts_manual.children + self._funscripts_auto.children:
            use = item.axis not in used
            used.add(item.axis)

            if use != item.used:
                item.used = use
                index = self.createIndex(item.row(), 0, item.parent)
                self.dataChanged.emit(index, index, [Qt.DisplayRole])

    def case_insensitive_compare(self, a, b):
        return a.lower() == b.lower()

    def split_funscript_path(self, path):
        a, b = os.path.split(path)
        parts = b.split('.')
        extension = parts[-1]
        if len(parts) == 1:
            return parts[0], '', ''
        if len(parts) == 2:
            return parts[0], '', extension
        return '.'.join(parts[:-2]), parts[-2], extension

    def detect_funscripts_from_path(self, media_path: str) -> bool:
        """
        :param media_path: /path/to/video.mp4
        :return:
        """
        logger.info(f'detecting funscripts from: `{media_path}`')
        dirty = self._funscripts_auto.childCount() > 0

        self._funscripts_auto.children.clear()

        media_dir = os.path.dirname(media_path)
        prefix, suffix, extension = self.split_funscript_path(media_path)

        prefix = prefix.lower() + '.'
        suffix = '.funscript'.lower()

        try:
            for file in os.scandir(media_dir):
                if file.name.lower().startswith(prefix) and file.name.lower().endswith(suffix):
                    self.add_funscript_resource_auto(FunscriptTreeItem(file.path))
                    dirty = True
        except OSError:
            # probably invalid network path
            pass
        return dirty

    def clear_auto_detected_funscripts(self):
        if self._funscripts_auto.childCount():
            self.beginRemoveRows(self.createIndex(0, 0, self._funscripts_auto), 0, self._funscripts_auto.childCount())
            self._funscripts_auto.children.clear()
            self.endRemoveRows()
            return True
        return False

    def auto_link_funscripts(self, kit: FunscriptKitModel) -> None:
        for item in self.funscript_conifg():
            self.auto_link_funscript(kit, item)
        self.refresh_active_files()

    def auto_link_funscript(self, kit: FunscriptKitModel, item: FunscriptTreeItem):
        prefix, suffix, extension = self.split_funscript_path(item.file_name)
        if suffix:
            for kit_item in kit.funscript_conifg():
                if kit_item.auto_loading:
                    if suffix in kit_item.funscript_names:
                        item.axis = kit_item.axis
                        logger.info(f'auto-linking `{item.file_name}` to {kit_item.axis.display_name()}.')
                        return
        logger.info(f'auto-linking `{item.file_name}` failed')
