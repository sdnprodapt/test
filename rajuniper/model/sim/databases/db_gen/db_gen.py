import json
import argparse
import re
from lxml import etree
from collections import OrderedDict

parser = argparse.ArgumentParser(description='')
parser.add_argument('dir', type=str, help='directory to read xml data from')

args = parser.parse_args()


def load_xml(xml_file):
    it = etree.iterparse(xml_file)
    for _, el in it:
        try:
            el.tag = el.tag.split('}', 1)[1]  # strip all namespaces
        except:
            pass
    return it.root


def get_path_value(element, path, default=None):
    v = element.xpath(path)
    if len(v) > 0:
        return v[0]
    return default


configuration = load_xml('{}/get-configuration.xml'.format(args.dir))
interfaces = load_xml('{}/get-interface-information.xml'.format(args.dir))
inventory = load_xml('{}/get-chassis-inventory.xml'.format(args.dir))
software_version = load_xml('{}/get-software-information.xml'.format(args.dir))
fpc_information = load_xml('{}/get-fpc-information.xml'.format(args.dir))

db = OrderedDict([
    ("deviceInfo", []),
    ("packageInfo", []),
    ("interfaces", []),
    ("logicalInterfaces", []),
    ("logicalInterfaceAddressFamilies", []),
    ("chassisModules", []),
    ("fpcInfo", []),

    ("l2circuits", []),
    ("l2circuitInterfaces", []),
    ("firewalls", []),
    ("firewall-filters", []),
    ("firewall-policers", []),
    ("routing-instances", []),
])

deviceInfo = {}
deviceInfo['name'] = inventory.xpath('//chassis/name')[0].text
deviceInfo['serial-number'] = inventory.xpath('//serial-number')[0].text
deviceInfo['description'] = inventory.xpath('//description')[0].text
try:
    deviceInfo['router-id'] = configuration.xpath('//router-id')[0].text
except IndexError:
    # No router-id found
    deviceInfo['router-id'] = "NotSet"
deviceInfo['host-name'] = software_version.xpath('//host-name')[0].text
deviceInfo['product-model'] = software_version.xpath('//product-model')[0].text
deviceInfo['product-name'] = software_version.xpath('//product-name')[0].text
try:
    deviceInfo['junos-version'] = software_version.xpath('//junos-version')[0].text
except:
    # If the junos-version doesn't exist try and read it from the first package information
    deviceInfo['junos-version'] = re.match(r'.*\[(.*)\]$',
                                           software_version.xpath('//package-information/comment/text()')[0]).group(1)

db['deviceInfo'].append(deviceInfo)

package_info = software_version.xpath('//package-information')
for pkg in package_info:
    db['packageInfo'].append({
        'name': pkg.findtext('name'),
        'comment': pkg.findtext('comment')
    })


def get_chassis_module(module, parent_name, path):
    # 'chassis-module'
    # 'chassis-sub-module'
    # 'chassis-sub-sub-module'
    name = module.findtext('name')
    db['chassisModules'].append({
        "name": name,
        "parentName": parent_name,
        "version": module.findtext('version') or '',
        "clei-code": module.findtext('clei-code') or '',
        "part-number": module.findtext('part-number') or '',
        "serial-number": module.findtext('serial-number') or '',
        "description": module.findtext('description') or '',
        "model-number": module.findtext('model-number') or ''
    })

    l = path.split('-')
    subs = l[1:-1]
    subs.append('sub')
    next_path = '-'.join(l[0:1] + subs + l[-1:])
    for el in module.xpath(next_path):
        next_parent_name = ':'.join([parent_name, name]) if parent_name != '' else name
        get_chassis_module(el, next_parent_name, next_path)


chassis_modules = inventory.xpath('//chassis-module')
for cm in chassis_modules:
    get_chassis_module(cm, '', 'chassis-module')

fpc_info = fpc_information.xpath('//fpc')
for fpc in fpc_info:
    fpc_d = {
        'slot': int(fpc.findtext('slot')),
        'state': fpc.findtext('state')
    }
    if fpc_d['state'] != 'Empty':
        fpc_d['temperature'] = int(fpc.findtext('temperature'))
        fpc_d['cpu-total'] = int(fpc.findtext('cpu-total'))
        fpc_d['cpu-interrupt'] = int(fpc.findtext('cpu-interrupt'))
        fpc_d['dram-size'] = int(fpc.findtext('memory-dram-size'))
        fpc_d['heap-utilization'] = int(fpc.findtext('memory-heap-utilization'))
        fpc_d['buffer-utilization'] = int(fpc.findtext('memory-buffer-utilization'))
    db['fpcInfo'].append(fpc_d)

ifaces = interfaces.xpath('//physical-interface')
for iface in ifaces:
    interface_name = iface.findtext('name')
    if_d = {
        'name': interface_name,
        'admin-status': iface.findtext('admin-status').strip() == 'up',
        'oper-status': iface.findtext('oper-status').strip() == 'up',
        'local-index': int(iface.findtext('local-index')),
        'snmp-index': int(iface.findtext('snmp-index')),
        'speed': iface.findtext('speed') or '',
        'interface-flapped': iface.findtext('interface-flapped'),
        'link-level-type': get_path_value(iface, 'link-level-type/text()', default=''),
        'mtu': get_path_value(iface, 'mtu/text()', default=''),
        'hw-address': get_path_value(iface, 'hardware-physical-address/text()', default='')
    }

    device_flags = []
    for flag in iface.xpath('if-device-flags/*'):
        if flag.tag != 'internal-flags':
            device_flags.append(flag.tag)
    if_d['if-device-flags'] = ';'.join(device_flags)

    media_flags = []
    for flag in iface.xpath('if-media-flags/*'):
        if flag.tag != 'internal-flags':
            media_flags.append(flag.tag)
    if_d['if-media-flags'] = ';'.join(media_flags)

    config_flags = []
    for flag in iface.xpath('if-config-flags/*'):
        if flag.tag != 'internal-flags':
            config_flags.append(flag.tag)
    if_d['if-config-flags'] = ';'.join(config_flags)

    for lif in iface.xpath('logical-interface'):
        lif_name = get_path_value(lif, 'name/text()')
        logical_d = {
            'name': lif_name,
            'interfaceName': interface_name,
            'snmp-index': int(lif.xpath('snmp-index/text()')[0]),
            'local-index': int(lif.xpath('local-index/text()')[0]),
            'logical-interface-bandwidth': get_path_value(lif, 'logical-interface-bandwidth/text()', default=''),
            'encapsulation': lif.xpath('encapsulation/text()')[0],
            'filter-information': lif.xpath('filter-information') != []
        }
        config_flags = []
        for flag in lif.xpath('if-config-flags/*'):
            if flag.tag != 'internal-flags':
                config_flags.append(flag.tag)
        logical_d['if-config-flags'] = ';'.join(config_flags)

        for stat in lif.xpath('traffic-statistics/*'):
            logical_d['stat-{}'.format(stat.tag)] = int(stat.text)
        stats = ['stat-input-packets', 'stat-input-bps', 'stat-input-pps',
                 'stat-output-packets', 'stat-output-bps', 'stat-output-pps']
        for stat in stats:
            if stat not in logical_d:
                logical_d[stat] = -1

        for family in lif.xpath('address-family'):
            address_d = {
                'familyName': family.xpath('address-family-name/text()')[0],
                'logicalInterface': lif_name,
                'mtu': get_path_value(family, 'mtu/text()', default=''),
                'ifa-destination': get_path_value(family, 'interface-address/ifa-destination/text()', default=''),
                'ifa-local': get_path_value(family, 'interface-address/ifa-local/text()', default=''),
                'ifa-broadcast': get_path_value(family, 'interface-address/ifa-broadcast/text()', default='')
            }
            ifa_flags = []
            for flag in family.xpath('interface-address/ifa-flags/*'):
                if flag.tag != 'internal-flags':
                    ifa_flags.append(flag.tag)
            address_d['ifa-flags'] = ';'.join(ifa_flags)
            db['logicalInterfaceAddressFamilies'].append(address_d)
        db['logicalInterfaces'].append(logical_d)

    stats = ['stat-input-packets', 'stat-input-bps', 'stat-input-pps',
             'stat-output-packets', 'stat-output-bps', 'stat-output-pps']
    for stat in iface.xpath('traffic-statistics/*'):
        if_d['stat-{}'.format(stat.tag)] = int(stat.text)

    for stat in stats:
        if stat not in if_d:
            if_d[stat] = -1

    db['interfaces'].append(if_d)


l2circuits = configuration.xpath('/rpc-reply/configuration/protocols/l2circuit/neighbor')
for circuit in l2circuits:
    circuit_name = circuit.findtext('name')
    for iface in circuit.xpath('interface'):
        if_d = {
            'circuit-name': circuit_name,
            'if-name': iface.findtext('name'),
            'virtual-circuit-id': iface.findtext('virtual-circuit-id'),
            'encapsulation-type': iface.findtext('encapsulation-type')
        }
        db['l2circuitInterfaces'].append(if_d)
    db['l2circuits'].append({'name': circuit_name})


def strip_ws(obj):
    '''
    recursively strip leading and trailing whitespace from all strings in an object
    '''
    if isinstance(obj, dict):
        for k, v in obj.iteritems():
            obj[k] = strip_ws(v)
        return obj
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            obj[i] = strip_ws(v)
        return obj
    elif isinstance(obj, (str, unicode)):
        return obj.strip()
    else:
        return obj


json.dump(strip_ws(db), open('{}/db.json'.format(args.dir), 'w'), indent=4)
