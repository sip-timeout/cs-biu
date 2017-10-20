import json
import random
import numpy
import functools
import operator
from services import FeatureCalculator
from model import FileManager

thresholds = None
category_scores = None
bucketed_feature_modifiers = ['continent', 'country', 'cuisine', 'good-for']
feature_types = ['visit', 'avg']
like_factor = 1.2
buckets_num = 3
top_coverage_calculation = 200
random_sample_times = 11


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
        for mod in bucketed_feature_modifiers:
            for tp in feature_types:
                threshold_arrs[mod + '_' + tp] = []

        for username in users:
            user = users[username]
            if 'restaurants' in user and len(user['restaurants']) > 3:
                for mod in bucketed_feature_modifiers:
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
                for mod in bucketed_feature_modifiers:
                    for tp in feature_types:
                        cat_name = mod + '_' + tp
                        user_features = user['rest_features'][cat_name]
                        for key in user_features:
                            buck_name = get_bucket(user_features[key], cat_name)
                            upsert(category_scores, '_'.join([key, buck_name]))
            for bin_feat in user['bin_features']:
                upsert(category_scores, bin_feat)

    calculate_thresholds()
    calculate_category_scores()


def get_selection(restaurant_name, selection_criteria):
    k = 10
    m = 5
    collected_vars = []
    users = FeatureCalculator.calculate_features()

    ensure_category_scores()

    def get_user_feedback_scores():
        feedback_scores = dict(category_scores)
        max_val = max(feedback_scores.iteritems(), key=operator.itemgetter(1))[1]

        for like_cat in selection_criteria['like_cats']:
            feedback_scores[like_cat] += int(max_val * like_factor)
        for dislike_cat in selection_criteria['dislike_cats']:
            feedback_scores[dislike_cat] = 0

        return feedback_scores

    user_feedback_category_scores = get_user_feedback_scores()

    def remove_rest_users_data(category_scores, rest_users):

        def get_rest_cuisines():
            rest_cuisines = next((poi['cuisines'] for poi in FileManager.get_pois() if poi['name'] == restaurant_name),
                                 None)

            tax = dict(FileManager.get_rest_taxonomy())

            def get_tax(cus):
                if cus in tax:
                    return tax[cus]
                else:
                    return cus

            return [get_tax(cus) for cus in rest_cuisines]

        rest_cuisines = get_rest_cuisines()

        for user_name in rest_users:
            user = rest_users[user_name]
            if 'restaurants' in user and len(user['restaurants']) > 3:
                user_features = user['rest_features']
                for cus in rest_cuisines:
                    for feat_type in feature_types:
                        cat_name = '_'.join(['cuisine', feat_type])
                        if cus in user_features[cat_name]:
                            buck_name = get_bucket(user_features[cat_name][cus], cat_name)
                            full_cat = '_'.join([cus, buck_name])
                            category_scores[full_cat] -= 1

    def calculate_user_score(user):
        score = 0
        user_covered = []
        user_cats = dict()
        if 'restaurants' in user and len(user['restaurants']) > 3:
            for mod in bucketed_feature_modifiers:
                for tp in feature_types:
                    cat_name = mod + '_' + tp
                    user_features = user['rest_features'][cat_name]
                    for key in user_features:
                        buck_name = get_bucket(user_features[key], cat_name)
                        full_cat_name = '_'.join([key, buck_name])
                        user_cats[full_cat_name] = True
                        if full_cat_name not in covered_cats:
                            score += user_feedback_category_scores[full_cat_name]
                            user_covered.append((full_cat_name, user_feedback_category_scores[full_cat_name]))
        for bin_feat in user['bin_features']:
            user_cats[bin_feat] = True
            if bin_feat not in covered_cats:
                score += user_feedback_category_scores[bin_feat]
                user_covered.append((bin_feat, user_feedback_category_scores[bin_feat]))

        return score, user_covered, user_cats

    def get_category_coverage(top_for_coverage, top_covered_indication):
        ordered_total_cats = sorted(category_scores.keys(), key=lambda cat: category_scores[cat], reverse=True)
        selection_cats = set(reduce(lambda x, y: x + y[2], selected_users, []))
        selection_dict = dict((k[0], 1) for k in selection_cats)
        category_coverage = [[cat, cat in selection_dict] for cat in ordered_total_cats]

        top_covered = [cat for cat in category_coverage if cat[1]][:top_covered_indication]
        top_not_covered = [cat for cat in category_coverage if not cat[1]][:top_covered_indication]

        top_category_coverage = category_coverage[:top_for_coverage]
        coverage_rate = float(len([1 for cat in top_category_coverage if cat[1]])) / top_for_coverage

        return top_category_coverage, coverage_rate, top_covered, top_not_covered, selection_dict

    def get_selection_obj(rest_categories):
        selection_users = [{'score': user[1], 'categories': user[2][:m], 'user': user[-1]} for user in selected_users]
        selection_variance = numpy.var(map(lambda user: float(user[4]), selected_users))
        category_coverage, coverage, top_covered, top_not_covered, all_covered_cats = get_category_coverage(
            top_coverage_calculation, 20)

        formatted_cats = sorted([[rest_cat, rest_cat in all_covered_cats] for rest_cat in rest_categories],
                                key=lambda cat: category_scores[cat[0]], reverse=True)

        return {'users': selection_users, 'top_category_coverage': category_coverage,
                'category_coverage_rate': coverage, 'variance': selection_variance,
                'total_variance': total_variance, 'top_covered': top_covered, 'top_not_covered': top_not_covered,
                'rest_categories': formatted_cats}

    def validate_user(user_cats):
        for req_cat in selection_criteria['required_cats']:
            if not req_cat in user_cats:
                return False
        for forb_cat in selection_criteria['forbidden_cats']:
            if forb_cat in user_cats:
                return False
        return True

    rest_users = {k: v for k, v in users.iteritems() if v['restName'] == restaurant_name}

    remove_rest_users_data(user_feedback_category_scores, rest_users)

    total_variance = numpy.var(map(lambda username: float(rest_users[username]['review_rating']), rest_users))
    selected_users = []
    covered_cats = dict()
    restaurant_cats = set()
    for i in range(0, k):
        max_score = -1
        arg_max = None

        for username in rest_users:
            user = rest_users[username]

            score, user_covered_cats, user_total_cats = calculate_user_score(user)

            if validate_user(user_total_cats):
                if score > max_score:
                    max_score = score
                    arg_max = [username, score, user_covered_cats, user['review_title'], user['review_rating'], user]

            if i == 0:
                restaurant_cats = restaurant_cats.union(user_total_cats)

        if not arg_max:
            break

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
    return get_selection_obj(restaurant_cats)


def get_category_analysis(category_name, restaurant_name, selection_criteria):
    users = FeatureCalculator.calculate_features()
    selection = get_selection(restaurant_name, selection_criteria)
    specification, mod, tp, bucket = category_name.split('_')
    cat_name = '_'.join([mod, tp])

    selection_users = [user['user']['userName'] for user in selection['users']]
    total_users_dist = [0] * buckets_num
    selection_users_dist = [0] * buckets_num

    def get_normalized_dist(dist_arr):
        arr_sum = sum(dist_arr)
        return [(float(elem) / arr_sum) * 100 for elem in dist_arr]

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


def get_prediction(restaurant_name, selection_criteria):
    def get_topic_coverage(rest_users, selection_users):
        def is_topic_in_array(topic, arr):
            sub_topics = topic.split(' ')
            for user in arr:
                found = True
                review_text = user['review_title'].lower() + '###' + user['review_content'].lower()
                for sub_topic in sub_topics:
                    if review_text.find(sub_topic) < 0:
                        found = False
                        break
                if found:
                    return True
            return False

        poi_topics = next(poi['topics'] for poi in FileManager.get_pois() if poi['name'] == restaurant_name)
        topic_coverage = {k: {} for k in poi_topics}
        for topic in poi_topics:
            topic_coverage[topic]['total'] = is_topic_in_array(topic, rest_users)
            topic_coverage[topic]['selection'] = is_topic_in_array(topic, selection_users)

        coverage = [[topic, v['selection']] for topic, v in topic_coverage.iteritems() if v['total']]
        coverage_rate = float(len([1 for topic in coverage if topic[1]])) / len(coverage)
        return coverage, coverage_rate

    def get_rating_dist(rating_arr):
        dist = [0.0] * 10
        for rat in rating_arr:
            dist[int(rat * 2) - 1] += 1.0 / len(rating_arr)
        return dist

    def get_random_coverage(sample_size):
        all_coverages = list()
        total_topic_coverage = list()
        total_coverage_rate = 0.0
        for i in range(0, random_sample_times):
            random_users = random.sample(rest_users, sample_size)
            random_ratings = [float(user['review_rating']) for user in random_users]
            topic_coverage, coverage_rate = get_topic_coverage(rest_users, random_users)
            all_coverages.append(topic_coverage)


        for topic in all_coverages[0]:
            vote_count = functools.reduce(lambda x, y: x + int([topic[0],True] in y), all_coverages, 0)
            added_topic = [topic[0],vote_count > random_sample_times / 2]
            total_topic_coverage.append(added_topic)
            total_coverage_rate += float(added_topic[1]) / float(len(all_coverages[0]))

        return total_topic_coverage, total_coverage_rate

    users = FeatureCalculator.calculate_features()

    rest_users = [user for user in users.values() if user['restName'] == restaurant_name]
    selection_users = [user['user'] for user in get_selection(restaurant_name, selection_criteria)['users']]
    random_users = random.sample(rest_users, len(selection_users))
    total_ratings = [float(user['review_rating']) for user in rest_users]
    selection_ratings = [float(user['review_rating']) for user in selection_users]
    random_ratings = [float(user['review_rating']) for user in random_users]

    topic_coverage, coverage_rate = get_topic_coverage(rest_users, selection_users)
    random_topic_coverage, random_coverage_rate = get_random_coverage(len(selection_users))
    return {'total_variance': numpy.var(total_ratings),
            'selection_variance': numpy.var(selection_ratings),
            'random_variance': numpy.var(random_ratings),
            'topic_coverage': topic_coverage,
            'topic_coverage_rate': coverage_rate,
            'random_topic_coverage': random_topic_coverage,
            'random_topic_coverage_rate': random_coverage_rate,
            'total_dist': get_rating_dist(total_ratings),
            'selection_dist': get_rating_dist(selection_ratings),
            'random_dist': get_rating_dist(random_ratings)
            }
