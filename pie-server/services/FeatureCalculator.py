import time
from model import FileManager

cached_users = None
calculation_time = 0


def calculate_features():
    global cached_users
    global calculation_time
    start = time.time()
    if cached_users:
        # print 'return users from cache'
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

    def calculate_binary_features(user):
        feat_types = ['location', 'age']
        bin_features = dict()
        for bin_feat in feat_types:
            if bin_feat in user:
                bin_features['_'.join([bin_feat, user[bin_feat]])] = 1
        user['bin_features'] = bin_features

    def calculate_rest_features(user):

        # list_modifiers = ['cuisine', 'restaurant-features']
        list_modifiers = ['cuisine']
        location_modifiers = ['country', 'city']
        # location_modifiers = []
        mod_types = ['avg','visit','liked']

        if 'restaurants' in user:
            rest_features = dict()

            for mod in location_modifiers + list_modifiers:
                rest_features[mod + '_visit'] = dict()
                rest_features[mod + '_liked'] = dict()
                rest_features[mod + '_avg'] = dict()

            total_restaurants = len(user['restaurants'])
            total_rating = reduce(lambda x, y: x + y,
                                  map(lambda rest: float(rest['rating']), user['restaurants'].values()))
            total_avg = float(total_rating) / total_restaurants

            for rest in user['restaurants']:
                for mod in list_modifiers:
                    if mod in rests[rest]:
                        for list_val in [val.strip() for val in rests[rest][mod].split(',')]:
                            if mod == 'cuisine':
                                if list_val in cuisine_types:
                                    list_val = cuisine_types[list_val]
                                else:
                                    upsert(unclassified_cuisines, list_val)

                            upsert(rest_features[mod + '_visit'], list_val, float(1) / total_restaurants)
                            upsert(rest_features[mod + '_liked'], list_val,
                                   float(user['restaurants'][rest]['rating']) / total_rating)
                            upsert(rest_features[mod + '_avg'], list_val,
                                   float(user['restaurants'][rest]['rating']) / total_avg)

                for mod in location_modifiers:
                    if mod in rests[rest]:
                        upsert(rest_features[mod + '_visit'], rests[rest][mod], float(1) / total_restaurants)
                        upsert(rest_features[mod + '_liked'], rests[rest][mod],
                               float(user['restaurants'][rest]['rating']) / total_rating)
                        upsert(rest_features[mod + '_avg'], rests[rest][mod],
                               float(user['restaurants'][rest]['rating']) / total_avg)

            # for key in rest_features['cuisine_avg']:
            #     rest_features['cuisine_avg'][key] /= (rest_features['cuisine_visit'][key] * total_restaurants)

            for mod in location_modifiers + list_modifiers:
                for key in rest_features[mod + '_avg']:
                    rest_features[mod + '_avg'][key] /= (rest_features[mod + '_visit'][key] * total_restaurants)

            filtered_features = {}
            for mod in location_modifiers + list_modifiers:
                for type in mod_types:
                    filtered_features['_'.join([mod,type])] = rest_features['_'.join([mod,type])]


            user['rest_features'] = filtered_features

    for username in users:
        user = users[username]
        calculate_rest_features(user)
        calculate_binary_features(user)
    #
    # with open('usersFeatures.json','w') as feat_file:
    #     json.dump(users,feat_file)


    # print json.dumps(sorted(unclassified_cuisines.items(),key=operator.itemgetter(1),reverse=True))
    # print unclassified_cuisines
    cached_users = users
    calculation_time = time.time() - start
    print 'Number of users:' + str(len(users))

    features_number_arr = [
        (sum([len(mod_features) for mod_features in users[username]['rest_features'].values()]) + len(users[username]['bin_features'].keys()))
        for username in users]
    print 'Average number of features:' + str(float(sum(features_number_arr)) / float(len(features_number_arr)))
    return users
