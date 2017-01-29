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
                data['policerConfig']="True"
    return data

# Get the loopback IP from the output
def get_loopback_ip(data):
    if data['data']['configuration']:
        primary = False
        loopback_ips = []
        inet_addresses = data['data']['configuration']['interfaces']['interface']['unit']['family']['inet']
        for address in inet_addresses['address']:
            if 'primary' in address:
                data['loopback_ip'] = address['name'].split("/")[0]
                primary=True
                break
            else:
                loopback_ips.append(address['name'].split("/")[0])
        if not primary:
            sorted_loopback_ips = sorted(loopback_ips, key=lambda ip: long(''.join(["%02X" % long(i) for i in ip.split('.')]), 16))
            data['loopback_ip'] = sorted_loopback_ips[0]
    return data