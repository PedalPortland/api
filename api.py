"""
PedalAPI

The following is the RESTFULL API for use by PedalPDX
"""

from flask import Flask, jsonify, make_response, request
from random import randint
from os import listdir
from json import dump, load
from markdown import markdown
import Secrets

# The locations from which we will be handling flat files of JSON
# data containing the ride logs
RIDELOCATIONS = "./rides/"

# Current Version
APIVERSION = '0.3'

# The hostname of the server the API is hosted on
APIHOSTNAME = Secrets.API_HOSTNAME

# URLSTRING identifies the base for the API's URL
URLSTRING = 'http://' + APIHOSTNAME + ':' + str(Secrets.API_PORT)

# Pass the name of the app to flask
app = Flask(__name__)


@app.route('/')
def index():
    """
    Define a simple function for returning useful information about the
    pedalAPI Converts the markdown README into html and serves to the
    requester
    """
    with open("./README.md") as mark:
        return markdown(mark.read(), extensions=['tables'])


@app.errorhandler(404)
def not_found(error):
    """
    If the caller attempts to use a URL not specified in the file, they will
    be given JSON information stating that there is no such page.
    """
    return make_response(jsonify({'error': 'Not found'}), 404)

# GET ------------------------------------------------------------


@app.route('/version', methods=['GET'])
def get_version():
    """ Get request to return the current version of the API """
    return jsonify({'version': str(APIVERSION)})


@app.route('/rides', methods=['GET'])
def get_all_rides():
    """ Get all of the known ride IDs """
    return jsonify({'RideIds': listdir(RIDELOCATIONS)})


@app.route('/rides/<string:ride_id>', methods=['GET'])
def get_one_ride(ride_id):
    """ Get the information on a single ride using an ID """
    return jsonify(get_ride_by_id(ride_id))


def get_ride_by_id(ride_id):
    """ Get the information about a ride by using the ID number """
    with open(RIDELOCATIONS + ride_id) as ride:
        json_data = load(ride)
        return json_data

# POST -----------------------------------------------------------


@app.route('/rides', methods=['POST'])
def add_ride():
    """
    rideURL: 127.0.0.1:5000/rides/812241

    The only POST function currently implemented is for posting rides to the
    server necessary arguments are the post version number, and a list of
    points in JSON. Currently, input should
    contain JSON like the following:
        {
        "points": [
            {
                "accuracy": 4.0,
                "latitude": 45.4,
                "longitude": -122.22,
                "time": "2013-1-12-3:21:32"
                },
            {
                "accuracy": 5.0,
                "latitude": 45.4,
                "longitude": -126.48,
                "time": "2013-1-12-3:25:32"
                }
            ],
        "version": 0.3
        "hash" : 12343234
        }

    Once the information has been posted, the user will receive JSON back.
    like so:
    {
        "RideURL": "127.0.0.1:5000/rides/812241"
    }

    A URL in which the user may do a GET request in order to receive the
    information back from the server:

        {
        "id": "812241",
        "points": [
            {
                "accuracy": 4.0,
                "latitude": 45.4,
                "longitude": -122.22,
                "time": "210123"
                }
            ],
        "version": 0.3
        }

    """
    if not request.json:
        return make_response(jsonify({'error': 'Requires JSON format'}), 400)
    elif 'version' not in request.json:
        return make_response(jsonify({'error': 'Requires version'}), 400)
    elif 'hash' not in request.json:
        return make_response(jsonify({'error': 'Requires client hash'}), 400)
    elif 'points' not in request.json:
        return make_response(jsonify(
            {'error': 'Requires location information'}), 400)
    elif not request.json['points']:
        return make_response(jsonify(
            {'error': 'Requires location information'}), 400)
    else:
        while True:
            num = gen_number()
            if num not in listdir(RIDELOCATIONS):
                break
        ride = {
            'id': str(num),
            'hash': request.json['hash'],
            'version': request.json['version'],
            'points': request.json['points']
        }
        with open(RIDELOCATIONS + str(num), 'w') as data_file:
            dump(ride, data_file)
        url_to_return = URLSTRING + '/rides/' + str(num)
        return make_response(jsonify({'RideURL': url_to_return}), 201)


def gen_number():
    """ Generate a random 6 digit number """
    return randint(100000, 999999)

# Main ------------------------------------------------------------------------


if __name__ == '__main__':
    app.run(host=Secrets.API_HOSTNAME, port=Secrets.API_PORT)
