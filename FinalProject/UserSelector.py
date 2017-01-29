import json
import numpy
import itertools
import  random

thresholds = dict()
category_scores = dict()
feature_modifiers = ['continent', 'country', 'city', 'cuisine']
feature_types = ['visit', 'liked', 'avg']

random_users_num = 30
k = 5
m = 5

#case_name = raw_input('insert scenario name:')
case_name = 'bla'
collected_vars = []



with open('usersFeatures.json') as users_file:
    users = json.load(users_file)

user_list = random.sample(users.values(),random_users_num)

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

    for user in user_list:
        if 'restaurants' in user and len(user['restaurants']) > 3:
            for mod in feature_modifiers:
                for tp in feature_types:
                    for val in user['rest_features'][mod + '_' + tp].values():
                        threshold_arrs[mod + '_' + tp].append(val)

    for key in threshold_arrs:
        thresholds[key + '_high'] = numpy.percentile(threshold_arrs[key], 65)
        thresholds[key + '_low'] = numpy.percentile(threshold_arrs[key], 35)


def calculate_category_scores():
    for user in user_list:
        if 'restaurants' in user and len(user['restaurants']) > 3:
            for mod in feature_modifiers:
                for tp in feature_types:
                    user_features = user['rest_features'][mod + '_' + tp]
                    for key in user_features:
                        if user_features[key] >= thresholds['_'.join([mod, tp, 'high'])]:
                            upsert(category_scores, '_'.join([key, mod, tp, 'high']))
                        if user_features[key] <= thresholds['_'.join([mod, tp, 'low'])]:
                            upsert(category_scores, '_'.join([key, mod, tp, 'low']))


def calculate_user_score(user, covered_categories):
    score = 0
    user_covered = []
    if 'restaurants' in user and len(user['restaurants']) > 3:
        for mod in feature_modifiers:
            for tp in feature_types:
                user_features = user['rest_features'][mod + '_' + tp]
                for key in user_features:
                    high_cat = '_'.join([mod, tp, 'high'])
                    low_cat = '_'.join([mod, tp, 'low'])
                    if user_features[key] >= thresholds[high_cat]:
                        full_cat_name = '_'.join([key, high_cat])
                        if full_cat_name not in covered_categories:
                            score += category_scores[full_cat_name]
                            user_covered.append((full_cat_name, category_scores[full_cat_name]))
                    if user_features[key] <= thresholds[low_cat]:
                        full_cat_name = '_'.join([key, low_cat])
                        if full_cat_name not in covered_categories:
                            score += category_scores[full_cat_name]
                            user_covered.append((full_cat_name, category_scores[full_cat_name]))
    return score, user_covered


calculate_thresholds()
calculate_category_scores()

print 'Total variance:', numpy.var(map(lambda user: float(user['review_rating']), user_list))

selected_users = []
covered_cats = dict()
for i in range(0, k):
    max_score = -1
    arg_max = None

    for user in user_list:
        score, categories = calculate_user_score(user, covered_cats)
        if score > max_score:
            max_score = score
            arg_max = [user['userName'], score, categories, user['review_title'], user['review_rating']]

    users.pop(arg_max[0])

    user_categories = arg_max[2]
    for cat in user_categories:
        covered_cats[cat[0]] = True

    user_categories = sorted(user_categories,key=lambda cat: cat[1],reverse=True)[:m]
    arg_max[2] = user_categories
    selected_users.append(arg_max)
    collected_vars.append(numpy.var(map(lambda user: float(user[4]), selected_users)))




print 'Selection variance:', numpy.var(map(lambda user: float(user[4]), selected_users))

generator = itertools.combinations(user_list,k)

i = 0
max_comb_score = 0
max_comb = None
for comb in generator:
    i+=1
    if i % 10000 == 0:
        print i
    covered_cats = dict()
    comb_score = 0
    for user in comb:
        score, categories = calculate_user_score(user, covered_cats)
        for cat in categories:
            covered_cats[cat[0]] = True
        comb_score += score
    if comb_score > max_comb_score:
        max_comb_score = comb_score
        max_comb = comb




print 'optimal selection variance:', numpy.var(map(lambda user: float(user['review_rating']), max_comb))

with open(case_name+'.json', 'w') as selected_file:
    json.dump(selected_users, selected_file, indent=4, separators=(',', ': '))

with open(case_name+'.var', 'w') as var_file:
    json.dump(collected_vars, var_file, indent=4, separators=(',', ': '))

