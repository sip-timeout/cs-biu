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

