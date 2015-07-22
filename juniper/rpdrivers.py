import copy
from easdk.access.session import SessionAccess
from easdk.exceps import ExecutionError

from twisted.internet import defer

from easdk.controller import Controller
from easdk.bpprovif import execute as bpprov_execute
from rpsdk.drivers import (
    RpSdkResourceCudDriver,
    RpSdkResourceGetDriver,
    RpSdkResourceListDriver)
from rpsdk.model import RpSdkResource
from rpsdk.utils.cyclonehelpers import ApiNotFoundError, RpError


def pop_class(d):
    d.pop('__class__', None)
    for v in d.itervalues():
        if isinstance(v, dict):
            pop_class(v)

def _session(session):
    auth = session.authentication.asDict()
    pop_class(auth)
    conn = session.connection.asDict()
    pop_class(conn)
    return {
        'id': session.id,
        'description': session.description,
        'authentication': auth,
        'connection': conn,
        'typeGroup': session.typeGroup.id,
        'connectState': session.connectState,
    }

def _device(device):
    return {
        'serialNumber': device.serialNumber,
        'swType': device.swType,
        'swVersion': device.swVersion,
        'swImage': device.swImage,
        'session': device.session,
        'elementType': device.elementType,
        'type': device.type,
        'id': device.id,
        'deviceVersion': device.deviceVersion,
    }


class EasdkBpprovHelper(object):
    def __init__(self, tenant_id, product_id, device_id, prid_field,
                 device_namespace_props=None, label_field=None, is_domain_manager=False):
        self.product_id = product_id
        self.device_id = device_id
        self.prid_field = prid_field
        self.label_field = label_field
        self.tenant_id = tenant_id
        self.is_domain_manager = is_domain_manager
        self.device_namespace_props = device_namespace_props or []

    def get_prid(self, provider_resource_id):
        if not self.is_domain_manager:
            return provider_resource_id.partition("::")[2]
        return provider_resource_id

    def map_props_to_market(self, props, discovered, device_id_field=None, device_id=None):
        device_id = device_id or self.device_id
        _device_id_field = device_id_field or 'device'
        if device_id_field is not None or not self.is_domain_manager:
            props[_device_id_field] = device_id
        if not self.is_domain_manager:
            for prop_name in self.device_namespace_props:
                if prop_name in props:
                    props[prop_name] = "{}::{}".format(
                        device_id, props[prop_name])

        data = {
            "providerResourceId": self._get_prid_from_props(props, device_id),
            "properties": props,
            "orchState": "active",
            "productId": self.product_id,
            "discovered": discovered,
            }

        if self.label_field and props[self.label_field]:
            data.update({"label": str(props[self.label_field])})

        return RpSdkResource(**data)

    def map_props_to_domain(self, props):
        if not self.is_domain_manager:
            for prop_name in self.device_namespace_props:
                if prop_name in props.keys():
                    props[prop_name] = props[prop_name].partition('::')[2]
        return props

    def _get_prid_from_props(self, obj, device_id):
        if not self.is_domain_manager:
            return "{}::{}".format(device_id, obj[self.prid_field])
        return obj[self.prid_field]

    @defer.inlineCallbacks
    def execute_command(self, session, command, parameters=None):
        try:
            data = yield bpprov_execute(session, command, parameters)
            defer.returnValue(data)
        except ExecutionError as ex:
            try:
                route_data = ex.data.get('route_data')
                header = route_data.header
                reason = header.get('reason')
                code = header.get('errorDict', {"statusCode": 400}).get('statusCode', 400)
            except:
                reason = "Bp-prov command {} failed execution".format(command)
                code = 500
            raise RpError(code, reason)


class EasdkBpprovListDriver(RpSdkResourceListDriver):
    def __init__(self,
                 tenant_id,
                 product_id,
                 rpc_commands,
                 prid_field,
                 device_namespace_props=None,
                 label_field=None,
                 is_domain_manager=False,
                 device_id_field=None,
                 session=None,
                 reactor=None):
        self.product_id = product_id
        self.rpc_commands = rpc_commands
        self.prid_field = prid_field
        self.root = Controller.instance().root
        # The session id this driver should read from associated with
        self.session = session
        self.device_id_field = device_id_field
        from twisted.internet import reactor as twisted_reactor

        self.reactor = reactor or twisted_reactor

        self.helper = EasdkBpprovHelper(tenant_id,
                                        self.product_id,
                                        None,
                                        self.prid_field,
                                        device_namespace_props,
                                        label_field,
                                        is_domain_manager)

    def __repr__(self):
        return "<%s %s>" % (
            self.__class__.__name__,
            self.product_id
        )

    @defer.inlineCallbacks
    def list_resources(self):
        result = []
        rpc_is_list = 'list' in self.rpc_commands
        rpc_command = self.rpc_commands["list"] if rpc_is_list else self.rpc_commands["get"]
        if self.session:
            device = self.root.devices[self.session.id]
            if self.session.connectState == "CONNECTED":
                cmd_res = yield self.helper.execute_command(self.session, rpc_command)
                if rpc_is_list:
                    objs = [self.helper.map_props_to_market(obj, True, device_id_field=self.device_id_field, device_id=device.id)
                            for obj in cmd_res]
                    result.extend(objs)
                else:
                    obj = self.helper.map_props_to_market(cmd_res, True, device_id_field=self.device_id_field, device_id=device.id)
                    result.append(obj)
        else:
            devices = self.root.devices
            for device in devices.values():
                if device.session.connectState == "CONNECTED":
                    cmd_res = yield self.helper.execute_command(device.session, rpc_command)
                    if rpc_is_list:
                        objs = [self.helper.map_props_to_market(obj, True, device_id_field=self.device_id_field, device_id=device.id)
                                for obj in cmd_res]
                        result.extend(objs)
                    else:
                        obj = self.helper.map_props_to_market(cmd_res, True, device_id_field=self.device_id_field, device_id=device.id)
                        result.append(obj)
        defer.returnValue(result)


class EasdkBpprovGetDriver(RpSdkResourceGetDriver):
    def __init__(self,
                 device_id,
                 tenant_id,
                 product_id,
                 rpc_commands,
                 prid_field,
                 device_namespace_props=None,
                 label_field=None,
                 device_id_field=None,
                 is_domain_manager=False,
                 reactor=None):
        self.product_id = product_id
        self.rpc_commands = rpc_commands
        self.prid_field = prid_field
        self.device_id = device_id
        self.root = Controller.instance().root
        self.device_id_field = device_id_field
        from twisted.internet import reactor as twisted_reactor

        self.reactor = reactor or twisted_reactor

        self.helper = EasdkBpprovHelper(tenant_id,
                                        self.product_id,
                                        self.device_id,
                                        self.prid_field,
                                        device_namespace_props,
                                        label_field,
                                        is_domain_manager)

    def __repr__(self):
        return "<%s %s %s>" % (
            self.__class__.__name__,
            self.device_id,
            self.product_id
        )

    @defer.inlineCallbacks
    def get_resource(self, provider_resource_id):
        rpc_command = self.rpc_commands["get"]

        device = self.root.devices.get(self.device_id)
        if not device:
            raise RpError(404, "Device {} not found".format(self.device_id))

        params = {
            self.prid_field: self.helper.get_prid(provider_resource_id)
        }
        data = yield self.helper.execute_command(device.session, rpc_command, parameters=params)

        defer.returnValue(self.helper.map_props_to_market(data, True, device_id_field=self.device_id_field))


class EasdkBpprovCudDriver(RpSdkResourceCudDriver):
    def __init__(self,
                 device_id,
                 tenant_id,
                 product_id,
                 rpc_commands,
                 prid_field,
                 device_namespace_props=None,
                 label_field=None,
                 device_id_field=None,
                 is_domain_manager=False,
                 reactor=None):
        self.product_id = product_id
        self.rpc_commands = rpc_commands
        self.prid_field = prid_field
        self.device_id = device_id
        self.device_id_field = device_id_field
        self.root = Controller.instance().root
        from twisted.internet import reactor as twisted_reactor

        self.reactor = reactor or twisted_reactor

        self.helper = EasdkBpprovHelper(tenant_id,
                                     self.product_id,
                                     self.device_id,
                                     self.prid_field,
                                     device_namespace_props,
                                     label_field,
                                     is_domain_manager)

    def __repr__(self):
        return "<%s %s %s>" % (
            self.__class__.__name__,
            self.device_id,
            self.product_id
        )

    @defer.inlineCallbacks
    def create_resource(self, resource):
        rpc_command = self.rpc_commands["post"]

        properties = copy.deepcopy(resource.properties)
        properties = self.helper.map_props_to_domain(properties)

        device = self.root.devices[self.device_id]
        if not device:
            raise RpError(404, "Device {} not found".format(self.device_id))

        create_resp = yield self.helper.execute_command(device.session, rpc_command, parameters=properties)

        provider_id = create_resp.get(self.prid_field)
        if provider_id is None:
            raise RpError(500, "Unable to determine provider ID from created resource")

        params = {
            self.prid_field: provider_id
        }
        data = yield self.helper.execute_command(device.session, self.rpc_commands["get"], parameters=params)

        defer.returnValue(self.helper.map_props_to_market(data, False))

    @defer.inlineCallbacks
    def delete_resource(self, resource):
        rpc_command = self.rpc_commands["delete"]
        device = self.root.devices[self.device_id]
        if not device:
            raise RpError(404, "Device {} not found".format(self.device_id))

        params = {
            self.prid_field: self.helper.get_prid(resource.providerResourceId)
        }
        yield self.helper.execute_command(device.session, rpc_command, parameters=params)
        # TODO process result

    @defer.inlineCallbacks
    def update_resource(self, resource):
        rpc_command = self.rpc_commands["put"]

        properties = copy.deepcopy(resource.properties)

        # ensure the properties contains the prid field as this is required
        # by the bpprov library
        properties[self.prid_field] = self.helper.get_prid(
            resource.providerResourceId)

        properties = self.helper.map_props_to_domain(properties)

        device = self.root.devices[self.device_id]
        if not device:
            raise RpError(404, "Device {} not found".format(self.device_id))

        yield self.helper.execute_command(device.session, rpc_command, parameters=properties)
        params = {
            self.prid_field: self.helper.get_prid(resource.providerResourceId)
        }
        data = yield self.helper.execute_command(device.session, self.rpc_commands["get"], parameters=params)

        defer.returnValue(self.helper.map_props_to_market(data, False))


class EasdkDriverHelper(object):
    DEVICE_FIELDS = {
        "deviceVersion",
        "serialNumber",
        "swImage",
        "swVersion",
        "type",
        "elementType",
        "swType",
        "id",
    }

    def __init__(self, tenant_id, product_id):
        self.product_id = product_id
        self.tenant_id = tenant_id

    def get_resource(self, obj, discovered):
        data = {
            "productId": self.product_id,
            "providerResourceId": obj["id"],
            "discovered": discovered,
            "orchState": obj["orchState"],
            "properties": obj,
        }
        if discovered:
            data.update({'label': obj['connection']['hostname']})

        del obj['id']
        del obj['orchState']

        return RpSdkResource(**data)

    def get_orch_state(self, session):
        stateMap = dict.fromkeys(['INITIALIZING', 'CONNECTING', 'SYNCHRONIZING'], 'activating')
        stateMap.update({'DISCONNECTED': 'unknown',
                         'ERROR': 'failed',
                         'DELETING': 'terminating',
                         "CONNECTED": "active"})
        return stateMap[session['connectState']]

    def merge_device_session_info(self, device, session, state=None):
        obj = {}
        if device is not None:
            for field in self.DEVICE_FIELDS:
                if field in device:
                    obj[field] = device[field]
        obj["authentication"] = session["authentication"]
        obj["connection"] = session["connection"]
        obj["typeGroup"] = session["typeGroup"]
        obj["id"] = session["id"]
        obj["orchState"] = state if state is not None else self.get_orch_state(session)
        return obj


class EasdkDeviceGetDriver(RpSdkResourceGetDriver):
    def __init__(self, tenant_id, product_id, top_down=False, resource=None, reactor=None):
        super(EasdkDeviceGetDriver, self).__init__()
        from twisted.internet import reactor as twisted_reactor

        self.reactor = reactor or twisted_reactor
        self.helper = EasdkDriverHelper(tenant_id, product_id)
        self.top_down = top_down
        self.resource = resource

        self.root = Controller.instance().root

    def __str__(self):
        return "<%s>" % (self.__class__.__name__)

    @defer.inlineCallbacks
    def get_resource(self, provider_resource_id):

        # Assuming that the session and the device will have same ID.
        # Try to get the session first. If the EA is restarted, the session will be gone
        # Re-create the session if we have a hold of the device resource from market,
        # and it is a managed (i.e. non-discovered) resource
        #
        # Also it is possible that the session is created but the device is not
        # yet identified. For this case, a resource for the session part will be returned

        session = self.root.sessions.get(provider_resource_id)
        if not session:
            if not self.top_down or not self.resource or self.resource.discovered:
                raise RpError(404, "Device {} not found".format(provider_resource_id))
            else:
                createdResource = yield self.top_down_create_resource(self.resource)
                defer.returnValue(createdResource)

        device = self.root.devices.get(provider_resource_id)

        obj = self.helper.merge_device_session_info(device, session)
        resource = self.helper.get_resource(obj, True)
        defer.returnValue(resource)

    @defer.inlineCallbacks
    def top_down_create_resource(self, resource):
        cudDriver = EasdkDeviceCudDriver(self.helper.tenant_id, self.helper.product_id)
        retVal = yield cudDriver.create_resource(resource)
        defer.returnValue(retVal)


class EasdkDeviceListDriver(RpSdkResourceListDriver):
    def __init__(self, tenant_id, product_id, reactor=None, session=None):
        super(EasdkDeviceListDriver, self).__init__()
        self.product_id = product_id
        from twisted.internet import reactor as twisted_reactor

        self.reactor = reactor or twisted_reactor
        self.helper = EasdkDriverHelper(tenant_id, product_id)

        self.session = session
        self.root = Controller.instance().root

    def __str__(self):
        return "<%s>" % (self.__class__.__name__)

    def list_resources(self):
        result = []
        if self.session:
            device = self.root.devices[self.session.id]
            obj = self.helper.merge_device_session_info(_device(device), _session(self.session))
            result.append(self.helper.get_resource(obj, True))
        else:
            for device in self.root.devices.values():
                session = device.session
                obj = self.helper.merge_device_session_info(_device(device), _session(session))
                result.append(self.helper.get_resource(obj, True))
        return result


class EasdkDeviceCudDriver(RpSdkResourceCudDriver):
    def __init__(self, tenant_id, product_id, reactor=None):
        self.product_id = product_id
        self.helper = EasdkDriverHelper(tenant_id, self.product_id)
        from twisted.internet import reactor as twisted_reactor

        self.reactor = reactor or twisted_reactor

        self.root = Controller.instance().root
        self.session_access = SessionAccess(self.root)

    def __str__(self):
        return "<%s>" % (self.__class__.__name__)

    @defer.inlineCallbacks
    def create_resource(self, resource):
        properties = {key: resource.properties[key] for key in
                      ['authentication', 'connection', 'typeGroup', 'id', 'description']
                      if key in resource.properties}
        if resource.providerResourceId is not None:
            properties['id'] = resource.providerResourceId

        yield self.session_access.preCreate(properties, None)
        session = self.session_access.doCreate(properties, None, self.root.sessions)
        yield self.session_access.postCreate(session, None)

        obj = self.helper.merge_device_session_info(None, _session(session), "activating")
        defer.returnValue(self.helper.get_resource(obj, False))

    def delete_resource(self, resource):
        device = self.root.devices.get(resource.providerResourceId)
        if device:
            session = device.session
        else:
            session = self.root.sessions.get(resource.providerResourceId)

        if session:
            self.session_access.doDelete(session, "RPCDelete", self.root.sessions)

    def get_resource(self, prid):
        device = self.root.devices.get(prid)
        if not device:
            raise RpError(404, "Device with id {} not found".format(prid))
        session = device.session
        obj = self.helper.merge_device_session_info(_device(device), _session(session))
        self.helper.get_resource(obj, True)

    def update_resource(self, resource):
        # EA framework does not yet support updates to devices or sessions,
        # this should be modelled in the device resource type(s)
        raise NotImplementedError
