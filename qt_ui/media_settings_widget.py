import functools
import logging
import os
import pathlib

from PySide6.QtCore import Qt

from funscript.collect_funscripts import Resource
from net.media_source.vlc import VLC
from net.media_source.kodi import Kodi
from qt_ui.additional_search_paths_dialog import AdditionalSearchPathsDialog
from qt_ui.heresphere_api_dialog import HeresphereApiDialog
from PySide6.QtGui import QShortcut, QKeySequence
from funscript import heresphere_api
from qt_ui.device_wizard.axes import AxisEnum

from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QAbstractItemView, QFileDialog

from net.media_source.heresphere import HereSphere
from net.media_source.interface import MediaConnectionState
from qt_ui.file_dialog import FileDialog
from qt_ui.media_settings_widget_ui import Ui_MediaSettingsWidget

from net.media_source.internal import Internal
from net.media_source.mpc import MPC
from qt_ui.models.script_mapping import FunscriptTreeItem, ScriptMappingModel
from qt_ui.widgets.table_view_with_combobox import ComboBoxDelegate, ButtonDelegate
from qt_ui.models import funscript_kit, additional_search_paths
from qt_ui.models.funscript_kit import FunscriptKitItem
from qt_ui import settings

logger = logging.getLogger('restim.media_settings')


class _MediaSettingsWidget(type(QtWidgets.QWidget), type(Ui_MediaSettingsWidget)):
    pass


class MediaSettingsWidget(QtWidgets.QWidget, Ui_MediaSettingsWidget, metaclass=_MediaSettingsWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setupUi(self)

        self.media_sync = [
            Internal(),
            MPC(self),
            HereSphere(self),
            VLC(self),
            Kodi(self),
        ]
        self.media_sync[0].connectionStatusChanged.connect(functools.partial(self.connection_status_changed, 0))
        self.media_sync[1].connectionStatusChanged.connect(functools.partial(self.connection_status_changed, 1))
        self.media_sync[2].connectionStatusChanged.connect(functools.partial(self.connection_status_changed, 2))
        self.media_sync[3].connectionStatusChanged.connect(functools.partial(self.connection_status_changed, 3))
        self.media_sync[4].connectionStatusChanged.connect(functools.partial(self.connection_status_changed, 4))

        self.comboBox.addItem("Internal")
        self.comboBox.addItem(QIcon(":/restim/media_players/mpc-hc.png"), "MPC-HC")
        self.comboBox.addItem(QIcon(":/restim/media_players/heresphere.png"), "HereSphere")
        self.comboBox.addItem(QIcon(":/restim/media_players/vlc.svg"), "VLC")
        self.comboBox.addItem(QIcon(":/restim/media_players/kodi.png"), "Kodi")
        self.comboBox.currentIndexChanged.connect(self.media_index_changed)

        self.loaded_media_path = None
        self.current_index = 0

        self.model = ScriptMappingModel()
        self.model.dataChanged.connect(self.on_data_changed)
        self.treeView.setModel(self.model)
        self.treeView.expandAll()

        combobox_items = []
        combobox_items.append(('(none)', AxisEnum.NONE))
        for item in funscript_kit.FunscriptKitModel.load_from_settings().children:
            item: FunscriptKitItem
            if item.allow_funscript_control:
                combobox_items.append((item.axis.display_name(), item.axis))
        self.treeView.setItemDelegateForColumn(1, ComboBoxDelegate(combobox_items, self))
        self.treeView.setEditTriggers(
            # QAbstractItemView.AllEditTriggers
            QAbstractItemView.CurrentChanged |
            QAbstractItemView.SelectedClicked |
            QAbstractItemView.DoubleClicked |
            QAbstractItemView.EditKeyPressed |
            QAbstractItemView.AnyKeyPressed
        )
        self.treeView.setItemDelegateForColumn(2, ButtonDelegate(self))
        self.treeView.setMouseTracking(True)

        self.comboBox.setCurrentIndex(self.comboBox.findText(settings.media_sync_default_source.get()))
        self.stop_audio_automatically_checkbox.setChecked(settings.media_sync_stop_audio_automatically.get())

        header = self.treeView.header()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        header.resizeSection(1, 160)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Fixed)
        header.resizeSection(2, 50)

        self.add_funscript_button.clicked.connect(self.open_add_funscripts_dialog)
        self.additional_search_paths_button.clicked.connect(self.open_search_paths_dialog)
        self.heresphere_api_button = QtWidgets.QPushButton("HereSphere API…")
        self.horizontalLayout_2.addWidget(self.heresphere_api_button)
        self.heresphere_api_button.clicked.connect(self.open_heresphere_api_dialog)

        # HereSphere: a scene may expose several funscripts -> selector (hidden if <=1)
        self.ft_funscript_combo = QtWidgets.QComboBox()
        self.ft_funscript_combo.setToolTip("HereSphere funscript (Ctrl+F to cycle)")
        self.ft_funscript_combo.setVisible(False)
        self.horizontalLayout_2.addWidget(self.ft_funscript_combo)
        self.ft_funscript_combo.currentIndexChanged.connect(self._on_ft_funscript_selected)
        self._ft_next_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        self._ft_next_shortcut.activated.connect(self._select_next_heresphere_funscript)
        self.reload_scripts_button.clicked.connect(self.reload_scripts)
        self.media_index_changed()

        self.media_offset_spinbox.valueChanged.connect(self.refresh_media_offset)
        self.media_offset_spinbox.setValue(settings.media_sync_time_offset_ms.get() / 1000.0)

    def open_add_funscripts_dialog(self):
        self.dialogOpened.emit()  # trigger stop audio

        dlg = FileDialog()
        dlg.setFileMode(QFileDialog.ExistingFiles)
        dlg.setNameFilters(["*.funscript"])

        if dlg.exec():
            self.model.beginResetModel()
            filenames = dlg.selectedFiles()
            kit = funscript_kit.FunscriptKitModel.load_from_settings()
            for filename in filenames:
                item = FunscriptTreeItem(Resource(pathlib.Path(filename)))
                self.model.auto_link_funscript(kit, item)
                self.model.add_funscript_resource_manual(item)
            self.model.endResetModel()
            self.treeView.expandAll()
            self.funscriptMappingChanged.emit()

    def open_search_paths_dialog(self):
        self.dialogOpened.emit()  # trigger stop audio
        dlg = AdditionalSearchPathsDialog()
        if dlg.exec():
            # Attempt to re-load funscripts
            self.detect_resources_for_media_file(self.loaded_media_path)

    def open_heresphere_api_dialog(self):
        self.dialogOpened.emit()  # trigger stop audio
        dlg = HeresphereApiDialog(self)
        if dlg.exec():
            # config may have changed -> re-detect funscripts for current media
            self.detect_resources_for_media_file(self.loaded_media_path)

    def reload_scripts(self):
        self.detect_resources_for_media_file(self.loaded_media_path)

    def on_data_changed(self, topleft, bottomright, roles):
        if Qt.EditRole in roles:
            # print('on data changed', roles, topleft.row(), bottomright.row())
            self.funscriptMappingChanged.emit()

    def media_index_changed(self):
        self.dialogOpened.emit()  # stop audio before possibly modifying important vars.

        any_funscripts_removed = self.model.clear_auto_detected_funscripts()
        old_interface = self.media_sync[self.current_index]
        new_interface = self.media_sync[self.comboBox.currentIndex()]
        self.current_index = self.comboBox.currentIndex()
        old_interface.disable()
        new_interface.enable()
        self.refresh_connection_status()
        self.refresh_media_offset()

        # emit because there is a chance we switched to/from internal
        # media, which does not support funscripts
        self.funscriptMappingChanged.emit()

    def connection_status_changed(self, index: int):
        if index == self.current_index:
            self.refresh_connection_status()

    def refresh_connection_status(self):
        self.connectionStatusChanged.emit(self.media_sync[self.current_index].state())
        connector = self.media_sync[self.current_index]
        if connector.is_internal():
            self.connection_status.setText('Connected')
            self.lineEdit.clear()
        elif connector.is_media_loaded():
            self.connection_status.setText('Connected')
            a, b = os.path.split(connector.media_path())
            self.lineEdit.setText(b)
        elif connector.is_connected():
            self.connection_status.setText('Connected, no file loaded.')
            self.lineEdit.clear()
        else:
            self.model.clear_auto_detected_funscripts()
            self.connection_status.setText('Attempting to connect...')
            self.lineEdit.clear()

        new_path = connector.media_path()

        if self.loaded_media_path != new_path:
            self.detect_resources_for_media_file(new_path)

    def detect_resources_for_media_file(self, new_path):
        self.loaded_media_path = new_path

        # Wrapped so a broken funscript / unreachable path logs an error instead
        # of crashing the app. try/finally keeps the Qt model out of a stuck
        # "reset" state even if detection raises.
        import time
        _t = {}
        try:
            self.model.beginResetModel()
            try:
                self.model.clear_auto_detected_funscripts()
                if new_path:
                    dirname = os.path.dirname(new_path)
                    basename = os.path.basename(new_path)
                    search_paths = [dirname] + settings.additional_search_paths.get()
                    _t0 = time.perf_counter()
                    self.model.detect_funscripts_from_path(search_paths, basename)
                    _t['detect'] = time.perf_counter() - _t0
            finally:
                self.model.endResetModel()

            _t1 = time.perf_counter()
            self.treeView.expandAll()
            _t['expandAll'] = time.perf_counter() - _t1
            _t2 = time.perf_counter()
            self.model.auto_link_funscripts(funscript_kit.FunscriptKitModel.load_from_settings())
            _t['auto_link'] = time.perf_counter() - _t2
            if _t:
                logger.debug('[perf] detect_resources %s -> %s', os.path.basename(new_path or ''),
                             ', '.join(f'{k}={v:.2f}s' for k, v in _t.items()))
        except Exception:
            logger.exception('failed to detect funscripts for %s', new_path)

        self._refresh_heresphere_funscript_selector()
        self.funscriptMappingChanged.emit()

    def _refresh_heresphere_funscript_selector(self):
        """Show/populate the HereSphere funscript combo when the scene has >1."""
        count = heresphere_api.available_count()
        combo = self.ft_funscript_combo
        combo.blockSignals(True)
        combo.clear()
        if count > 1:
            for i, name in enumerate(heresphere_api.funscript_names()):
                combo.addItem(f'{i + 1}/{count} — {name}')
            combo.setCurrentIndex(heresphere_api.current_index())
            combo.setVisible(True)
        else:
            combo.setVisible(False)
        combo.blockSignals(False)

    def _on_ft_funscript_selected(self, index):
        if index >= 0 and heresphere_api.select(index):
            self.detect_resources_for_media_file(self.loaded_media_path)

    def _select_next_heresphere_funscript(self):
        if heresphere_api.select_next():
            self.detect_resources_for_media_file(self.loaded_media_path)

    def has_media_file_loaded(self):
        return bool(self.loaded_media_path)

    def autostart_enabled(self):
        return not self.stop_audio_automatically_checkbox.isChecked()

    def is_connected(self):
        media = self.media_sync[self.current_index]
        return media.is_connected()

    def is_playing(self):
        media = self.media_sync[self.current_index]
        return media.is_playing()

    def is_internal(self):
        media = self.media_sync[self.current_index]
        return media.is_internal()

    def current_media_sync(self):
        return self.media_sync[self.current_index]

    def refresh_media_offset(self):
        offset = self.media_offset_spinbox.value()
        media = self.media_sync[self.current_index]
        media.set_media_sync_offset(offset)

    def save_settings(self):
        settings.media_sync_time_offset_ms.set(self.media_offset_spinbox.value() * 1000)

    dialogOpened = QtCore.Signal()  # emitted whenever a dialog is opened which promps audio stop.
    connectionStatusChanged = QtCore.Signal(MediaConnectionState)  # emitted whenever video player connection status changes.
    funscriptMappingChanged = QtCore.Signal()  # emitted whenever new funscript files are added, removed or modified