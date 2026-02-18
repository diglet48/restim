import serial
import time

from pathlib import Path

import stm32loader.bootloader
from PySide6.QtSerialPort import QSerialPortInfo
from serial.serialutil import SerialException

from PySide6.QtWidgets import QDialog, QFileDialog
from PySide6.QtCore import Signal, QThread

from qt_ui.focstim_flash_dialog_ui import Ui_FocStimFlashDialog
from qt_ui.file_dialog import FileDialog
from qt_ui import settings



BAUD = 115200


class FlashingThread(QThread):
    def __init__(self, com_port, file_path, parent=None):
        super(FlashingThread, self).__init__(parent)
        self.com_port = com_port
        self.file_path = file_path

    def run(self):
        # firmware_binary = Path(PATH).read_bytes()
        path = Path(self.file_path)
        if not path.is_file():
            self.report_message.emit("ERROR: could not open firmware binary")
            return

        firmware_binary = path.read_bytes()
        self.report_message.emit(f"firmware size: {len(firmware_binary)} bytes")

        if len(firmware_binary) / 1024 > 128:  # flash is 128k + 128k, only single-page firmware supported at this time
            self.report_message.emit("ERROR: firmware too large")

        com_port_path = QSerialPortInfo(self.com_port).systemLocation()
        self.report_message.emit(f'opening {com_port_path}')

        # Note: due to windows driver shit, closing the serial connection
        # toggles reset line and reboots the ESP32
        try:
            serial_connection = serial.Serial(
                port=com_port_path,
                baudrate=BAUD,
                bytesize=8, parity='E', stopbits=1,
                xonxoff=0,  # don't enable software flow control
                rtscts=0,  # don't enable RTS/CTS flow control
                timeout=1,  # set a timeout value, None for waiting forever
            )
        except SerialException as e:
            self.report_message.emit(str(e))
            return

        # prevent toggle RTS/DTR on port closing
        serial_connection.setRTS(False)
        serial_connection.setDTR(False)

        with serial_connection:
            stm32 = stm32loader.bootloader.Stm32Bootloader(
                serial_connection,
                verbosity=10,
                show_progress=False,
                device_family=None,
            )

            bootloader_active = self.poke_bootloader(serial_connection, stm32)

            if not bootloader_active:
                self.report_message.emit('Sending command to enter bootloader')
                self.enter_bootloader(serial_connection)
                time.sleep(0.05)
                bootloader_active = self.poke_bootloader(serial_connection, stm32)

            if not bootloader_active:
                self.report_message.emit('ERROR: Bootloader not active, giving up.')
                return

            self.report_message.emit('Bootloader activated!')

            stm32.detect_device()
            flash_size = stm32.get_flash_size()
            self.report_message.emit(f'device: {stm32.device}')
            self.report_message.emit(f'flash size: {flash_size}Kb')

            if stm32.device.product_id != 0x469:
                self.report_message.emit(f'ERROR: Unsupported CPU. Not a FOC-Stim v4 board?')
                return

            if flash_size != 256:
                self.report_message.emit(f'ERROR: Unsupported memory amount. Not a FOC-Stim v4 board?')
                return

            self.report_message.emit('Erasing flash...')
            stm32.extended_erase_memory()
            page1 = firmware_binary[:0x20000]  # 128k
            self.report_message.emit('writing firmware...')
            stm32.write_memory_data(0x0800_0000, page1)
            self.report_message.emit('verifying...')
            page1_readback = stm32.read_memory_data(0x0800_0000, len(page1))
            try:
                stm32.verify_data(page1_readback, page1)
            except stm32loader.bootloader.DataMismatchError as e:
                self.report_message.emit("Verify failed, please retry")
                self.report_message.emit(e)
                return

            self.report_message.emit('verified!')
            self.report_message.emit('starting program')
            stm32.go(0x08000000)


    def poke_bootloader(self, transport, stm32):
        self.report_message.emit("trying to talk with bootloader...")
        for attempt in range(4):
            transport.reset_input_buffer()
            stm32.write(stm32.Command.SYNCHRONIZE)
            read_data = bytearray(transport.read())
            if read_data and read_data[0] in (stm32.Reply.ACK, stm32.Reply.NACK):
                self.report_message.emit(f"Got {read_data}, OK, bootloader active.")
                return True
            elif read_data and read_data[0] == ord(b'~'):
                self.report_message.emit(f"Got {read_data}, bootloader not active.")
                return False
            else:
                self.report_message.emit(f"Got {read_data}, Retrying.")
        self.report_message.emit("Maximum retries exceeded")
        return False

    def enter_bootloader(self, transport):
        # RequestDebugEnterBootloader
        transport.write(b'~\x12\x05\x08{\xca>\x00\xa7\x8f~')
        transport.reset_input_buffer()

    # report_progress = Signal()
    report_message = Signal(str)



class FocStimFlashDialog(QDialog, Ui_FocStimFlashDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.flashing_thread = None

        self.pushButton.clicked.connect(self.flash)
        self.refresh.clicked.connect(self.refresh_serial_devices)
        self.open.clicked.connect(self.open_file_picker)

        self.refresh_serial_devices()

    def flash(self):
        self.textBrowser.clear()
        self.pushButton.setEnabled(False)

        self.flashing_thread = FlashingThread(
            self.focstim_port.currentData(),
            self.firmware_path.text()
        )
        self.flashing_thread.report_message.connect(self.textBrowser.append)

        self.flashing_thread.finished.connect(lambda : self.pushButton.setEnabled(True))
        self.flashing_thread.start()

    def refresh_serial_devices(self):
        selected_port_name = self.focstim_port.currentData()
        if selected_port_name is None:
            selected_port_name = settings.focstim_serial_port.get()


        self.focstim_port.clear()
        for port in QSerialPortInfo.availablePorts():
            self.focstim_port.addItem(
                f"{port.portName()} {port.description()}",
                port.portName()
            )

        if selected_port_name:
            index = self.focstim_port.findData(selected_port_name)
            if index != -1:
                self.focstim_port.setCurrentIndex(index)
            else:
                # if the port is no longer available, create a dummy port and add that.
                self.focstim_port.addItem(
                    f"{selected_port_name}",
                    selected_port_name
                )
                self.focstim_port.setCurrentIndex(self.focstim_port.count() - 1)

    def open_file_picker(self):
        dialog = FileDialog(self)
        dialog.setWindowTitle('Select FOC-Stim v4 firmware')
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilters(["*.bin"])
        ret = dialog.exec()

        if ret:
            files = dialog.selectedFiles()
            if files:
                self.firmware_path.setText(files[0])
            else:
                self.firmware_path.clear()
