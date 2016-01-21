import time
from uuid import uuid4

ALARM_TOPIC = 'bp.ra.v1.alarms'
ALARM_TYPE = 'bp.v1.AlarmEvent'
ALARM_ACTIVE_STATE = 'set'
ALARM_CLEAR_STATE = 'clear'
ALARM_STATE_MAP = {
    'CREATE': ALARM_ACTIVE_STATE,
    'UPDATE': ALARM_ACTIVE_STATE,
    'DELETE': ALARM_CLEAR_STATE
}
ALARM_SERVICE_AFF_MAP = {
    'MAJOR': 'SERVICE_AFFECTING',
    'CRITICAL': 'SERVICE_AFFECTING',
    'WARNING': 'NON_SERVICE_AFFECTING',
    'MINOR': 'NON_SERVICE_AFFECTING',
    'INFO': 'NON_SERVICE_AFFECTING'
}
RA_TYPE = 'Firefly'
POWER_SUPPLY_FAILURE = '1.3.6.1.4.1.2636.4.1.1'
FAN_FAILURE = '1.3.6.1.4.1.2636.4.1.2'
OVER_TEMPERATURE = '1.3.6.1.4.1.2636.4.1.3'
REDUNDANCY_SWITCH_OVER = '1.3.6.1.4.1.2636.4.1.4'
FRU_REMOVAL = '1.3.6.1.4.1.2636.4.1.5'
FRU_INSERTION = '1.3.6.1.4.1.2636.4.1.6'
FRU_POWER_OFF = '1.3.6.1.4.1.2636.4.1.7'
FRU_POWER_ON = '1.3.6.1.4.1.2636.4.1.8'
FRU_FAILED = '1.3.6.1.4.1.2636.4.1.9'
FRU_OFFLINE = '1.3.6.1.4.1.2636.4.1.10'
FRU_ONLINE = '1.3.6.1.4.1.2636.4.1.11'
FRU_CHECK = '1.3.6.1.4.1.2636.4.1.12'
FEB_SWITCH_OVER = '1.3.6.1.4.1.2636.4.1.13'
HARDDISK_FAILED = '1.3.6.1.4.1.2636.4.1.14'
HARDDISK_MISSING = '1.3.6.1.4.1.2636.4.1.15'
BOOT_FROM_BACKUP = '1.3.6.1.4.1.2636.4.1.16'
FM_LINK_ERROR = '1.3.6.1.4.1.2636.4.1.17'
FM_CELL_DROP_ERROR = '1.3.6.1.4.1.2636.4.1.18'
EXT_SRC_LOCK_LOST = '1.3.6.1.4.1.2636.4.1.19'
POWER_SUPPLY_OK = '1.3.6.1.4.1.2636.4.2.1'
FAN_OK = '1.3.6.1.4.1.2636.4.2.2'
TEMPERATURE_OK = '1.3.6.1.4.1.2636.4.2.3'
FRU_OK = '1.3.6.1.4.1.2636.4.2.4'
EXT_SRC_LOCK_ACQUIRED = '1.3.6.1.4.1.2636.4.2.5'

ALARM_LIST = {
    POWER_SUPPLY_FAILURE: ('POWER SUPPLY FAILURE', 'MAJOR', ALARM_ACTIVE_STATE, 'Power supply failure'),
    POWER_SUPPLY_OK: ('POWER SUPPLY FAILURE', 'MAJOR', ALARM_CLEAR_STATE, 'Power supply failure'),
    FAN_FAILURE: ('FAN FAILURE', 'CRITICAL', ALARM_ACTIVE_STATE, 'Fan failure'),
    FAN_OK: ('FAN FAILURE', 'MAJOR', ALARM_CLEAR_STATE, 'Fan failure'),
    OVER_TEMPERATURE: ('OVER TEMPERATURE', 'CRITICAL', ALARM_ACTIVE_STATE, 'Over temperature'),
    TEMPERATURE_OK: ('OVER TEMPERATURE', 'MAJOR', ALARM_CLEAR_STATE, 'Over temperature'),
    FRU_REMOVAL: ('FRU REMOVAL', 'NOTICE', ALARM_ACTIVE_STATE, 'FRU removed'),
    FRU_INSERTION: ('FRU REMOVAL', 'NOTICE', ALARM_CLEAR_STATE, 'FRU removed'),
    FRU_POWER_OFF: ('FRU POWER OFF', 'NOTICE', ALARM_ACTIVE_STATE, 'FRU Power off'),
    FRU_POWER_ON: ('FRU POWER OFF', 'NOTICE', ALARM_CLEAR_STATE, 'FRU Power off'),
    FRU_FAILED: ('FRU FAILED', 'WARNING', ALARM_ACTIVE_STATE, 'FRU Failed'),
    FRU_OK: ('FRU FAILED', 'MAJOR', ALARM_CLEAR_STATE, 'FRU Failed'),
    FRU_OFFLINE: ('FRU OFFLINE', 'NOTICE', ALARM_ACTIVE_STATE, 'FRU Offline'),
    FRU_ONLINE: ('FRU OFFLINE', 'NOTICE', ALARM_CLEAR_STATE, 'FRU Offline'),
    EXT_SRC_LOCK_LOST: ('EXT SRC LOCK LOST', 'MAJOR', ALARM_ACTIVE_STATE, 'Ext source lock lost'),
    EXT_SRC_LOCK_ACQUIRED: ('EXT SRC LOCK LOST', 'MAJOR', ALARM_CLEAR_STATE, 'Ext source lock lost'),
    REDUNDANCY_SWITCH_OVER: ('REDUNDANCY SWITCH OVER', 'MAJOR', ALARM_ACTIVE_STATE, 'Redundancy switch over'),
    FRU_CHECK: ('FRU CHECK', 'NOTICE', ALARM_ACTIVE_STATE, 'FRU check'),
    FEB_SWITCH_OVER: ('FEB SWITCH OVER', 'MAJOR', ALARM_ACTIVE_STATE, 'FRU switch over'),
    HARDDISK_FAILED: ('HARDDISK FAILED', 'MAJOR', ALARM_ACTIVE_STATE, 'Harddisk failed'),
    HARDDISK_MISSING: ('HARDDISK MISSING', 'MAJOR', ALARM_ACTIVE_STATE, 'Harddisk missing'),
    BOOT_FROM_BACKUP: ('BOOT FROM BACKUP', 'MAJOR', ALARM_ACTIVE_STATE, 'Boot from backup'),
    FM_LINK_ERROR: ('FM LINK ERROR', 'MAJOR', ALARM_ACTIVE_STATE, 'Link error'),
    FM_CELL_DROP_ERROR: ('FM CELL DROP ERROR', 'MAJOR', ALARM_ACTIVE_STATE, 'Cell drop error')
}


def convert_time(t):
    '''ISO time year-month-dayThour-mins-seconds-millisecondsZ '''
    from datetime import datetime

    if type(t) in [str, unicode]:
        new_t = datetime.strptime(t, '%Y-%m-%d %H:%M:%S %Z')
    else:
        new_t = datetime.fromtimestamp(t / 1e3)
    new_t = new_t.strftime('%Y-%m-%dT%H:%M:%S.%f%Z')[:-3]
    new_t += "Z"
    return new_t


def check_alarm_data(data, **kwargs):
    '''
    '''
    if data:
        alarmInformation = data['alarm-information']
        if alarmInformation and 'alarm-detail' not in alarmInformation:
            # There are no active alarms
            alarmInformation['alarm-detail'] = {}

    return data


def sync_alarm_data(data, **kqargs):
    '''
    The alarms are syncd to kafka, to make sure the RA sync works fine
    return an empty dict.
    '''
    return {}


def convert_alarm(data, **kwargs):
    '''
    '''
    alarmOID = data['snmpTrapOID']
    alarmDetails = ALARM_LIST.get(alarmOID, None)
    if alarmDetails:
        resource = '%s-%s/%s/%s' % (data['jnxName'], data['jnxL1Index'],
                                    data['jnxL2Index'], data['jnxL3Index'])
        alarmData = {
            'alarm-time': long(data['sysUpTimeInstance']),
            'alarm-short-description': '%s %s' % (resource, alarmDetails[0]),
            'alarm-class': alarmDetails[1],
            'alarm-op': alarmDetails[2],
            'alarm-description': alarmDetails[3],
            'alarm-resource': resource
        }
        return process_alarms({'alarms': [alarmData]})

    return []


def process_alarms(data, **kwargs):
    ''' Convert the alarms to a format as expected by bpocore kafka exchange '''

    alarms = []
    for alarmDict in data.get('alarms', []):
        alarmType = alarmDict.get('alarm-short-description', '')
        resourceName, alarmType = alarmType.split(' ', 1)
        alarmDict['alarm-short-description'] = alarmType.replace(' ', '-').upper()
        alarmDict['alarm-resource'] = 'Firefly:%s' % resourceName
        alarm = convert_alarm_to_rasdk_format(alarmDict)
        alarms.append(alarm)

    return alarms


def convert_alarm_to_rasdk_format(alarmData, event_state='CREATE'):
    ''' Creates a alarm dict which can be published to bpocore alarm processor '''

    severity = alarmData.get('alarm-class', 'MINOR').upper()
    return {
        'version': 1,
        'header': {
            'roleIds': [],
            'envelopeId': str(uuid4()),
            'timestamp': convert_time(time.time())
        },
        'event': {
            '_type': ALARM_TYPE,
            'id': str(uuid4()),
            'resource': alarmData.get('alarm-resource', '%s:%s' % ('firefly', 'chassis')),
            'op': alarmData.get('alarm-op', ALARM_ACTIVE_STATE),
            'time': convert_time(alarmData.get('alarm-time', time.time())),
            'severity': severity,
            'additionalText': alarmData.get('alarm-description', ''),
            'conditionSource': 'MANAGER',
            'nativeConditionType': alarmData.get('alarm-short-description', ''),
            'nativeConditionTypeQualifier': 'chassis',
            'server': {
                'id': "1",
                'name': RA_TYPE
            },
            'serviceAffecting': ALARM_SERVICE_AFF_MAP.get(severity, 'UNKNOWN'),
            'additionalAttributes': {
            }
        }
    }


def push_alarms(data, **kwargs):
    toKafka = []

    append_tags = kwargs.get('append_tags', False)

    if append_tags:
        toKafka.append(build_sync_status_header('start', str(uuid4())))

    for alarm in data:
        toKafka.append({
            'topic': ALARM_TOPIC,
            'key': alarm.get('nodeId', alarm['header']['envelopeId']),
            'msg': alarm
        })

    if append_tags:
        toKafka.append(build_sync_status_header('complete', str(uuid4())))

    return toKafka


def build_sync_status_header(state, domainID=''):
    return {
        'topic': ALARM_TOPIC,
        'key': domainID,
        'msg': {
            'version': 1,
            'header': {
                'roleIds': [],
                'envelopeId': str(uuid4()),
                'timestamp': convert_time(time.time())
            },
            'event': {
                '_type': 'bp.v1.SyncEvent',
                'id': "1",
                'object_type': 'alarms',
                'op': state
            }
        }
    }
