"""
#
# Module: device.py
# Descr : Adds the sessionid to the data
#
# Copyright(c) 2016, Ciena Corporation. All rights reserved.
#
"""

import os
from bpprov.translators.base import Translator


class SessionId(Translator):
    schema = "device.json"
    schema_base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema")
    documentation = {
        'overview': (
            'Add the session_id of the running pipeline.  The data must already be a dict, '
            'the attribute "session" is added to the dict, with the sessionId value.'
        ),
        'examples': [{
            'description': 'assume here that the session.id="NE1"',
            'parameters': {},
            'input': {'data': {'a': 1, 'b': 'abc', 'c': 9}},
            'output': {'data': {'session': 'NE1', 'a': 1, 'b': 'abc', 'c': 9}},
        }]
    }

    def process(self, route_data):
        route_data.header['device'] = self.config.get_session_id()
        return route_data
