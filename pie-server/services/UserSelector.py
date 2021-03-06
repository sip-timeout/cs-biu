import time
import sys
import itertools
import random
import numpy
import functools
import operator
from services import FeatureCalculator
from model import FileManager
from services.Clustering import KMeansCluster

calculation_time = 0
thresholds = None
category_scores = None
meaningful_overlaps = None
# bucketed_feature_modifiers = ['continent', 'country', 'cuisine', 'good-for']
# bucketed_feature_modifiers = ['cuisine', 'country','city','good-for']
bucketed_feature_modifiers = ['cuisine','restaurant-features']
feature_types = ['avg','visit','liked']
# feature_types = ['avg','visit','liked']
like_factor = 4
rest_cat_factor = 1
buckets_num = 3
top_coverage_calculation = 200
random_sample_times = 51
selection_size = 5
overlapping_cats_limit = 50
user_to_cats = dict()


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


def set_trival_weight():
    for category in category_scores:
        category_scores[category] = 1


def set_EBS_weights():
    ordered_cats = sorted(category_scores.keys(), key=lambda cat: category_scores[cat])
    for i in range(len(category_scores)):
        category_scores[ordered_cats[i]] = (i + 1) ** 2


def ensure_category_scores():
    global thresholds
    global category_scores

    if thresholds:
        # print 'return thresholds from cache'
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
            # print 'done'

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

    def calculate_meaningful_overlaps():
        global meaningful_overlaps

        def is_cat_in_user(cat, user):
            cat_parts = cat.split('_')
            cat_type = '_'.join(cat_parts[1:3])
            if cat_type in user['rest_features']:
                if cat_parts[0] in user['rest_features'][cat_type]:
                    if get_bucket(user['rest_features'][cat_type][cat_parts[0]], cat_type) == '_'.join(cat_parts[1:4]):
                        return True
            return False

        overlapping_cats = {}

        ordered_cats = sorted(category_scores.keys(), key=lambda cat: category_scores[cat], reverse=True)
        category_combinations = list(itertools.combinations(ordered_cats[:overlapping_cats_limit], 2))
        overlap_to_combination = {'&'.join(list(comb)): comb for comb in category_combinations}
        for username in users:

            user = users[username]
            if 'restaurants' in user and len(user['restaurants']) > 3:
                for combination in category_combinations:
                    if is_cat_in_user(combination[0], user) and is_cat_in_user(combination[1], user):
                        upsert(overlapping_cats, '&'.join(list(combination)))

        threshold_score = category_scores[ordered_cats[200]]
        # print ordered_cats[200]
        # print category_scores[ordered_cats[200]]
        ordered_overlapping = sorted(overlapping_cats.keys(), key=lambda cat: overlapping_cats[cat], reverse=True)

        meaningful_overlaps = []
        # for overlap in ordered_overlapping:
        #     print overlap + ' ' + str(overlapping_cats[overlap])
        for overlap in ordered_overlapping:
            if overlapping_cats[overlap] > threshold_score:
                # print overlap + ' ' + str(overlapping_cats[overlap])
                meaningful_overlaps.append(overlap_to_combination[overlap])

    calculate_thresholds()
    calculate_category_scores()
    # set_trival_weight()
    # set_EBS_weights()
    #
    calculate_meaningful_overlaps()
    print 'Number of categories:' + str(len(category_scores))


def get_overlapping_coverage(selection, ordered_cats, overlap_limit):
    # category_combinations = list(itertools.combinations(ordered_cats[:overlap_limit], 2))
    if not meaningful_overlaps:
        return 0

    covered_combinations = 0
    for combination in meaningful_overlaps:
        for user in selection:
            covered = True
            for category in combination:
                if category not in [cat[0] for cat in user[2]]:
                    covered = False
                    break
            if covered:
                covered_combinations += 1
                break

    return float(covered_combinations) / float(len(meaningful_overlaps))


def get_category_coverage(top_for_coverage, top_covered_indication, selection):
    ordered_total_cats = sorted(category_scores.keys(), key=lambda cat: category_scores[cat], reverse=True)
    selection_cats = set(reduce(lambda x, y: x + y[2], selection, []))
    selection_dict = dict((k[0], 1) for k in selection_cats)
    category_coverage = [[cat, cat in selection_dict, category_scores[cat]] for cat in ordered_total_cats]

    top_covered = [cat for cat in category_coverage if cat[1]][:top_covered_indication]
    top_not_covered = [cat for cat in category_coverage if not cat[1]][:top_covered_indication]

    top_category_coverage = category_coverage[:top_for_coverage]
    coverage_rate = float(len([1 for cat in top_category_coverage if cat[1]])) / top_for_coverage

    overlapping_coverage = get_overlapping_coverage(selection, ordered_total_cats, overlapping_cats_limit)
    return top_category_coverage, coverage_rate, top_covered, top_not_covered, selection_dict, overlapping_coverage


def get_selection_obj(selection, rest_categories):
    selection_users = [{'score': user[1], 'categories': user[2][:10], 'user': user[-1]} for user in selection]
    category_coverage, coverage, top_covered, top_not_covered, all_covered_cats, overlapping_coverage = get_category_coverage(
        top_coverage_calculation, 20, selection)

    formatted_cats = sorted([[rest_cat, rest_cat in all_covered_cats] for rest_cat in rest_categories],
                            key=lambda cat: category_scores[cat[0]], reverse=True)

    selection_score = sum([category_scores[cat] for cat in all_covered_cats])
    covered_cat_num = len(all_covered_cats)
    return {'users': selection_users, 'top_category_coverage': category_coverage,
            'category_coverage_rate': coverage, 'top_covered': top_covered, 'top_not_covered': top_not_covered,
            'rest_categories': formatted_cats, 'selection_score': selection_score, 'cats_num': covered_cat_num,
            'overlapping_coverage': overlapping_coverage}


def calculate_arbitrary_selection_score(random_users, users, cat_score):
    ret_obj = []
    covered = dict()
    for username in random_users:
        user = users[username]
        score, user_cats, all_cats = calculate_user_score(user, covered, cat_score)
        ret_obj.append([username, score, user_cats, user])

        for cat in user_cats:
            covered[cat[0]] = True
    return ret_obj


def calculate_user_score(user, covered_cats, cat_scores):
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
                        score += cat_scores[full_cat_name]
                        user_covered.append((full_cat_name, cat_scores[full_cat_name]))
    for bin_feat in user['bin_features']:
        user_cats[bin_feat] = True
        if bin_feat not in covered_cats:
            score += cat_scores[bin_feat]
            user_covered.append((bin_feat, cat_scores[bin_feat]))

    return score, user_covered, user_cats


def user_in_restaurant(user, rest_id):
    if 'reviews' in user:
        return rest_id in user['reviews']


def get_selection(restaurant_name, selection_criteria):
    global calculation_time

    users = FeatureCalculator.calculate_features()

    ensure_category_scores()

    def get_rest_cuisines():
        rest_cuisines = next((poi['cuisine'] for poi in FileManager.get_pois() if poi['id'] == restaurant_name),
                             None)

        tax = dict(FileManager.get_rest_taxonomy())

        def get_tax(cus):
            if cus in tax:
                return tax[cus]
            else:
                return cus

        return [get_tax(cus) for cus in rest_cuisines]

    def predominate_restaurant_categories():
        predominated_scores = dict(category_scores)
        max_val = max(predominated_scores.iteritems(), key=operator.itemgetter(1))[1]

        rest_cats = []
        for cui in get_rest_cuisines():
            for type in feature_types:
                for buck_num in range(1, buckets_num + 1):
                    rest_cats.append('_'.join([cui, 'cuisine', type, str(buck_num)]))

        for rest_cat in rest_cats:
            if rest_cat in predominated_scores:
                predominated_scores[rest_cat] += int(max_val * rest_cat_factor)

        return predominated_scores

    def get_user_feedback_scores(score_dict):
        feedback_scores = score_dict
        max_val = max(feedback_scores.iteritems(), key=operator.itemgetter(1))[1]

        for like_cat in selection_criteria['like_cats']:
            feedback_scores[like_cat] += int(max_val * like_factor)
        for dislike_cat in selection_criteria['dislike_cats']:
            feedback_scores[dislike_cat] = 0

        return feedback_scores

    if restaurant_name:
        # restaurant_predominated_scores = predominate_restaurant_categories()
        # user_feedback_category_scores = get_user_feedback_scores(restaurant_predominated_scores)
        user_feedback_category_scores = get_user_feedback_scores(dict(category_scores))
    else:
        user_feedback_category_scores = dict(category_scores)

    def remove_rest_users_data(category_scores, rest_users):

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

    def get_random_users(users):

        random_users = random.sample(users, selection_size)
        return calculate_arbitrary_selection_score(random_users, users, user_feedback_category_scores)

    def get_distance_based_selection(users, seed_user):
        start = time.time()
        global user_to_cats


        for user in users:
            if not user in user_to_cats:
                _, _, user_cats = calculate_user_score(users[user], dict(), user_feedback_category_scores)
                user_to_cats[user] = user_cats.keys()

        def get_crowd_similarity(crowd_users):
            def jaccard_similarity(x, y):
                intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
                union_cardinality = len(set.union(*[set(x), set(y)]))
                return intersection_cardinality / float(union_cardinality)

            pairs = itertools.combinations(crowd_users, 2)
            aggregated_similarity = 0
            for pair in pairs:
                aggregated_similarity += jaccard_similarity(user_to_cats[pair[0]], user_to_cats[pair[1]])
            return aggregated_similarity / len(crowd_users)

        selected_users = random.sample([user for user in users.keys() if len(user_to_cats[user]) > 0], 1)

        # selected_users = [[user for user in users.keys() if len(user_to_cats[user]) > 0][0]]
        for i in range(1, selection_size):
            min_score = sys.maxint
            arg_min = []
            for username in users:
                if len(user_to_cats[username]) > 0:
                    sim_score = get_crowd_similarity(selected_users + [username])
                    if sim_score < min_score:
                        min_score = sim_score
                        arg_min = [username]
                    elif sim_score == min_score:
                        arg_min.append(username)

            selected_users.append(max(arg_min, lambda username: len(user_to_cats[username]))[0])

        print 'DISTANCE calculation time:'+str(time.time() - start)
        return selected_users

    def validate_user(user_cats):
        for req_cat in selection_criteria['required_cats']:
            if not req_cat in user_cats:
                return False
        for forb_cat in selection_criteria['forbidden_cats']:
            if forb_cat in user_cats:
                return False
        return True

    if restaurant_name:
        rest_users = {k: v for k, v in users.iteritems() if user_in_restaurant(v, restaurant_name)}
        remove_rest_users_data(user_feedback_category_scores, rest_users)
    else:
        rest_users = users.copy()

    rest_users_copy = rest_users.copy()

    start = time.time()

    selected_users = []
    covered_cats = dict()
    restaurant_cats = set()
    for i in range(0, selection_size):
        max_score = -1
        arg_max = None

        for username in rest_users:
            user = rest_users[username]

            score, user_covered_cats, user_total_cats = calculate_user_score(user, covered_cats,
                                                                             user_feedback_category_scores)

            if selection_criteria is None or validate_user(user_total_cats):
                if score > max_score:
                    max_score = score
                    # arg_max = [username, score, user_covered_cats, user['review_title'], user['review_rating'], user]
                    arg_max = [username, score, user_covered_cats, user]

            if i == 0 and restaurant_name:
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

    # return [{'score': user[1], 'categories': user[2], 'user': user[-1]} for user in selected_users]
    calculation_time = time.time() - start
    # print sum([user[1] for user in selected_users])
    # print ';'.join([user[0] for user in selected_users])
    print 'PODIUM calculation time:' + str(calculation_time)

    # start = time.time()
    # max_score = 0
    # opt_max_arg = None
    # print 'Starting Optimal Calc'
    # for comb in itertools.combinations(rest_users_copy, 5):
    #     selection_score_obj = calculate_arbitrary_selection_score(comb, rest_users_copy,
    #                                                                                    user_feedback_category_scores)
    #
    #     selection_score = sum([user[1] for user in selection_score_obj])
    #     if selection_score > max_score:
    #         max_score = selection_score
    #         opt_max_arg = selection_score_obj
    # print 'Optimal Calc:' + str(time.time() - start)
    # print max_score
    # print ';'.join([user[0] for user in opt_max_arg])
    return get_selection_obj(selected_users, restaurant_cats), get_selection_obj(get_random_users(rest_users_copy),
                                                                                 restaurant_cats), get_selection_obj(
        calculate_arbitrary_selection_score([user['user_id'] for user in get_cluster_selection(rest_users_copy)],
                                            rest_users_copy,
                                            user_feedback_category_scores),
        restaurant_cats), get_selection_obj(
        calculate_arbitrary_selection_score([user['user_id'] for user in
                                             sorted(rest_users_copy.values(), key=lambda user: user['review_count'],
                                                    reverse=True)[:selection_size]], rest_users_copy,
                                            user_feedback_category_scores),
        restaurant_cats), get_selection_obj(
        calculate_arbitrary_selection_score(get_distance_based_selection(rest_users_copy, selected_users[0][0]),
                                            rest_users_copy, user_feedback_category_scores), restaurant_cats)


def get_cluster_selection(users):
    clustering = KMeansCluster()
    start = time.time()
    reps = clustering.get_representatives(users, selection_size)
    print 'Cluster calculation time:' + str(time.time() - start)
    return reps


def get_category_analysis(category_name, restaurant_name, selection_criteria, selection=None):
    users = FeatureCalculator.calculate_features()
    if not selection:
        selection = get_selection(restaurant_name, selection_criteria)
    specification, mod, tp, bucket = category_name.split('_')
    cat_name = '_'.join([mod, tp])

    selections = {
        'pod': {'users': [user['user']['user_id'] for user in selection[0]['users']], 'dist': [0] * buckets_num},
        'random': {'users': [user['user']['user_id'] for user in selection[1]['users']], 'dist': [0] * buckets_num},
        'cluster': {'users': [user['user']['user_id'] for user in selection[2]['users']], 'dist': [0] * buckets_num},
        'top': {'users': [user['user']['user_id'] for user in selection[3]['users']], 'dist': [0] * buckets_num},
        'distance': {'users': [user['user']['user_id'] for user in selection[4]['users']], 'dist': [0] * buckets_num}}

    total_users_dist = [0] * buckets_num
    selection_users_dist = [0] * buckets_num

    def get_normalized_dist(dist_arr):
        arr_sum = sum(dist_arr)
        if arr_sum == 0:
            return [0] * len(dist_arr)
        return [(float(elem) / arr_sum) for elem in dist_arr]

    for user_name, user in users.iteritems():
        user_features = user['rest_features']
        if cat_name in user_features and specification in user_features[cat_name] and len(user['restaurants']) > 3:
            bucket = get_bucket(user_features[cat_name][specification], cat_name)
            buck_num = int(bucket[-1])
            total_users_dist[buck_num - 1] += 1
            for selection_type in selections:
                selection = selections[selection_type]
                if user_name in selection['users']:
                    selection['dist'][buck_num - 1] += 1

    return {'dist_total': get_normalized_dist(total_users_dist),
            'dist_pod': get_normalized_dist(selections['pod']['dist']),
            'dist_cluster': get_normalized_dist(selections['cluster']['dist']),
            'dist_random': get_normalized_dist(selections['random']['dist']),
            'dist_top': get_normalized_dist(selections['top']['dist']),
            'dist_distance': get_normalized_dist(selections['distance']['dist'])}

def calculate_selection_avg_overlap(selection):
    global user_to_cats

    tot_card = 0.0
    combs = 0
    pairs = itertools.combinations(selection, 2)
    for pair in pairs:
        # intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
        tot_card += len(set.intersection(*[set(user_to_cats[pair[0]['user_id']]), set(user_to_cats[pair[1]['user_id']])]))
        combs+=1

    return tot_card / float(combs)

def get_prediction(restaurant_name, selection_criteria):
    def get_topic_coverage(rest_users, selection_users):
        def is_topic_in_array(topic, arr):
            sub_topics = topic.split(' ')
            for user in arr:
                found = True
                # review_text = user['review_title'].lower() + '###' + user['review_content'].lower()
                review_text = user['reviews'][restaurant_name]['content'].lower()
                for sub_topic in sub_topics:
                    if review_text.find(sub_topic) < 0:
                        found = False
                        break
                if found:
                    return True
            return False

        poi_topics = next(poi['topics'].split(';') for poi in FileManager.get_pois() if poi['id'] == restaurant_name)
        topic_coverage = {k: {} for k in poi_topics}
        for topic in poi_topics:
            topic_coverage[topic]['total'] = is_topic_in_array(topic, rest_users)
            topic_coverage[topic]['selection'] = is_topic_in_array(topic, selection_users)

        coverage = [[topic, v['selection']] for topic, v in topic_coverage.iteritems() if v['total']]
        coverage_rate = float(len([1 for topic in coverage if topic[1]])) / len(coverage)
        return coverage, coverage_rate

    def get_weighted_topic_coverage(rest_users, selection_users):
        weights = ['low', 'med', 'high']
        rating_to_weight = {1: 'low', 2: 'low', 3: 'med', 4: 'high', 5: 'high'}

        def is_topic_in_array(topic, rating, arr):
            sub_topics = topic.split(' ')
            for user in arr:
                found = True
                # review_text = user['review_title'].lower() + '###' + user['review_content'].lower()
                review_text = user['reviews'][restaurant_name]['content'].lower()
                for sub_topic in sub_topics:
                    if review_text.find(sub_topic) < 0:
                        found = False
                        break
                if found:
                    if rating_to_weight[user['reviews'][restaurant_name]['rating']] == rating:
                        # print '\n'.join([topic,rating,str(user['reviews'][restaurant_name])])
                        return True
            return False

        poi_topics = next(poi['topics'].split(';') for poi in FileManager.get_pois() if poi['id'] == restaurant_name)
        weighted_topics = list(
            itertools.chain.from_iterable([['_'.join([topic, weight]) for weight in weights] for topic in poi_topics]))
        topic_coverage = {k: {} for k in weighted_topics}
        for topic in poi_topics:
            for weight in weights:
                topic_coverage['_'.join([topic, weight])]['total'] = is_topic_in_array(topic, weight, rest_users)
                topic_coverage['_'.join([topic, weight])]['selection'] = is_topic_in_array(topic, weight,
                                                                                           selection_users)

        coverage = [[topic, v['selection']] for topic, v in topic_coverage.iteritems() if v['total']]
        # print coverage
        coverage_rate = float(len([1 for topic in coverage if topic[1]])) / len(coverage)

        # print selection_users
        if 'usefulness' in selection_users[0]['reviews'][restaurant_name]:
            relevant_reviews_usefulness = [user['reviews'][restaurant_name]['usefulness'] for user in selection_users]
        else:
            relevant_reviews_usefulness = [0]
        # print relevant_reviews_usefulness
        return coverage, coverage_rate, sum(relevant_reviews_usefulness)

    def get_rating_dist(rating_arr):
        # print rating_arr
        dist = [0.0] * 5
        for rat in rating_arr:
            dist[int(rat) - 1] += 1.0 / len(rating_arr)
        return dist

    def get_random_stats(sample_size):
        all_coverages = list()
        total_topic_coverage = list()
        total_coverage_rate = 0.0
        random_var = 0.0
        random_usefulness = 0.0
        for i in range(0, random_sample_times):
            random_users = random.sample(rest_users, sample_size)
            random_var += numpy.var([float(user['reviews'][restaurant_name]['rating']) for user in random_users])
            topic_coverage, coverage_rate, instance_usefulness = get_weighted_topic_coverage(rest_users, random_users)
            random_usefulness += instance_usefulness
            all_coverages.append(topic_coverage)

        for topic in all_coverages[0]:
            vote_count = functools.reduce(lambda x, y: x + int([topic[0], True] in y), all_coverages, 0)
            added_topic = [topic[0], vote_count > random_sample_times / 2]
            total_topic_coverage.append(added_topic)
            total_coverage_rate += float(added_topic[1]) / float(len(all_coverages[0]))

        return total_topic_coverage, total_coverage_rate, random_var / float(
            random_sample_times), random_usefulness / float(random_sample_times)

    def get_marginal_cont():
        marg_cont = []
        prev_top_rate, prev_pod_rate = 0.0, 0.0
        for i in range(0, selection_size):
            stage_margin = {}
            _, pod_rate, _ = get_weighted_topic_coverage(rest_users, selection_users[:i + 1])
            _, top_rate, _ = get_weighted_topic_coverage(rest_users, top_reviewers[:i + 1])

            stage_margin['pod'] = pod_rate - prev_pod_rate
            stage_margin['top'] = top_rate - prev_top_rate

            prev_pod_rate = pod_rate
            prev_top_rate = top_rate

            marg_cont.append(stage_margin)
        return marg_cont

    users = FeatureCalculator.calculate_features()

    rest_users = [user for user in users.values() if user_in_restaurant(user, restaurant_name)]
    selection_obj = get_selection(restaurant_name, selection_criteria)
    selection_users = [user['user'] for user in selection_obj[0]['users']]
    # random.seed(abs(hash(restaurant_name)))
    # random_users = random.sample(rest_users, len(selection_users))
    random_users = [user['user'] for user in selection_obj[1]['users']]
    cluster_users = [user['user'] for user in selection_obj[2]['users']]
    top_reviewers = sorted(rest_users, key=lambda user: user['review_count'], reverse=True)[:selection_size]
    distance_users = [user['user'] for user in selection_obj[4]['users']]

    total_ratings = [float(user['reviews'][restaurant_name]['rating']) for user in rest_users]
    selection_ratings = [float(user['reviews'][restaurant_name]['rating']) for user in selection_users]
    random_ratings = [float(user['reviews'][restaurant_name]['rating']) for user in random_users]
    cluster_ratings = [float(user['reviews'][restaurant_name]['rating']) for user in cluster_users]
    top_ratings = [float(user['reviews'][restaurant_name]['rating']) for user in top_reviewers]
    distance_ratings = [float(user['reviews'][restaurant_name]['rating']) for user in distance_users]

    topic_coverage, coverage_rate, usefulness = get_weighted_topic_coverage(rest_users, selection_users)
    random_topic_coverage, random_coverage_rate, random_variance, random_usefulness = get_random_stats(
        len(selection_users))
    cluster_topic_coverage, cluster_coverage_rate, cluster_usefulness = get_weighted_topic_coverage(rest_users,
                                                                                                    cluster_users)
    top_topic_coverage, top_coverage_rate, top_usefulness = get_weighted_topic_coverage(rest_users, top_reviewers)
    distance_topic_coverage, distance_coverage_rate, distance_usefulness = get_weighted_topic_coverage(rest_users,
                                                                                                       distance_users)

    selection_overlap = calculate_selection_avg_overlap(selection_users)
    random_overlap = calculate_selection_avg_overlap(random_users)
    cluster_overlap = calculate_selection_avg_overlap(cluster_users)
    top_overlap = calculate_selection_avg_overlap(top_reviewers)
    distance_overlap = calculate_selection_avg_overlap(distance_users)

    marginal_cont = get_marginal_cont()
    return {'total_variance': numpy.var(total_ratings),
            'selection_variance': numpy.var(selection_ratings),
            'random_variance': random_variance,
            'cluster_variance': numpy.var(cluster_ratings),
            'top_variance': numpy.var(top_ratings),
            'distance_variance': numpy.var(distance_ratings),
            'topic_coverage': topic_coverage,
            'topic_coverage_rate': coverage_rate,
            'random_topic_coverage': random_topic_coverage,
            'random_topic_coverage_rate': random_coverage_rate,
            'cluster_topic_coverage': cluster_topic_coverage,
            'cluster_topic_coverage_rate': cluster_coverage_rate,
            'top_topic_coverage': top_topic_coverage,
            'top_topic_coverage_rate': top_coverage_rate,
            'distance_topic_coverage': distance_topic_coverage,
            'distance_topic_coverage_rate': distance_coverage_rate,
            'distributions': {
                'dist_total': get_rating_dist(total_ratings),
                'dist_pod': get_rating_dist(selection_ratings),
                'dist_random': get_rating_dist(random_ratings),
                'dist_cluster': get_rating_dist(cluster_ratings),
                'dist_top': get_rating_dist(top_ratings),
                'dist_distance': get_rating_dist(distance_ratings)
            },
            'marg_cont': marginal_cont,
            'selection_reviews': [user['reviews'][restaurant_name] for user in selection_users],
            'top_reviews': [user['reviews'][restaurant_name] for user in top_reviewers],
            'usefulness': usefulness,
            'random_usefulness': random_usefulness,
            'cluster_usefulness': cluster_usefulness,
            'top_usefulness': top_usefulness,
            'distance_usefulness': distance_usefulness,
            'inter': selection_overlap,
            'random_inter': random_overlap,
            'cluster_inter': cluster_overlap,
            'top_inter': top_overlap,
            'distance_inter': distance_overlap
            }
