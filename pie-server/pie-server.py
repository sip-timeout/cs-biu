from flask import Flask, request
from flask import jsonify
from services import UserSelector
from model import FileManager
from flask_cors import CORS, cross_origin

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


@app.route('/test_results')
def get_test():
    results = {}
    better = 0
    beteq = 0
    for poi in FileManager.get_pois()[:50]:
        # try:
        prediction = UserSelector.get_prediction(poi['id'],
                                                 {'forbidden_cats': [], 'dislike_cats': [], 'required_cats': [],
                                                  'like_cats': []})

        # except Exception as ex:
        #     print 'cant predict ' + poi['name'] + ' ex:' + str(ex)

        results[poi['name']] = {'our': prediction['topic_coverage_rate'],
                                'random': prediction['random_topic_coverage_rate'],
                                ' cluster': prediction['cluster_topic_coverage_rate']}
        comp = prediction['topic_coverage_rate'] - prediction['random_topic_coverage_rate']
        if comp >= 0:
            beteq += 1
            if comp - 0.0001 > 0:
                better += 1

    results['better'] = better
    results['better_equal'] = beteq
    return jsonify(results)


@app.route('/experiment/quality')
def perform_quality_test():
    return jsonify(UserSelector.get_selection('4JNXUYY8wbaaDmk3BPzlWw',
                                              {'forbidden_cats': [], 'dislike_cats': [], 'required_cats': [],
                                               'like_cats': []}))
    # return jsonify(UserSelector.get_cluster_selection())


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, threaded=True, debug=True)
