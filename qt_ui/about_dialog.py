import logging
from PySide6.QtWidgets import QDialog

from qt_ui.about_dialog_ui import Ui_AboutDialog
from version import VERSION

logger = logging.getLogger('restim.bake_audio')

class AboutDialog(QDialog, Ui_AboutDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.setupUi(self)

        self.label.setText(
            f"""
<html>
	<head/>
	<body>
		<p><span style=" font-size:18pt; font-weight:700;">
			Restim
			</span>
		</p>
		<p>
			version: {VERSION}
		</p>
		<p>
			homepage: <a href="https://github.com/diglet48/restim">
			<span style=" text-decoration: underline; color:#334327;">
			https://github.com/diglet48/restim</span>
			</a>
		</p>
	</body>
</html>
            """
        )