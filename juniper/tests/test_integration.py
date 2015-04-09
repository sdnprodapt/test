'''
Integration tests for Juniper provisioning
'''

import unittest
import json
import sys
from time import sleep
from urlparse import urlparse
import httplib as http

# So nosetest ignores this file
__test__ = False

CONNECT_TIMEOUT = 15

SIM_NETCONF_PORT = 22

SIM_USERNAME = 'admin'
SIM_PASSWORD = 'admin'

SIMS = {
    'mx960': {
        'device': 'mx960',
        'interface': None,
        'docker_settings': '/tmp/mx960'
    }
}

ADAPTER_SETTINGS_FILE = '/tmp/eajuniper'
ADAPTER_API = 'http://localhost:8080/api/v1'

class RestApi(object):
    """
    Supports basic communication with a HTTP/REST interface.
    """
    def __init__(self, url):
        self.baseUrl = url.rstrip('/')
        parse = urlparse(url)
        if ':' in parse.netloc:
            self.host, self.port = parse.netloc.split(':')
        else:
            self.host = parse.netloc
            self.port = '8080'

    def getHeaders(self):
        headers = {
            "Content-Type": "application/json",
        }
        return headers

    def buildUrl(self, url=''):
        return self.baseUrl + '/' + url.lstrip('/')

    def get(self, url):
        url = self.buildUrl(url)
        response = self.sendRequest(url, "GET", "")
        if response:
            content = response.read()
        if content:
            return json.loads(content)

    def post(self, url, data):
        url = self.buildUrl(url)
        body = json.dumps(data)
        response = self.sendRequest(url, "POST", body)
        if response:
            content = response.read()
        if content:
            return json.loads(content)

    def put(self, url, data):
        url = self.buildUrl(url)
        body = json.dumps(data)
        response = self.sendRequest(url, "PUT", body)
        if response:
            content = response.read()
        if content:
            return json.loads(content)

    def delete(self, url):
        url = self.buildUrl(url)
        response = self.sendRequest(url, "DELETE", "")
        if response:
            content = response.read()
        if content:
            return json.loads(content)

    def sendRequest(self, url, method, body):
        h = http.HTTPConnection(self.host, int(self.port))
        h.request(method, url, body, headers=self.getHeaders())
        return h.getresponse()


def poll_session(timeout, poll_time, api, uri, states=(u'CONNECTING', u'SYNCHRONIZING', u'INITIALIZING')):
    '''
    returns the session after either `timeout` is reached or if the session enters a
    state that is not in `states`
    returns a tuple of the session info and whether the operation timed out or not
    '''
    t = 0
    session = api.get(uri)
    while t < timeout and session['connectState'] in states:
        sleep(poll_time)  # dont constantly poll the api
        t += poll_time
        session = api.get(uri)

    return (session, t >= timeout)

class BaseTest(unittest.TestCase):
    def setUp(self):
        if not getattr(self, 'device', None):
            self.fail("Device not specified")

        self.api = RestApi(ADAPTER_API)

        request = {
            "authentication": {
                "netconf": {
                    "username": SIM_USERNAME,
                    "password": SIM_PASSWORD
                }
            },
            "connection": {
                "hostname": SIMS[self.device]['interface'],
                "netconf": {
                    "hostport": SIM_NETCONF_PORT
                }
            },
            "typeGroup": "/typeGroups/Juniper",
            "description": "Provision Tests"
        }

        response = self.api.post('sessions', request)
        self.session_uri = 'sessions/{}'.format(response['id'])

        session, timedout = poll_session(CONNECT_TIMEOUT, 1, self.api, self.session_uri)

        self.assertFalse(timedout)
        # Verify that it connected properly
        self.assertEqual(session['connectState'], u'CONNECTED')
        self.session = session
        self.device_uri = self.session['children'][0]

        self.maxDiff = None

    def tearDown(self):
        self.api.delete(self.session_uri)
        sessions = self.api.get('sessions')
        self.assertEqual(sessions['itemsAvailable'], 0)

    def get_command_and_expected(self, cmd_type, oid_class, object_name, parameters=None, oid_class_in_id=True):
        """
        if parameters is None, no parameters are present
        """
        oid_id_fmt = "OID_CLASS_{cls}:{cls}-{name}" if oid_class_in_id else "OID_CLASS_{cls}:{name}"
        command = {
            "type": cmd_type,
            "parameters": [
                "OID_CLASS_{}".format(oid_class),
                oid_id_fmt.format(cls=oid_class, name=object_name)
            ]
        }

        expected = {
            "message": 'Command Executed',
            "data": [
                "Command Executed",
                oid_id_fmt.format(cls=oid_class, name=object_name)
            ],
            "success": True
        }

        if parameters is not None:
            command['parameters'].append(parameters)
            expected['data'].append(parameters)

        return command, expected

    def oid_create_delete_test(self, oid_class, object_name, parameters, oid_class_in_id=True, create=True, delete=True):
        if create:
            command, expected = self.get_command_and_expected('createObject', oid_class,
                                                              object_name, parameters=parameters,
                                                              oid_class_in_id=oid_class_in_id)
            result = self.api.post('{}/oidOperation'.format(self.device_uri), command)
            self.assertDictEqual(result, expected)

        if delete:
            command, expected = self.get_command_and_expected('deleteObject', oid_class,
                                                              object_name, parameters=None,
                                                              oid_class_in_id=oid_class_in_id)
            result = self.api.post('{}/oidOperation'.format(self.device_uri), command)
            self.assertDictEqual(result, expected)


class MX960Test(BaseTest):
    def setUp(self):
        self.device = 'mx960'
        super(MX960Test, self).setUp()

    def test_oid_INTERFACE(self):
        params = [["encapsulation", "ethernet-ccc"],
                  ["description", "test"],
                  ["mtu", "4321"],
                  ["apply_groups_accept", ["uRPF_interface", "ARP_interface"]],
                  ["family_filter", "test-filter"]]
        self.oid_create_delete_test('INTERFACE', 'FAC_ge-0-0-0-0.0', params, oid_class_in_id=False)

    def test_oid_COS(self):
        params = [["scheduler_map", "test-map"]]
        self.oid_create_delete_test('COS', 'test1', params, oid_class_in_id=False)

    def test_oid_COSVPLS(self):
        params = [["classifiers_exp", "classifier"]]
        self.oid_create_delete_test('COSVPLS', 'test1', params)

    def test_oid_DISABLEINTERFACE(self):
        self.oid_create_delete_test('DISABLEINTERFACE', 'FAC_ge-0-0-0-0.0', [[]], oid_class_in_id=False)

    def test_oid_COMMIT(self):
        self.oid_create_delete_test('COMMIT', '', [[]], delete=False)

    def test_oid_FW3CPOLICER(self):
        params = [["cir", "10m"],
                  ["cbs", "100k"],
                  ["eir", "1m"],
                  ["ebs", "50k"],
                  ["color_mode", "aware"]]
        self.oid_create_delete_test('FW3CPOLICER', 'test_policer', params)

    def test_oid_FWFILTER(self):
        params = [["intf_specific", "true"],
                  ["terms", [{
                    "name": "t1",
                    "then_3cpolicer": "single-rate test",
                    "then_loss_priority": "loss_prio",
                    "then_forwarding_class": "fwd_class",
                    "then_accept": "true"
                  }]]]
        self.oid_create_delete_test('FWFILTER', 'inet-filter1', params)

    def test_oid_FWPOLICER(self):
        params = [["cir", "5m"],
                  ["cbs", "100k"],
                  ["then", "discard"]]
        self.oid_create_delete_test('FWPOLICER', 'test_policer', params)

    def test_oid_L2CIRCUIT(self):
        params = [["vcid", "NS_12345"],
                  ["description", "test circuit"]]
        self.oid_create_delete_test('L2CIRCUIT', 'FAC_ge-0-0-0-0.0-10.12.23.24', params, oid_class_in_id=False)

    def test_oid_ROUTINGINSTANCES(self):
        params = [["mac_table_size", "100"],
                  ["interface_mac_limit", "10"],
                  ["description", "test routing instance"]]
        self.oid_create_delete_test('ROUTINGINSTANCES', 'FAC_ge-0-0-0-0.0-NS_12345-123', params, oid_class_in_id=False)

    def test_oid_P2P_EPL(self):
        # FWPOLICER -> FWFILTER -> INTERFACE -> L2CIRCUIT -> deleteDISABLEINTERFACE -> COS -> COMMIT
        params = [["cir", "5m"],
                  ["cbs", "100k"],
                  ["then", "discard"]]
        self.oid_create_delete_test('FWPOLICER', 'test_policer', params, delete=False)
        params = [["intf_specific", "true"],
                  ["terms", [{
                    "name": "t1",
                    "then_3cpolicer": "single-rate test",
                    "then_loss_priority": "loss_prio",
                    "then_forwarding_class": "fwd_class",
                    "then_accept": "true"
                  }]]]
        self.oid_create_delete_test('FWFILTER', 'inet-filter1', params, delete=False)
        params = [["encapsulation", "ethernet-ccc"],
                  ["description", "test"],
                  ["mtu", "4321"],
                  ["apply_groups_accept", ["uRPF_interface", "ARP_interface"]],
                  ["family_filter", "filter1"]]
        self.oid_create_delete_test('INTERFACE', 'FAC_ge-0-0-0-0.0', params, oid_class_in_id=False, delete=False)
        params = [["vcid", "NS_12345"],
                  ["description", "test circuit"]]
        self.oid_create_delete_test('L2CIRCUIT', 'FAC_ge-0-0-0-0.0-10.12.23.24', params, oid_class_in_id=False, delete=False)
        # delete the disable, which enables the interface
        self.oid_create_delete_test('DISABLEINTERFACE', 'FAC_ge-0-0-0-0.0', [[]], oid_class_in_id=False, create=False)
        params = [["scheduler_map", "test-map"]]
        self.oid_create_delete_test('COS', 'test1', params, oid_class_in_id=False, delete=False)
        self.oid_create_delete_test('COMMIT', '', [[]], delete=False)

        # deprovisioning
        self.oid_create_delete_test('COS', 'test1', params, oid_class_in_id=False, create=False)
        # create the disable, which disables the interface
        self.oid_create_delete_test('DISABLEINTERFACE', 'FAC_ge-0-0-0-0.0', [[]], oid_class_in_id=False, delete=False)
        self.oid_create_delete_test('L2CIRCUIT', 'FAC_ge-0-0-0-0.0-10.12.23.24', None, oid_class_in_id=False, create=False)
        self.oid_create_delete_test('INTERFACE', 'FAC_ge-0-0-0-0.0', None, oid_class_in_id=False, create=False)
        self.oid_create_delete_test('FWFILTER', 'inet-filter1', None, create=False)
        self.oid_create_delete_test('FWPOLICER', 'test_policer', None, create=False)
        self.oid_create_delete_test('COMMIT', '', [[]], delete=False)


    def test_oid_MP_ELAN(self):
        # deleteDISABLEINTERFACE -> FWPOLICER -> FWFILTER -> INTERFACE -> ROUTINGINSTANCES -> COS -> COSVPLS -> COMMIT
        # delete the disable, which enables the interface
        self.oid_create_delete_test('DISABLEINTERFACE', 'FAC_ge-0-0-0-0.0', [[]], oid_class_in_id=False, create=False)
        params = [["cir", "5m"],
                  ["cbs", "100k"],
                  ["then", "discard"]]
        self.oid_create_delete_test('FWPOLICER', 'test_policer', params, delete=False)
        params = [["intf_specific", "true"],
                  ["terms", [{
                    "name": "t1",
                    "then_policer": "test_policer",
                    "then_loss_priority": "loss_prio",
                    "then_forwarding_class": "fwd_class",
                    "then_accept": "true"
                  }]]]
        self.oid_create_delete_test('FWFILTER', 'inet-filter1', params, delete=False)
        params = [["encapsulation", "ethernet-ccc"],
                  ["description", "test"],
                  ["mtu", "4321"],
                  ["apply_groups_accept", ["uRPF_interface", "ARP_interface"]],
                  ["family_filter", "filter1"]]
        self.oid_create_delete_test('INTERFACE', 'FAC_ge-0-0-0-0.0', params, oid_class_in_id=False, delete=False)
        params = [["mac_table_size", "100"],
                  ["interface_mac_limit", "10"],
                  ["description", "test routing instance"]]
        self.oid_create_delete_test('ROUTINGINSTANCES', 'FAC_ge-0-0-0-0.0-NS_12345-123', params, oid_class_in_id=False, delete=False)
        params = [["scheduler_map", "test-map"]]
        self.oid_create_delete_test('COS', 'test1', params, oid_class_in_id=False, delete=False)
        params = [["classifiers_exp", "classifier"]]
        self.oid_create_delete_test('COSVPLS', 'testvpls1', params, delete=False)
        self.oid_create_delete_test('COMMIT', '', [[]], delete=False)


        # deprovisioning
        self.oid_create_delete_test('COSVPLS', 'testvpls1', None, create=False)
        self.oid_create_delete_test('COS', 'test1', None, oid_class_in_id=False, create=False)
        self.oid_create_delete_test('ROUTINGINSTANCES', 'FAC_ge-0-0-0-0.0-NS_12345-123', None, oid_class_in_id=False, create=False)
        self.oid_create_delete_test('INTERFACE', 'FAC_ge-0-0-0-0.0', None, oid_class_in_id=False, create=False)
        self.oid_create_delete_test('FWFILTER', 'inet-filter1', None, create=False)
        self.oid_create_delete_test('FWPOLICER', 'test_policer', None, create=False)
        # create the disable, which disables the interface
        self.oid_create_delete_test('DISABLEINTERFACE', 'FAC_ge-0-0-0-0.0', [[]], oid_class_in_id=False, delete=False)
        self.oid_create_delete_test('COMMIT', '', [[]], delete=False)


if __name__ == '__main__':

    # Get simulator ips from the files generated by the docker start scripts
    for dev, sim in SIMS.iteritems():
        with open(sim['docker_settings'], 'r') as f:
            lines = [line for line in f]
            # First line is the command used to start the adapter
            # second line is the container id
            # third line is the ip
            sim['interface'] = lines[2].strip()
            if sim['interface'] == '':
                raise ValueError('ERROR: Sim {} does not have an ip. Verify the container started properly'.format(
                                 sim['device']
                                 ))
            print('{} at {}'.format(sim['device'], sim['interface']))

    # Get the EA containers ports from /tmp/ea
    with open(ADAPTER_SETTINGS_FILE, 'r') as f:
        lines = [line for line in f]
        # First line in the file is the ip of the adapter
        # Second line is the container id
        host = lines[0].strip()
        if host in {'', None}:
            raise ValueError('ERROR: No hostname or ip given for EA')
            sys.exit(1)
        port = '8080'
        ADAPTER_API = 'http://{}:{}/api/v1'.format(host, port)
        print('EA at {}'.format(ADAPTER_API))

    # Delete any sessions that the adapter knows about, just incase
    api = RestApi(ADAPTER_API)
    sessions = api.get('sessions')
    for session in sessions['items']:
        api.delete('sessions/{}'.format(session['id']))

    unittest.main()
