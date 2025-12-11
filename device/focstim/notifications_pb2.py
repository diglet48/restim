"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 0, '', 'notifications.proto')
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x13notifications.proto\x12\x0bfocstim_rpc"\x12\n\x10NotificationBoot"*\n\x19NotificationPotentiometer\x12\r\n\x05value\x18\x01 \x01(\x02"\xd5\x01\n\x14NotificationCurrents\x12\r\n\x05rms_a\x18\x01 \x01(\x02\x12\r\n\x05rms_b\x18\x02 \x01(\x02\x12\r\n\x05rms_c\x18\x03 \x01(\x02\x12\r\n\x05rms_d\x18\x04 \x01(\x02\x12\x0e\n\x06peak_a\x18\x05 \x01(\x02\x12\x0e\n\x06peak_b\x18\x06 \x01(\x02\x12\x0e\n\x06peak_c\x18\x07 \x01(\x02\x12\x0e\n\x06peak_d\x18\x08 \x01(\x02\x12\x14\n\x0coutput_power\x18\t \x01(\x02\x12\x19\n\x11output_power_skin\x18\n \x01(\x02\x12\x10\n\x08peak_cmd\x18\x0b \x01(\x02"\xdf\x01\n\x1bNotificationModelEstimation\x12\x14\n\x0cresistance_a\x18\x01 \x01(\x02\x12\x14\n\x0creluctance_a\x18\x02 \x01(\x02\x12\x14\n\x0cresistance_b\x18\x03 \x01(\x02\x12\x14\n\x0creluctance_b\x18\x04 \x01(\x02\x12\x14\n\x0cresistance_c\x18\x05 \x01(\x02\x12\x14\n\x0creluctance_c\x18\x06 \x01(\x02\x12\x14\n\x0cresistance_d\x18\x07 \x01(\x02\x12\x14\n\x0creluctance_d\x18\x08 \x01(\x02\x12\x10\n\x08constant\x18\x14 \x01(\x02"W\n\x0fSystemStatsESC1\x12\x12\n\ntemp_stm32\x18\x01 \x01(\x02\x12\x12\n\ntemp_board\x18\x02 \x01(\x02\x12\r\n\x05v_bus\x18\x03 \x01(\x02\x12\r\n\x05v_ref\x18\x04 \x01(\x02"\xa3\x01\n\x14SystemStatsFocstimV3\x12\x12\n\ntemp_stm32\x18\x01 \x01(\x02\x12\x11\n\tv_sys_min\x18\x02 \x01(\x02\x12\x11\n\tv_sys_max\x18\x06 \x01(\x02\x12\r\n\x05v_ref\x18\x03 \x01(\x02\x12\x13\n\x0bv_boost_min\x18\x04 \x01(\x02\x12\x13\n\x0bv_boost_max\x18\x07 \x01(\x02\x12\x18\n\x10boost_duty_cycle\x18\x05 \x01(\x02"\x89\x01\n\x17NotificationSystemStats\x12,\n\x04esc1\x18\x01 \x01(\x0b2\x1c.focstim_rpc.SystemStatsESC1H\x00\x126\n\tfocstimv3\x18\x02 \x01(\x0b2!.focstim_rpc.SystemStatsFocstimV3H\x00B\x08\n\x06system"J\n\x17NotificationSignalStats\x12\x1e\n\x16actual_pulse_frequency\x18\x01 \x01(\x02\x12\x0f\n\x07v_drive\x18\x02 \x01(\x02"\x9b\x01\n\x13NotificationBattery\x12\x17\n\x0fbattery_voltage\x18\x01 \x01(\x02\x12 \n\x18battery_charge_rate_watt\x18\x02 \x01(\x02\x12\x13\n\x0bbattery_soc\x18\x03 \x01(\x02\x12\x1a\n\x12wall_power_present\x18\x04 \x01(\x08\x12\x18\n\x10chip_temperature\x18\x05 \x01(\x02"p\n\x14NotificationLSM6DSOX\x12\r\n\x05acc_x\x18\x01 \x01(\x05\x12\r\n\x05acc_y\x18\x02 \x01(\x05\x12\r\n\x05acc_z\x18\x03 \x01(\x05\x12\r\n\x05gyr_x\x18\x04 \x01(\x05\x12\r\n\x05gyr_y\x18\x05 \x01(\x05\x12\r\n\x05gyr_z\x18\x06 \x01(\x05"*\n\x17NotificationDebugString\x12\x0f\n\x07message\x18\x01 \x01(\t"F\n\x17NotificationDebugAS5311\x12\x0b\n\x03raw\x18\x01 \x01(\x05\x12\x0f\n\x07tracked\x18\x02 \x01(\x11\x12\r\n\x05flags\x18\x03 \x01(\x05"k\n\x17NotificationDebugEdging\x12\x1c\n\x14full_power_threshold\x18\x01 \x01(\x02\x12\x1f\n\x17reduced_power_threshold\x18\x02 \x01(\x02\x12\x11\n\treduction\x18\x03 \x01(\x02b\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'notifications_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_NOTIFICATIONBOOT']._serialized_start = 36
    _globals['_NOTIFICATIONBOOT']._serialized_end = 54
    _globals['_NOTIFICATIONPOTENTIOMETER']._serialized_start = 56
    _globals['_NOTIFICATIONPOTENTIOMETER']._serialized_end = 98
    _globals['_NOTIFICATIONCURRENTS']._serialized_start = 101
    _globals['_NOTIFICATIONCURRENTS']._serialized_end = 314
    _globals['_NOTIFICATIONMODELESTIMATION']._serialized_start = 317
    _globals['_NOTIFICATIONMODELESTIMATION']._serialized_end = 540
    _globals['_SYSTEMSTATSESC1']._serialized_start = 542
    _globals['_SYSTEMSTATSESC1']._serialized_end = 629
    _globals['_SYSTEMSTATSFOCSTIMV3']._serialized_start = 632
    _globals['_SYSTEMSTATSFOCSTIMV3']._serialized_end = 795
    _globals['_NOTIFICATIONSYSTEMSTATS']._serialized_start = 798
    _globals['_NOTIFICATIONSYSTEMSTATS']._serialized_end = 935
    _globals['_NOTIFICATIONSIGNALSTATS']._serialized_start = 937
    _globals['_NOTIFICATIONSIGNALSTATS']._serialized_end = 1011
    _globals['_NOTIFICATIONBATTERY']._serialized_start = 1014
    _globals['_NOTIFICATIONBATTERY']._serialized_end = 1169
    _globals['_NOTIFICATIONLSM6DSOX']._serialized_start = 1171
    _globals['_NOTIFICATIONLSM6DSOX']._serialized_end = 1283
    _globals['_NOTIFICATIONDEBUGSTRING']._serialized_start = 1285
    _globals['_NOTIFICATIONDEBUGSTRING']._serialized_end = 1327
    _globals['_NOTIFICATIONDEBUGAS5311']._serialized_start = 1329
    _globals['_NOTIFICATIONDEBUGAS5311']._serialized_end = 1399
    _globals['_NOTIFICATIONDEBUGEDGING']._serialized_start = 1401
    _globals['_NOTIFICATIONDEBUGEDGING']._serialized_end = 1508