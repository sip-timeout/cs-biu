import pickle

class Utils:
    def __init__(self):
        pass

    @staticmethod
    def add_or_increase_key(dic,key,value=1):
        if key not in dic:
            dic[key] = 0
        dic[key] += value

    @staticmethod
    def get_or_create(dic,key,default):
        if key not in dic:
            dic[key] = default
        return dic[key]

def save_obj(obj, name):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)