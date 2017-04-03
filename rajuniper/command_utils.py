# Convert the ENNI flag from boolean to string type for comparision
def convert_enni_flag_bool_string(data):
    data['ENNI'] = "False"
    interfaces = data['interfaces']
    for interface in interfaces:
        if interface['isENNI']:
            data["ENNI"] = "True"
            break
    return data


# Check if policer is configured already
def check_pe_firewall_policer_config(data):
    data['policerConfig'] = "False"
    if data['output']['data']['configuration']:
        if 'policer' in data['output']['data']['configuration']['firewall']:
            if 'name' in data['output']['data']['configuration']['firewall']['policer']:
                data['policerConfig'] = "True"
    return data


# Get the loopback IP from the output
def get_loopback_ip(data):
    if data['data']['configuration']:
        primary = False
        loopback_ips = []
        if 'family' in data['data']['configuration']['interfaces']['interface']['unit']:
            if 'inet' in data['data']['configuration']['interfaces']['interface']['unit']['family']:
                if 'address' in data['data']['configuration']['interfaces']['interface']['unit']['family']['inet']:
                    inet_addresses = \
                        data['data']['configuration']['interfaces']['interface']['unit']['family']['inet']['address']
                    if not isinstance(inet_addresses, (str, list)):
                        addresses = []
                        addresses.append(inet_addresses)
                    else:
                        addresses = inet_addresses
                    for address in addresses:
                        if 'primary' in address and '127.0.0.1' not in address['name']:
                            data['loopback_ip'] = address['name'].split("/")[0]
                            primary = True
                            break
                        elif '127.0.0.1' not in address['name']:
                            loopback_ips.append(address['name'].split("/")[0])
                    if not primary and loopback_ips:
                        loopback_ips = sorted(loopback_ips,
                           key=lambda ip: long(''.join(["%02X" % long(i) for i in ip.split('.')]), 16))
                        data['loopback_ip'] = loopback_ips[0]
    return data


# Determine used VLANs on a given interface
def get_interface_used_vlans(data):
    if data['data']['configuration']:
        used_vlans = []
        if 'unit' in data['data']['configuration']['interfaces']['interface']:
            if not isinstance(data['data']['configuration']['interfaces']['interface']['unit'], (str, list)):
                interface_units = []
                interface_units.append(data['data']['configuration']['interfaces']['interface']['unit'])
            else:
                interface_units = data['data']['configuration']['interfaces']['interface']['unit']
            for unit in interface_units:
                if 'vlan-id' in unit:
                    used_vlans.append(unit['vlan-id'])
                if 'vlan-tags' in unit:
                    used_vlans.append((unit['vlan-tags']['outer']).split('.')[-1])
        data['vlan_ids'] = [int(vlan) for vlan in list(set(used_vlans))]
    return data
