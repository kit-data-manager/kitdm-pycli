
def add_query_parameters(resource_path, query_params):
    result = resource_path

    first_param = True
    if query_params and len(query_params) > 0:
        for param in query_params:
            if param['value'] != 'None' and first_param:
                result += "?" + param['name'] + "=" + param['value']
                first_param = False
            elif param['value'] != 'None' and not first_param:
                result += "&" + param['name'] + "=" + param['value']

    return result


def get_query_param_entry(name, value):
    return {'name': name, 'value': value}
