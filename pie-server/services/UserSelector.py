import json
import numpy
from services import FeatureCalculator

thresholds = None
category_scores = None
feature_modifiers = ['continent', 'country', 'city', 'cuisine']
feature_types = ['visit', 'liked', 'avg']
buckets_num = 4


def upsert(map, key, value=1):
    if key in map:
        map[key] += value
    else:
        map[key] = value


def get_bucket(score, cat):
    for i in range(1, buckets_num + 1):
        buck_name = cat + '_' + str(i)
        if score <= thresholds[buck_name]:
            return buck_name


def ensure_category_scores():
    global thresholds
    global category_scores

    if thresholds:
        print 'return thresholds from cache'
        return
    else:
        thresholds = dict()
        category_scores = dict()

    users = FeatureCalculator.calculate_features()

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

    calculate_thresholds()
    calculate_category_scores()


def get_selection(restaurant_name):
    k = 10
    m = 5
    collected_vars = []
    users = FeatureCalculator.calculate_features()

    ensure_category_scores()

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

    def get_category_coverage(top_k):
        ordered_total_cats = sorted(category_scores.keys(), key=lambda cat: category_scores[cat], reverse=True)
        selection_cats = set(reduce(lambda x, y: x + y[2], selected_users, []))
        selection_dict = dict((k[0], 1) for k in selection_cats)
        category_coverage = [[cat, cat in selection_dict] for cat in ordered_total_cats[:top_k]]
        coverage_rate = float(len([1 for cat in category_coverage if cat[1]])) / top_k

        return category_coverage, coverage_rate

    def get_selection_obj():
        selection_users = [{'score': user[1], 'categories': user[2][:m], 'user': user[-1]} for user in selected_users]
        selection_variance = numpy.var(map(lambda user: float(user[4]), selected_users))
        category_coverage, coverage = get_category_coverage(200)

        return {'users': selection_users, 'top_category_coverage': category_coverage,
                'category_coverage_rate': coverage, 'variance': selection_variance,
                'total_variance': total_variance}

    rest_users = {k: v for k, v in users.iteritems() if v['restName'] == restaurant_name}
    total_variance = numpy.var(map(lambda username: float(rest_users[username]['review_rating']), rest_users))
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
                arg_max = [username, score, categories, user['review_title'], user['review_rating'], user]

        rest_users.pop(arg_max[0])

        user_categories = arg_max[2]
        for cat in user_categories:
            covered_cats[cat[0]] = True

        user_categories = sorted(user_categories, key=lambda cat: cat[1], reverse=True)
        arg_max[2] = user_categories
        selected_users.append(arg_max)
        collected_vars.append(numpy.var(map(lambda user: float(user[4]), selected_users)))

    print 'Selection variance:', numpy.var(map(lambda user: float(user[4]), selected_users))

    # return [{'score': user[1], 'categories': user[2], 'user': user[-1]} for user in selected_users]
    return get_selection_obj()


def get_category_analysis(category_name, restaurant_name):
    users = FeatureCalculator.calculate_features()
    selection = get_selection(restaurant_name)
    specification, mod, tp, bucket = category_name.split('_')
    cat_name = '_'.join([mod, tp])

    selection_users = [user['user']['userName'] for user in selection['users']]
    total_users_dist = [0] * buckets_num
    selection_users_dist = [0] * buckets_num

    def get_normalized_dist(dist_arr):
        arr_sum = sum(dist_arr)
        return [(float(elem) / arr_sum)*100 for elem in dist_arr]

    for user_name, user in users.iteritems():
        if 'restaurants' in user and len(user['restaurants']) > 3:
            user_features = user['rest_features']
            if user['restName'] == restaurant_name:
                if cat_name in user_features and specification in user_features[cat_name]:
                    bucket = get_bucket(user_features[cat_name][specification], cat_name)
                    buck_num = int(bucket[-1])
                    total_users_dist[buck_num - 1] += 1
                    if user_name in selection_users:
                        selection_users_dist[buck_num - 1] += 1

    return {'total_dist': get_normalized_dist(total_users_dist),
            'selection_dist': get_normalized_dist(selection_users_dist)}
