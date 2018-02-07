from flask import Flask, request
from flask import jsonify
from services import UserSelector
from model import FileManager
from flask_cors import CORS, cross_origin
import json
import os

app = Flask(__name__)
CORS(app)


@app.route('/rests')
def get_rests():
    return jsonify(FileManager.get_pois()[:50])


@app.route('/selection/<rest_name>', methods=['POST'])
def get_restaurant_users(rest_name):
    data = request.json
    return jsonify(UserSelector.get_selection(rest_name, data))


@app.route('/selection/<rest_name>/category_analysis/<category_name>', methods=['POST'])
def get_category_analysis(rest_name, category_name):
    data = request.json
    return jsonify(UserSelector.get_category_analysis(category_name, rest_name, data))


@app.route('/selection/<rest_name>/prediction', methods=['POST'])
def get_prediction(rest_name):
    data = request.json
    return jsonify(UserSelector.get_prediction(rest_name, data))
    # return jsonify({})


def compare_results(base, other, bet_key, beq_key, summary):
    if beq_key not in summary:
        summary[bet_key] = 0
    if beq_key not in summary:
        summary[beq_key] = 0

    comp = base - other
    if comp >= 0:
        summary[beq_key] += 1
        if comp - 0.0001 > 0:
            summary[bet_key] += 1


def get_marginal_summary(results):
    marg_sum = [{'pod': 0.0, 'top': 0.0} for marg in results[results.keys()[0]]['marg_cont']]
    for _, res in results.iteritems():
        for index, marginal_cont in enumerate(res['marg_cont']):
            for algo in marginal_cont:
                marg_sum[index][algo] += marginal_cont[algo] / len(results)
    return marg_sum


def get_averages(results):
    algos = ['pod','top','random','cluster']
    measures = ['var', 'top']
    avgs = {mes: {algo: 0.0 for algo in algos} for mes in measures}
    for _, res in results.iteritems():
        for algo in algos:
            for mes in measures:
                avgs[mes][algo] += res['_'.join([mes, algo])] / len(results)

    return avgs


@app.route('/test_results')
def get_test():
    results = {}
    summary = {'all': 0}
    if os.path.isfile('test_results'):
        results = json.load(file('test_results'))
    else:
        for poi in FileManager.get_pois():
            if ';' in poi['topics']:
                try:
                    prediction = UserSelector.get_prediction(poi['id'],
                                                             {'forbidden_cats': [], 'dislike_cats': [],
                                                              'required_cats': [],
                                                              'like_cats': []})

                except Exception as ex:
                    print 'cant predict ' + poi['name'] + ' ex:' + str(ex)
                    continue

                summary['all'] += 1
                results[poi['name']] = {'top_pod': prediction['topic_coverage_rate'],
                                        'top_random': prediction['random_topic_coverage_rate'],
                                        'top_cluster': prediction['cluster_topic_coverage_rate'],
                                        'top_top': prediction['top_topic_coverage_rate'],
                                        'var_pod': prediction['selection_variance'],
                                        'var_tot': prediction['total_variance'],
                                        'var_cluster': prediction['cluster_variance'],
                                        'var_random': prediction['random_variance'],
                                        'var_top': prediction['top_variance'],
                                        'marg_cont': prediction['marg_cont'],
                                        'top_reviews':prediction['top_reviews'],
                                        'selection_reviews':prediction['selection_reviews']}
                compare_results(prediction['topic_coverage_rate'], prediction['random_topic_coverage_rate'],
                                'rand_top_bet',
                                'rand_top_beq', summary)
                compare_results(prediction['topic_coverage_rate'], prediction['cluster_topic_coverage_rate'],
                                'clus_top_bet',
                                'clus_top_beq', summary)
                compare_results(prediction['topic_coverage_rate'], prediction['top_topic_coverage_rate'],
                                'top_top_bet',
                                'top_top_beq', summary)
                compare_results(prediction['selection_variance'], prediction['cluster_variance'], 'clus_var_bet',
                                'clus_var_beq', summary)
                compare_results(prediction['selection_variance'], prediction['random_variance'], 'rand_var_bet',
                                'rand_var_beq', summary)
                compare_results(prediction['selection_variance'], prediction['total_variance'], 'tot_var_bet',
                                'tot_var_beq', summary)
                compare_results(prediction['selection_variance'], prediction['top_variance'], 'top_var_bet',
                                'top_var_beq', summary)

                print summary

        results['summary'] = summary

    summary = results.pop('summary')
    summary['marginal'] = get_marginal_summary(results)
    summary['avgs'] = get_averages(results)
    results['summary'] = summary
    return jsonify(results)


@app.route('/experiment/quality')
def perform_quality_test():
    return jsonify(UserSelector.get_selection('4JNXUYY8wbaaDmk3BPzlWw',
                                              {'forbidden_cats': [], 'dislike_cats': [], 'required_cats': [],
                                               'like_cats': []}))
    # return jsonify(UserSelector.get_cluster_selection())


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, threaded=True, debug=True)
