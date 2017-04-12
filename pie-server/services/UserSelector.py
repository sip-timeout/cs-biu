import json
import numpy
from services import FeatureCalculator

def get_users(restaurant_name):
    thresholds = dict()
    category_scores = dict()
    feature_modifiers = ['continent', 'country', 'city', 'cuisine']
    feature_types = ['visit', 'liked', 'avg']
    k = 10
    m = 5
    buckets_num = 4
    collected_vars = []

    users = FeatureCalculator.calculate_features()

    def upsert(map, key, value=1):
        if key in map:
            map[key] += value
        else:
            map[key] = value

    def calculate_thresholds():
        threshold_arrs = dict()
        for mod in feature_modifiers:
            for tp in feature_types:
                threshold_arrs[mod + '_' + tp] = []

        for username in users:
            user = users[username]
            if 'restaurants' in user and len(user['restaurants']) > 3:
                for mod in feature_modifiers:
                    for tp in feature_types:
                        for val in user['rest_features'][mod + '_' + tp].values():
                            threshold_arrs[mod + '_' + tp].append(val)

        for key in threshold_arrs:
            sorted_arr = sorted(threshold_arrs[key])
            buck_size = len(sorted_arr) / buckets_num
            for i in range(1, buckets_num):
                thresholds[key + '_' + str(i)] = sorted_arr[i * buck_size]
            thresholds[key + '_' + str(buckets_num)] = sorted_arr[-1]

    def get_bucket(score, cat):
        for i in range(1, buckets_num + 1):
            buck_name = cat + '_' + str(i)
            if score <= thresholds[buck_name]:
                return buck_name

    def calculate_category_scores():
        for username in users:
            user = users[username]
            if 'restaurants' in user and len(user['restaurants']) > 3:
                for mod in feature_modifiers:
                    for tp in feature_types:
                        cat_name = mod + '_' + tp
                        user_features = user['rest_features'][cat_name]
                        for key in user_features:
                            buck_name = get_bucket(user_features[key], cat_name)
                            upsert(category_scores, '_'.join([key, buck_name]))

    def calculate_user_score(user, covered_categories):
        score = 0
        user_covered = []
        if 'restaurants' in user and len(user['restaurants']) > 3:
            for mod in feature_modifiers:
                for tp in feature_types:
                    cat_name = mod + '_' + tp
                    user_features = user['rest_features'][cat_name]
                    for key in user_features:
                        buck_name = get_bucket(user_features[key], cat_name)
                        full_cat_name = '_'.join([key, buck_name])
                        if full_cat_name not in covered_cats:
                            score += category_scores[full_cat_name]
                            user_covered.append((full_cat_name, category_scores[full_cat_name]))
        return score, user_covered

    calculate_thresholds()
    calculate_category_scores()

    rest_users = {k: v for k, v in users.iteritems() if v['restName']==restaurant_name}

    print 'Total variance:', numpy.var(map(lambda username: float(rest_users[username]['review_rating']), rest_users))

    selected_users = []
    covered_cats = dict()
    for i in range(0, k):
        max_score = -1
        arg_max = None

        for username in rest_users:
            user = rest_users[username]
            score, categories = calculate_user_score(user, covered_cats)
            if score > max_score:
                max_score = score
                arg_max = [username, score, categories, user['review_title'], user['review_rating'],user]

        rest_users.pop(arg_max[0])

        user_categories = arg_max[2]
        for cat in user_categories:
            covered_cats[cat[0]] = True

        user_categories = sorted(user_categories, key=lambda cat: cat[1], reverse=True)[:m]
        arg_max[2] = user_categories
        selected_users.append(arg_max)
        collected_vars.append(numpy.var(map(lambda user: float(user[4]), selected_users)))

    print 'Selection variance:', numpy.var(map(lambda user: float(user[4]), selected_users))

    return [{'score':user[1],'categories':user[2],'user':user[-1]} for user in selected_users]
    # with open(case_name + '.json', 'w') as selected_file:
    #     json.dump(selected_users, selected_file, indent=4, separators=(',', ': '))
    #
    # with open(case_name + '.var', 'w') as var_file:
    #     json.dump(collected_vars, var_file, indent=4, separators=(',', ': '))
