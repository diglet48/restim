from PySide6 import QtWidgets
from PySide6.QtWidgets import QStyleFactory


class VolumeWidget(QtWidgets.QProgressBar):
    def __init__(self, parent):
        QtWidgets.QProgressBar.__init__(self, parent)

        # use fusion style on Windows 11 because the
        # default progress bar styling is awful.
        if self.style().name() == 'windows11':
            self.setStyle(QStyleFactory.create("Fusion"))

    def set_value_and_tooltip(self, value: int, tooltip: str):
        self.setValue(value)
        self.setToolTip(tooltip)
