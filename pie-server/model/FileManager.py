import json

user_limit = 60000

def get_pois():
    return _file_to_dict('pois.json')


def get_rests():
    return _file_to_dict('rests.json')


def get_users():
    users =  _file_to_dict('users.json')
    sub_dict = {}
    i =0;
    for k in users:
        sub_dict[k] = users[k]
        if i > user_limit:
            break
        i+=1
    return sub_dict



def get_rest_taxonomy():
    return _file_to_dict('restTax.json')


def _file_to_dict(filename):
    with open('model/'+filename) as data_file:
        data_file = json.load(data_file)
    return data_file