import json
import operator
from model import FileManager

cached_users = None

def calculate_features():
    global cached_users

    if cached_users:
        print 'return users from cache'
        return cached_users

    users = FileManager.get_users()
    rests = FileManager.get_rests()
    cuisine_types = dict(FileManager.get_rest_taxonomy())

    unclassified_cuisines = dict()


    def upsert(map, key, value=1):
        if key in map:
            map[key] += value
        else:
            map[key] = value


    def calculate_rest_features(user):
        if 'restaurants' in user:

            location_modifiers = ['continent','country','city']
            rest_features = dict()
            rest_features['cuisine_visit'] = dict()
            rest_features['cuisine_liked'] = dict()
            rest_features['cuisine_avg'] = dict()

            for mod in location_modifiers:
                rest_features[mod+'_visit'] = dict()
                rest_features[mod+'_liked'] = dict()
                rest_features[mod + '_avg'] = dict()

            total_restaurants = len(user['restaurants'])
            total_rating = reduce(lambda x,y: x+y,map(lambda rest: int(rest['rating']),user['restaurants'].values()))
            total_avg = float(total_rating)/ total_restaurants

            for rest in user['restaurants']:
                if 'cuisine' in rests[rest]:
                    for cuisine in rests[rest]['cuisine'].split(','):
                        if cuisine in cuisine_types:
                            cuisine = cuisine_types[cuisine]
                        else:
                            upsert(unclassified_cuisines, cuisine)

                        upsert(rest_features['cuisine_visit'],cuisine, float(1) / total_restaurants )
                        upsert(rest_features['cuisine_liked'], cuisine,float(user['restaurants'][rest]['rating']) / total_rating)
                        upsert(rest_features['cuisine_avg'], cuisine, float(user['restaurants'][rest]['rating']) / total_avg)

                for mod in location_modifiers:
                    if mod in rests[rest]:
                        upsert(rest_features[mod+'_visit'], rests[rest][mod], float(1) / total_restaurants)
                        upsert(rest_features[mod+'_liked'], rests[rest][mod], float(user['restaurants'][rest]['rating']) / total_rating)
                        upsert(rest_features[mod+'_avg'], rests[rest][mod], float(user['restaurants'][rest]['rating']) / total_avg)

            for key in rest_features['cuisine_avg']:
                rest_features['cuisine_avg'][key] /= (rest_features['cuisine_visit'][key] * total_restaurants)

            for mod in location_modifiers:
                for key in rest_features[mod+'_avg']:
                    rest_features[mod+'_avg'][key] /= (rest_features[mod+'_visit'][key] * total_restaurants)

            user['rest_features'] = rest_features



    for username in users:
        user = users[username]
        calculate_rest_features(user)
    #
    # with open('usersFeatures.json','w') as feat_file:
    #     json.dump(users,feat_file)


    # print json.dumps(sorted(unclassified_cuisines.items(),key=operator.itemgetter(1),reverse=True))
    cached_users = users
    return users