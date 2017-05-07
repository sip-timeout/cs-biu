from flask import Flask
from flask import jsonify
from services import UserSelector
from model import  FileManager
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

@app.route('/rests')
def get_rests():
    return jsonify(FileManager.get_pois()[:5])

@app.route('/selection/<rest_name>')
def get_restaurant_users(rest_name):
    return jsonify(UserSelector.get_selection(rest_name))

@app.route('/selection/<rest_name>/category_analysis/<category_name>')
def get_category_analysis(rest_name,category_name):
    return jsonify(UserSelector.get_category_analysis(category_name,rest_name))

@app.route('/selection/<rest_name>/prediction')
def get_prediction(rest_name):
    return jsonify(UserSelector.get_prediction(rest_name))


if __name__== '__main__':
    app.run(host="0.0.0.0", port=5000, threaded=True, debug=True)