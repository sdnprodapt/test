# Convert the ENNI flag from boolean to string type for comparision
def convert_enni_flag_bool_string(data):
    data['ENNI'] = "False"
    interfaces = data['interfaces']
    for interface in interfaces:
        if interface['isENNI']:
            data["ENNI"] = "True"
            break
    return data