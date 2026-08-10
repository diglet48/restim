"""
GUI to configure the external HereSphere funscript-resolution API.

Hand-coded QDialog (no .ui file) that reads/writes the funscript/heresphere_api_*
settings. Reached from the media settings widget ("HereSphere API..." button).
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QCheckBox, QLineEdit,
    QDoubleSpinBox, QPlainTextEdit, QLabel, QDialogButtonBox,
)

from qt_ui import settings


class HeresphereApiDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('HereSphere funscript API')
        self.resize(480, 380)

        self.enabled_checkbox = QCheckBox('Enable HereSphere funscript API')

        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText('http://host:port')

        self.timeout_spinbox = QDoubleSpinBox()
        self.timeout_spinbox.setRange(0.1, 60.0)
        self.timeout_spinbox.setSingleStep(0.5)
        self.timeout_spinbox.setSuffix(' s')

        self.mappings_edit = QPlainTextEdit()
        self.mappings_edit.setPlaceholderText(
            '/server/prefix=>/local/prefix\n(one mapping per line)')

        form = QFormLayout()
        form.addRow(self.enabled_checkbox)
        form.addRow('Server URL', self.url_edit)
        form.addRow('Timeout', self.timeout_spinbox)
        form.addRow(QLabel('Path mappings (server=>local):'))
        form.addRow(self.mappings_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(buttons)

        self._load()

    def _load(self):
        self.enabled_checkbox.setChecked(settings.heresphere_api_enabled.get())
        self.url_edit.setText(settings.heresphere_api_url.get())
        self.timeout_spinbox.setValue(settings.heresphere_api_timeout.get())
        self.mappings_edit.setPlainText('\n'.join(settings.heresphere_api_path_mappings.get()))

    def accept(self):
        settings.heresphere_api_enabled.set(self.enabled_checkbox.isChecked())
        settings.heresphere_api_url.set(self.url_edit.text().strip())
        settings.heresphere_api_timeout.set(self.timeout_spinbox.value())
        mappings = [line.strip() for line in self.mappings_edit.toPlainText().splitlines()
                    if line.strip()]
        settings.heresphere_api_path_mappings.set(mappings)
        super().accept()
