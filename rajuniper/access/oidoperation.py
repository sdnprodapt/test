'''
Copyright(c) 2014, Cyan, Inc. All rights reserved.
'''
from cymlrest.access import RootAccess
from cymlrest.exceptions import RequestError
from twisted.internet import defer

import logging
from bpprov.manager import SessionDb
log = logging.getLogger(__name__)


class OidOperationAccess(RootAccess):
    def __init__(self, root):
        super(OidOperationAccess, self).__init__(root, 'oidOperation', 'oidOperation')

    @defer.inlineCallbacks
    def safeCreate(self, req, collection):
        success = False
        message = ""
        data = ""
        log.debug("safeCreate req.data: %s", req.data)

        method = req.data.get('type')
        parameters = req.data.get('parameters')

        device = collection.__parent__()
        endpoint = SessionDb.get_endpoint(device.session.id, 'netconf')

        if endpoint:
            fn = getattr(endpoint, method)
            cr = yield fn(*parameters)
            message = '\n'.join(cr.stdOut) if isinstance(cr.stdOut, list) else cr.stdOut
            success = cr.success
            data = cr.data
        else:
            message = "Session unavailable"

        result = {'success': success,
                  'message': message,
                  'data': data,
                  }

        if not success:
            raise RequestError(500, result)

        log.debug("safeCreate result: %s", result)

        defer.returnValue(result)
