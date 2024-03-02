from PyQt5.QtCore import QItemSelectionModel
from PyQt5.QtCore import QModelIndex
from PyQt5.QtWidgets import QDialog, QAbstractItemView, QFileDialog

from qt_ui.additional_search_paths_dialog_ui import Ui_AdditionalSearchPathsDialog
from qt_ui.models.additional_search_paths import AdditionalSearchPathsModel


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

        self.actionAdd.triggered.connect(self.add_triggered)
        self.actionRemove.triggered.connect(self.remove_triggered)

    def add_triggered(self):
        dir = QFileDialog.getExistingDirectory(self, 'Select Directory', None, QFileDialog.ShowDirsOnly)
        if dir:
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
        super(AdditionalSearchPathsDialog, self).accept()

    def reject(self) -> None:
        super(AdditionalSearchPathsDialog, self).reject()
