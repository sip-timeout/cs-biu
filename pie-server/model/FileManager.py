import json

def get_pois():
    return _file_to_dict('pois.json')


def get_rests():
    return _file_to_dict('rests.json')


def get_users():
    return _file_to_dict('users.json')


def get_rest_taxonomy():
    return _file_to_dict('restTax.json')


def _file_to_dict(filename):
    with open('model/'+filename) as data_file:
        data_file = json.load(data_file)
    return data_file