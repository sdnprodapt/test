"""
#
# Module: uniquekey.py
# Descr : generates a dict from the key provided parsing a list of dict data.
#
# Copyright(c) 2015, Cyan, Inc. All rights reserved.
#
"""

from jsonpointer import resolve_pointer
from bpprov.translators.base import Translator


import os
import copy


class UniqueKeyTranslator(Translator):
    '''
    Replaces the value with the pointer provided
    No Value found ?? Value is retained.
    '''

    schema = "dict-from-list.json"
    schema_base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema")

    def process(self, route_data):
        output = {}
        key = self.params.get("key")
        popchild = self.params.get("from-child", None)
        for data in route_data.data:
            if popchild:
                child = data.pop(popchild)
                if child is not None:
                    for childdata in child:
                        keyvalue = resolve_pointer(childdata, key, None)
                        if keyvalue is not None:
                            output[keyvalue] = copy.deepcopy(data)
                            output[keyvalue][popchild] = childdata
            else:
                keyvalue = resolve_pointer(data, key, None)
                if keyvalue is not None:
                    output[keyvalue] = data
        route_data.data = output
        return route_data


if __name__ == '__main__':
    pass
