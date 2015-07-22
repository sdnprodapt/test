
def firefly_errors(data, **kwargs):
    """ For any of the fields `fields` dict in kwargs that contain any of the values in the `errors`
        list, put them under the `error_key` dict

        Example:
            fields = {"commit": "commit-results"}
            errors = ["rpc-error"]
            error_key = "rpc-error"
    """
    ekey = kwargs['error_key']
    for to_key, from_key in kwargs.get('fields', {}).iteritems():
        for error in kwargs.get('errors', []):
            if error in data.get(from_key, {}):
                if ekey not in data:
                    data[ekey] = {}
                data[ekey][to_key] = data.pop(from_key)
                # Already found one error in this one, no need to keep looking
                break
    return data
