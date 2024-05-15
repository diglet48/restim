from PyQt5.QtWidgets import QFileDialog

from qt_ui import settings


# A file dialog that persistently stores the last directory.
class FileDialog(QFileDialog):
    def __init__(self, parent=None):
        super(FileDialog, self).__init__(parent)
        self.setDirectory(settings.file_dialog_last_dir.get())

    def exec(self) -> int:
        ret = super(FileDialog, self).exec()
        if ret:
            settings.file_dialog_last_dir.set(self.directory().absolutePath())
        return ret