import typing
from dataclasses import dataclass
from PyQt5.QtCore import QModelIndex, Qt, QAbstractTableModel, QSettings

from qt_ui.device_wizard.axes import AxisEnum, all_axis


defaults = {
    AxisEnum.POSITION_ALPHA: ('alpha', -1, 1, True),
    AxisEnum.POSITION_BETA: ('beta', -1, 1, True),
    AxisEnum.VOLUME_API: ('volume', 0, 1, True),
    AxisEnum.CARRIER_FREQUENCY: ('frequency', 500, 1000, True),
}

@dataclass
class FunscriptKitItem:
    axis: AxisEnum
    funscript_names: [str]
    limit_min: float
    limit_max: float
    auto_loading: bool


def split_functipt_names(str):
    return [x.strip() for x in str.split(',') if len(x.strip()) > 0]


class FunscriptKitModel(QAbstractTableModel):
    def __init__(self):
        super(FunscriptKitModel, self).__init__()
        self.children: [FunscriptKitItem] = []

    @staticmethod
    def load_from_settings():
        kit = FunscriptKitModel()
        for axis in all_axis:
            kit.children.append(FunscriptKitItem(axis, '', None, None, False))

        settings = QSettings()
        settings.beginGroup('funscript_configuration')
        for item in kit.children:
            default_funscript_name, default_min, default_max, default_auto_load = defaults[item.axis]

            settings.beginGroup(item.axis.settings_key())
            item.funscript_names = split_functipt_names(settings.value('funscript_names', default_funscript_name, str))
            item.limit_min = settings.value('limit_min', default_min, float)
            item.limit_max = settings.value('limit_max', default_max, float)
            item.auto_loading = settings.value('auto_loading', default_auto_load, bool)
            settings.endGroup()

        settings.endGroup()
        return kit

    def save_to_settings(self):
        settings = QSettings()
        settings.beginGroup('funscript_configuration')
        for item in self.children:
            settings.beginGroup(item.axis.settings_key())
            settings.setValue('funscript_names', ', '.join(item.funscript_names))
            settings.setValue('limit_min', item.limit_min)
            settings.setValue('limit_max', item.limit_max)
            settings.setValue('auto_loading', item.auto_loading)
            settings.endGroup()
        settings.endGroup()

    def limits_for_axis(self, axis: AxisEnum) -> (float, float):
        for item in self.children:
            if item.axis == axis:
                return item.limit_min, item.limit_max
        raise ValueError('unknown axis')

    def reset_to_defaults(self):
        for item in self.children:
            names, min, max, auto_load = defaults[item.axis]
            item.funscript_names = split_functipt_names(names)
            item.limit_min = min
            item.limit_max = max
            item.auto_loading = auto_load
        self.dataChanged.emit(self.index(0, 1), self.index(len(self.children), 3))

    def funscript_conifg(self) -> list[FunscriptKitItem]:
        return self.children

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.children)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return 5

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if role == Qt.CheckStateRole:
            item: FunscriptKitItem = self.children[index.row()]
            col = index.column()
            if col == 4:
                if item.auto_loading:
                    return Qt.Checked
                else:
                    return Qt.Unchecked

        if role in (Qt.DisplayRole, Qt.EditRole):
            item: FunscriptKitItem = self.children[index.row()]
            col = index.column()
            if col == 0:
                if role == Qt.EditRole:
                    return item.axis
                if role == Qt.DisplayRole:
                    return item.axis.display_name()
            if col == 1:
                return ', '.join(item.funscript_names)
            if col == 2:
                return item.limit_min
            if col == 3:
                return item.limit_max
            if col == 4:
                if role == Qt.EditRole:
                    return None #item.auto_loading
                if role == Qt.DisplayRole:
                    return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if index.column() == 0:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled
        if index.column() == 4:
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable
        return Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def setData(self, index: QModelIndex, value: typing.Any, role: int = ...) -> bool:
        if role == Qt.CheckStateRole:
            item: FunscriptKitItem = self.children[index.row()]
            col = index.column()
            if col == 4:
                if value == Qt.Checked:
                    item.auto_loading = True
                    return True
                if value == Qt.Unchecked:
                    item.auto_loading = False
                    return True
            return False

        if role == Qt.EditRole:
            item: FunscriptKitItem = self.children[index.row()]
            col = index.column()
            if col == 0:
                item.axis = value
                return True
            if col == 1:
                item.funscript_names = split_functipt_names(str(value))
                return True
            if col == 2:
                try:
                    item.limit_min = float(value)
                    return True
                except ValueError:
                    return False
            if col == 3:
                try:
                    item.limit_max = float(value)
                    return True
                except ValueError:
                    return False
            if col == 4:
                try:
                    item.auto_loading = bool(value)
                    return True
                except ValueError:
                    return False

        return False

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> typing.Any:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if section == 0:
                return 'Axis'
            if section == 1:
                return 'Funscript name'
            if section == 2:
                return 'Limit min'
            if section == 3:
                return 'Limit max'
            if section == 4:
                return 'auto load'
        return None

    # def insertRow(self, row: int, parent: QModelIndex = ...) -> bool:
    #     self.beginInsertRows(QModelIndex(), len(self.children), len(self.children))
    #     self.children.append(FunscriptKitItem(
    #         AxisEnum.NONE,
    #         [],
    #         0,
    #         1,
    #         False
    #     ))
    #     self.endInsertRows()
    #     return True
    #
    # def removeRow(self, row: int, parent: QModelIndex = ...) -> bool:
    #     self.beginRemoveRows(QModelIndex(), row, row)
    #     del self.children[row]
    #     self.endRemoveRows()
    #     return True