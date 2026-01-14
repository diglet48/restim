from PySide6.QtCore import QSettings
import os


def get_settings_instance():
    cwd = os.getcwd()
    path = os.path.join(cwd, 'restim.ini')
    return QSettings(path, QSettings.IniFormat)


class Setting:
    def __init__(self, key, default_value, dtype):
        self.key = key
        self.default_value = default_value
        self.dtype = dtype

        self.cache = None

    def get(self):
        if self.cache is None:
            self.cache = get_settings_instance().value(self.key, self.default_value, self.dtype)
        return self.cache

    def set(self, value):
        if value != self.cache:
            get_settings_instance().setValue(self.key, value)
            self.cache = value


class NonPersistentSetting:
    def __init__(self, default_value):
        self.value = default_value

    def get(self):
        return self.value

    def set(self, value):
        pass


pulse_carrier_frequency = Setting('carrier/pulse_carrier_frequency', 700, float)
pulse_frequency = Setting('carrier/pulse_frequency', 50, float)
pulse_width = Setting('carrier/pulse_width', 5, float)
pulse_interval_random = Setting('carrier/pulse_interval_random', 10, float)
pulse_rise_time = Setting('carrier/pulse_rise_time', 10, float)
pulse_polarity = NonPersistentSetting('random')
pulse_device_emulation_mode = NonPersistentSetting('continuous (best)')
pulse_phase_offset_increment = NonPersistentSetting(0.0)

volume_default_level = Setting('volume/default_level', 10.0, float)
volume_ramp_target = Setting('volume/ramp_target', 1.0, float)
volume_ramp_increment_rate = Setting('volume/increment_rate', 1.0, float)
volume_inactivity_time = Setting('volume/inactivity_ramp_time', 3.0, float)
volume_inactivity_threshold = Setting('volume/inactivity_inactive_threshold', 2.0, float)
volume_inactivity_volume = Setting('volume/inactivity_reduction', 0.0, float)
volume_slow_start_time = Setting('volume/slow_start_time', 1.0, float)
tau_us = Setting('volume/tau_us', 355, float)

mk312_carrier = Setting('mk312/carrier_frequency', 700, float)

ab_test_volume = NonPersistentSetting(1.0)
ab_test_carrier = NonPersistentSetting(1000.0)
ab_test_train_duration = NonPersistentSetting(1.0)
ab_test_pulse_frequency = NonPersistentSetting(50.0)
ab_test_pulse_width = NonPersistentSetting(5.0)
ab_test_pulse_rise_time = NonPersistentSetting(2.0)
ab_test_pulse_interval_random = NonPersistentSetting(0.0)

vibration_1_enabled = Setting('vibration/vibration_1_enabled', False, bool)
vibration_1_frequency = Setting('vibration/vibration_1_frequency', 10, float)
vibration_1_strength = Setting('vibration/vibration_1_strength', 50, float)
vibration_1_left_right_bias = Setting('vibration/vibration_1_left_right_bias', 0.0, float)
vibration_1_high_low_bias = Setting('vibration/vibration_1_high_low_bias', 0.0, float)
vibration_1_random = Setting('vibration/vibration_1_random', 0, float)

vibration_2_enabled = Setting('vibration/vibration_2_enabled', False, bool)
vibration_2_frequency = Setting('vibration/vibration_2_frequency', 2, float)
vibration_2_strength = Setting('vibration/vibration_2_strength', 30, float)
vibration_2_left_right_bias = Setting('vibration/vibration_2_left_right_bias', 80.0, float)
vibration_2_high_low_bias = Setting('vibration/vibration_2_high_low_bias', 10.0, float)
vibration_2_random = Setting('vibration/vibration_2_random', 0, float)


threephase_calibration_neutral = Setting('hw_calibration/neutral', 0.0, float)
threephase_calibration_right = Setting('hw_calibration/right', 0.0, float)
threephase_calibration_center = Setting('hw_calibration/center', -0.7, float)

threephase_transform_combobox_selection = Setting('threephase_transform/combobox_selection', 0, int)
threephase_transform_enabled = Setting('threephase_transform/enabled', False, bool)
threephase_transform_rotate = Setting('threephase_transform/rotate', 0.0, float)
threephase_transform_mirror = Setting('threephase_transform/mirror', False, bool)
threephase_transform_limit_top = Setting('threephase_transform/limit_top', 1.0, float)
threephase_transform_limit_bottom = Setting('threephase_transform/limit_bottom', -1.0, float)
threephase_transform_limit_left = Setting('threephase_transform/limit_left', -1.0, float)
threephase_transform_limit_right = Setting('threephase_transform/limit_right', 1.0, float)
threephase_map_to_edge_start = Setting('threephase_transform/map_to_edge_start', 0.0, float)
threephase_map_to_edge_length = Setting('threephase_transform/map_to_edge_length', 200, float)
threephase_map_to_edge_invert = Setting('threephase_transform/map_to_edge_invert', False, bool)
threephase_exponent = NonPersistentSetting(0.0)

fourphase_calibration_a = Setting('calibration_four/a', 0.0, float)
fourphase_calibration_b = Setting('calibration_four/b', 0.0, float)
fourphase_calibration_c = Setting('calibration_four/c', 0.0, float)
fourphase_calibration_d = Setting('calibration_four/d', 0.0, float)
fourphase_calibration_center = Setting('calibration_four/center', 0.0, float)

device_config_device_type = Setting('device_configuration/device_type', 0, int)
device_config_waveform_type = Setting('device_configuration/waveform_type', 1, int)
device_config_min_freq = Setting('device_configuration/min_frequency', 500, float)
device_config_max_freq = Setting('device_configuration/max_frequency', 1000, float)
device_config_waveform_amplitude_amps = Setting('device_configuration/waveform_amplitude_amps', 0.120, float)

media_sync_default_source = Setting('media_sync/default_source', 'Internal', str)
media_sync_mpc_address = Setting('media_sync/mpc_address', 'http://127.0.0.1:13579', str)
media_sync_heresphere_address = Setting('media_sync/heresphere_address', '192.168.1.???:23554', str)
media_sync_vlc_address = Setting('media_sync/vlc_address', 'http://127.0.0.1:8080', str)
media_sync_vlc_username = Setting('media_sync/vlc_username', '', str)
media_sync_vlc_password = Setting('media_sync/vlc_password', '1234', str)
media_sync_kodi_address = Setting('media_sync/kodi_address', 'ws://127.0.0.1:9090', str)
media_sync_stop_audio_automatically = Setting('media_sync/stop_audio_automatically', True, bool)

audio_api = Setting("audio/api-name", "", str)
audio_output_device = Setting("audio/device-name", "", str)
audio_latency = Setting("audio/latency", 'high', str)

additional_search_paths = Setting('additional_search_paths', [], list)

file_dialog_last_dir = Setting('file_dialog_last_dir', '', str)

funscript_conversion_random_direction_change_probability = Setting('funscript/random_direction_change_probability', 0.1, float)

simfile_conversion_atk_sus_rel_index = Setting('simfile/atk_sus_rel_index', 1, int)
simfile_conversion_output_debug_scripts = Setting('simfile/output_debug_scripts', False, bool)

display_fps = Setting('display/fps', 60, float)
display_latency = Setting('display/latency', 200, float)

buttplug_wsdm_enabled = Setting("network/buttplug-wsdm-enabled", False, bool)
buttplug_wsdm_address = Setting("network/buttplug-wsdm-address", "ws://127.0.0.1:54817", str)
buttplug_wsdm_auto_expand = Setting("network/buttplug-wsdm-auto-expand", True, bool)


websocket_enabled = Setting("network/websocket-enabled", True, bool)
websocket_port = Setting("network/websocket-port", 12346, int)
websocket_localhost_only = Setting("network/websocket-localhost-only", False, bool)
tcp_enabled = Setting("network/tcp-enabled", True, bool)
tcp_port = Setting("network/tcp-port", 12347, int)
tcp_localhost_only = Setting("network/tcp-localhost-only", False, bool)
udp_enabled = Setting("network/udp-enabled", True, bool)
udp_port = Setting("network/udp-port", 12347, int)
udp_localhost_only = Setting("network/udp-localhost-only", False, bool)
serial_enabled = Setting("network/serial-enabled", False, bool)
serial_port = Setting("network/serial-port", "COM20", str)
serial_auto_expand = Setting("network/serial-auto-expand", True, bool)


focstim_serial_port = Setting("focstim/serial_port", '', str)
focstim_use_teleplot = Setting("focstim/use-teleplot", True, bool)
focstim_teleplot_prefix = Setting("focstim/teleplot_prefix", "", str)
focstim_dump_notifications_to_file = Setting("focstim/dump_notifications_to_file", False, bool)
focstim_communication_serial = Setting("focstim/communication_serial", True, bool)
focstim_communication_wifi = Setting("focstim/communication_wifi", False, bool)
focstim_ssid = Setting("focstim/wifi_ssid", '', str)
focstim_password = Setting("focstim/wifi_password", '', str)
focstim_ip = Setting("focstim/wifi_ip", '', str)

# AS5311 Sensor Data Sharing
focstim_as5311_source = Setting("focstim/as5311_source", 0, int)
focstim_as5311_serve = Setting("focstim/as5311_serve", False, bool)
focstim_as5311_serve_port = Setting("focstim/as5311_serve_port", 55534, int)
focstim_as5311_server_address = Setting("focstim/as5311_server_address", "127.0.0.1", str)
focstim_as5311_server_port = Setting("focstim/as5311_server_port", 55534, int)

neostim_serial_port = Setting("neostim/serial_port", '', str)

# Pattern preferences - we'll store this as a JSON string and convert to dict
import json

class DictSetting(Setting):
    """Special setting for dictionary data stored as JSON string"""
    def __init__(self, key, default_value):
        super().__init__(key, default_value, str)
    
    def get(self):
        if self.cache is None:
            json_str = get_settings_instance().value(self.key, json.dumps(self.default_value), str)
            try:
                self.cache = json.loads(json_str) if json_str else self.default_value
            except (json.JSONDecodeError, TypeError):
                self.cache = self.default_value
        return self.cache
    
    def set(self, value):
        json_str = json.dumps(value)
        current_cache = self.cache if self.cache is not None else self.default_value
        if json_str != json.dumps(current_cache):
            get_settings_instance().setValue(self.key, json_str)
            self.cache = value
            # Force immediate sync to ensure persistence
            get_settings_instance().sync()

pattern_enabled = DictSetting("patterns/enabled", {})
