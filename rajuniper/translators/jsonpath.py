"""
#
# Module: jsonpointertranslator.py
# Descr : Converts Generic Json to device specific Json based on the Model json pointers
#
# Copyright(c) 2015, Cyan, Inc. All rights reserved.
#
"""

from jsonpointer import resolve_pointer
from bpprov.translators.base import Translator
from bpprov.components.base import RouteData

import os


class JsonPointerTranslator(Translator):
    '''
    Replaces the value with the pointer provided
    No Value found ?? Value is retained.
    '''

    schema = "json-pointer.json"
    schema_base = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema")

    def process(self, route_data):
        output_format = self.get_output_format()
        rdata = route_data.clone()
        data = self.translate(output_format, rdata.data)
        return RouteData(header=None, data=data)

    def get_output_format(self):
        return self.config.get_json(self.params["converter"])

    def translate(self, arg, data):
        return getattr(self, "translate_" + type(arg).__name__)(arg, data)

    def translate_dict(self, output_format, data):
        result = {self.translate(k, data): self.translate(v, data)
                  for k, v in output_format.iteritems() if not str(v).startswith("/") or v != self.translate(v, data)}
        return result

    def translate_str(self, value, data):
        value = str(value)
        if value.startswith("/"):
            return resolve_pointer(data, value, value)
        return value

    def translate_unicode(self, value, data):
        return self.translate_str(value, data)

    def translate_int(self, value, data):
        return value

    def translate_float(self, value, data):
        return value

    def translate_list(self, out_list, data):
        out_format = []
        for value in out_list:
            processed_value = getattr(self, "translate_" + type(value).__name__)(value, data)
            if str(value).startswith("/") and value == processed_value:
                continue
            out_format.append(processed_value)
        return out_format


if __name__ == '__main__':
    pass
