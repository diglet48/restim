from PySide6.QtCore import QItemSelectionModel
from PySide6.QtCore import QModelIndex
from PySide6.QtWidgets import QDialog, QAbstractItemView, QFileDialog, QCheckBox


from qt_ui.additional_search_paths_dialog_ui import Ui_AdditionalSearchPathsDialog
from qt_ui.models.additional_search_paths import AdditionalSearchPathsModel
from qt_ui.file_dialog import FileDialog
from qt_ui import settings


class AdditionalSearchPathsDialog(QDialog, Ui_AdditionalSearchPathsDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.model = AdditionalSearchPathsModel.load_from_settings()
        self.listView.setModel(self.model)
        self.listView.setDragEnabled(True)
        self.listView.setDropIndicatorShown(True)
        self.listView.setDragDropMode(QAbstractItemView.InternalMove)
        self.listView.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # Add checkbox for search priority
        self.search_first_checkbox = QCheckBox("Search here first")
        self.search_first_checkbox.setToolTip("When checked, search these paths before the media file's directory")
        self.search_first_checkbox.setChecked(settings.additional_search_paths_first.get())
        self.verticalLayout.insertWidget(0, self.search_first_checkbox)

        self.actionAdd.triggered.connect(self.add_triggered)
        self.actionRemove.triggered.connect(self.remove_triggered)

    def add_triggered(self):
        dialog = FileDialog(self)
        dialog.setWindowTitle('Select directory')
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOptions(QFileDialog.ShowDirsOnly)
        ret = dialog.exec()

        files = dialog.selectedFiles()
        if ret and len(files):
            dir = files[0]  # dialog does not support selecting multiple dirs :(
            self.model.insertRow(self.model.rowCount())
            index = self.model.index(self.model.rowCount() - 1, 0)
            self.model.setData(index, dir)

    def remove_triggered(self):
        rows = [index.row() for index in self.listView.selectionModel().selectedRows()]
        if not rows:
            return

        self.model.beginResetModel()
        for row in rows[::-1]:
            self.model.removeRow(row, QModelIndex())
        self.model.endResetModel()

        index = self.model.index(min(self.model.rowCount() - 1, rows[0]))

        selection = self.listView.selectionModel()
        selection.select(index, QItemSelectionModel.Select)
        self.listView.setSelectionModel(selection)

    def accept(self) -> None:
        self.model.save_to_settings()
        settings.additional_search_paths_first.set(self.search_first_checkbox.isChecked())
        super(AdditionalSearchPathsDialog, self).accept()

    def reject(self) -> None:
        super(AdditionalSearchPathsDialog, self).reject()
