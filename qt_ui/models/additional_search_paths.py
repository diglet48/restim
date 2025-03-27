from PySide6.QtCore import Qt, QModelIndex, QStringListModel

from qt_ui import settings


class AdditionalSearchPathsModel(QStringListModel):
    def __init__(self, *args, **kwargs):
        super(AdditionalSearchPathsModel, self).__init__(*args, **kwargs)

    # drag-move in listview only, not drag-copy
    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if index.isValid():
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsEditable
        return super(AdditionalSearchPathsModel, self).flags(index)

    @staticmethod
    def load_from_settings():
        paths = settings.additional_search_paths.get()
        return AdditionalSearchPathsModel(paths)

    def save_to_settings(self):
        settings.additional_search_paths.set(self.stringList())

