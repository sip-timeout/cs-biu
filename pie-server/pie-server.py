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

@app.route('/')
def index():
    return jsonify({'a':5 })


if __name__== '__main__':
    app.run(host="0.0.0.0", port=5000, threaded=True, debug=True)