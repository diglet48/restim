import typing
from dataclasses import dataclass
from PySide6.QtCore import QModelIndex, Qt, QAbstractTableModel

from qt_ui.device_wizard.axes import AxisEnum, all_axis
from qt_ui.settings import get_settings_instance


defaults = {
    AxisEnum.POSITION_ALPHA: ('alpha', 'L0', -1, 1, True, True),
    AxisEnum.POSITION_BETA: ('beta', 'L1', -1, 1, True, True),
    AxisEnum.POSITION_GAMMA: ('gamma', '', -1, 1, True, True),
    AxisEnum.VOLUME_API: ('volume', 'V0', 0, 1, True, True),
    AxisEnum.VOLUME_EXTERNAL: ('', '', 0, 1, False, False),
    AxisEnum.CARRIER_FREQUENCY: ('frequency', 'C0', 500, 1000, True, True),

    AxisEnum.PULSE_FREQUENCY: ('pulse_frequency', 'P0', 0, 100, True, True),
    AxisEnum.PULSE_WIDTH: ('pulse_width', 'P1', 4, 10, True, True),
    AxisEnum.PULSE_INTERVAL_RANDOM: ('pulse_interval_random', 'P2', 0, 1, True, True),
    AxisEnum.PULSE_RISE_TIME: ('pulse_rise_time', 'P3', 2, 20, True, True),

    AxisEnum.VIBRATION_1_FREQUENCY: ('vib1_frequency', '', 0, 100, True, True),
    AxisEnum.VIBRATION_1_STRENGTH: ('vib1_strength', '', 0, 1, True, True),
    AxisEnum.VIBRATION_1_LEFT_RIGHT_BIAS: ('vib1_left_right_bias', '', 0, 1, True, True),
    AxisEnum.VIBRATION_1_HIGH_LOW_BIAS: ('vib1_up_down_bias', '', 0, 1, True, True),
    AxisEnum.VIBRATION_1_RANDOM: ('vib1_random', '', 0, 1, True, True),

    AxisEnum.VIBRATION_2_FREQUENCY: ('vib2_frequency', '', 0, 100, True, True),
    AxisEnum.VIBRATION_2_STRENGTH: ('vib2_strength', '', 0, 1, True, True),
    AxisEnum.VIBRATION_2_LEFT_RIGHT_BIAS: ('vib2_left_right_bias', '', 0, 1, True, True),
    AxisEnum.VIBRATION_2_HIGH_LOW_BIAS: ('vib2_up_down_bias', '', 0, 1, True, True),
    AxisEnum.VIBRATION_2_RANDOM: ('vib2_random', '', 0, 1, True, True),

    AxisEnum.INTENSITY_A: ('e1', '', 0, 1, True, True),
    AxisEnum.INTENSITY_B: ('e2', '', 0, 1, True, True),
    AxisEnum.INTENSITY_C: ('e3', '', 0, 1, True, True),
    AxisEnum.INTENSITY_D: ('e4', '', 0, 1, True, True),
}

@dataclass
class FunscriptKitItem:
    axis: AxisEnum
    funscript_names: [str]
    tcode_axis_name = str
    limit_min: float
    limit_max: float
    auto_loading: bool
    allow_funscript_control: bool


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
            kit.children.append(FunscriptKitItem(axis, '', None, None, False, False))

        settings = get_settings_instance()
        settings.beginGroup('funscript_configuration')
        for item in kit.children:
            default_funscript_name, default_tcode_axis_name, default_min, default_max, default_auto_load, default_allow_funscript_control = defaults[item.axis]

            settings.beginGroup(item.axis.settings_key())
            item.funscript_names = split_functipt_names(settings.value('funscript_names', default_funscript_name, str))
            item.limit_min = settings.value('limit_min', default_min, float)
            item.limit_max = settings.value('limit_max', default_max, float)
            item.auto_loading = settings.value('auto_loading', default_auto_load, bool)
            item.tcode_axis_name = settings.value('tcode_axis', default_tcode_axis_name, str)
            item.allow_funscript_control = default_allow_funscript_control
            settings.endGroup()

        settings.endGroup()
        return kit

    def save_to_settings(self):
        settings = get_settings_instance()
        settings.beginGroup('funscript_configuration')
        for item in self.children:
            settings.beginGroup(item.axis.settings_key())
            settings.setValue('funscript_names', ', '.join(item.funscript_names))
            settings.setValue('tcode_axis', item.tcode_axis_name)
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
            names, tcode, min, max, auto_load, allow_funscript_control = defaults[item.axis]
            item.funscript_names = split_functipt_names(names)
            item.tcode_axis_name = tcode
            item.limit_min = min
            item.limit_max = max
            item.auto_loading = auto_load
            item.allow_funscript_control = allow_funscript_control
        self.dataChanged.emit(self.index(0, 1), self.index(len(self.children), 3))

    def funscript_conifg(self) -> list[FunscriptKitItem]:
        return self.children

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.children)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return 6

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if role == Qt.ItemDataRole.CheckStateRole:
            item: FunscriptKitItem = self.children[index.row()]
            col = index.column()
            if col == 5:
                if item.auto_loading:
                    return Qt.CheckState.Checked
                else:
                    return Qt.CheckState.Unchecked

        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            item: FunscriptKitItem = self.children[index.row()]
            col = index.column()
            if col == 0:
                if role == Qt.ItemDataRole.EditRole:
                    return item.axis
                if role == Qt.ItemDataRole.DisplayRole:
                    return item.axis.display_name()
            if col == 1:
                if item.allow_funscript_control:
                    return ', '.join(item.funscript_names)
                else:
                    return ''
            if col == 2:
                return item.tcode_axis_name
            if col == 3:
                return item.limit_min
            if col == 4:
                return item.limit_max
            if col == 5:
                if role == Qt.ItemDataRole.EditRole:
                    return None #item.auto_loading
                if role == Qt.ItemDataRole.DisplayRole:
                    return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        item: FunscriptKitItem = self.children[index.row()]
        if index.column() == 0:
            return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        if index.column() == 1:
            if item.allow_funscript_control:
                return Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
            else:
                return Qt.ItemFlag.ItemIsSelectable
        if index.column() == 5:
            return Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable
        return Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled

    def setData(self, index: QModelIndex, value: typing.Any, role: int = ...) -> bool:
        if role == Qt.ItemDataRole.CheckStateRole:
            value = Qt.CheckState(value)
            item: FunscriptKitItem = self.children[index.row()]
            col = index.column()
            if col == 5:
                if value == Qt.CheckState.Checked:
                    item.auto_loading = True
                    return True
                if value == Qt.CheckState.Unchecked:
                    item.auto_loading = False
                    return True
            return False

        if role == Qt.ItemDataRole.EditRole:
            item: FunscriptKitItem = self.children[index.row()]
            col = index.column()
            if col == 0:
                item.axis = value
                return True
            if col == 1:
                item.funscript_names = split_functipt_names(str(value))
                return True
            if col == 2:
                item.tcode_axis_name = str(value)
                return True
            if col == 3:
                try:
                    item.limit_min = float(value)
                    return True
                except ValueError:
                    return False
            if col == 4:
                try:
                    item.limit_max = float(value)
                    return True
                except ValueError:
                    return False
            if col == 5:
                try:
                    item.auto_loading = bool(value)
                    return True
                except ValueError:
                    return False

        return False

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> typing.Any:
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            if section == 0:
                return 'Axis'
            if section == 1:
                return 'Funscript name'
            if section == 2:
                return 'T-Code axis'
            if section == 3:
                return 'Limit min'
            if section == 4:
                return 'Limit max'
            if section == 5:
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