from flask import Flask, Response, request
from flask_cors import CORS
import json
import logging


from application_services.GameResource.game_service import GameResource

from database_services.RDBService import RDBService as RDBService

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

application = Flask(__name__)
CORS(application)


@application.route('/')
def hello_world():
    return '<u>Hello World!</u>'

@application.route('/Game', methods=['GET', 'POST'])
def get_game():
    if request.method == 'GET':
#         res = GameResource.find_by_template(None)
#         resp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
#         return  resp
# /Game?game_id=1&game_name=Mario&fields=type1,type2
        game_id = request.args.get("game_id")
        game_name = request.args.get("game_name")
        developer = request.args.get("developer")
        fields = request.args.get("fields")
        template = {}
        if game_id:
            template['Game_id'] = game_id
        if game_name:
            template['Game_name'] = game_name
        if developer:
            template['DEVELOPER'] = developer
        res = GameResource.find_by_template_fields(fields, template)
        resp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
        return resp
    if request.method == 'POST':
        id = request.form['id']
        game_name = request.form['name']
        type1 = request.form['type1']
        type2 = request.form['type2']
        type3 = request.form['type3']
        type4 = request.form['type4']
        type5 = request.form['type5']
        dev = request.form['dev']
        create_data = {
            "Game_id": id,
            "Game_name": game_name,
            "Type1": type1,
            "Type2": type2,
            "Type3": type3,
            "Type4": type4,
            "Type5": type5,
            "DEVELOPER": dev
        }
        res = GameResource.create(create_data)
        resp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
        return resp

@application.route('/Game/<game_id>', methods = ['GET', 'DELETE'])
def get_game_by_id(game_id):
    if request.method == 'GET':
        template = {"Game_id": game_id}
        res = GameResource.find_by_template(template)
        resp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
        return resp
    elif request.method == 'DELETE':
        template = {"Game_id": game_id}
        res = GameResource.delete(template)
        resp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
        return resp

@application.route('/game_type/<type>', methods = ['GET'])
def get_game_by_type(type):
    if request.method == 'GET':
        print(type)
        template = type
        res = GameResource.find_by_type(template)
        resp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
        return resp

@application.route('/game_dev/<dev>', methods = ['GET'])
def get_game_by_dev(dev):
    if request.method == 'GET':
        print(dev)
        template = dev
        res = GameResource.find_by_dev(template)
        resp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
        return resp


if __name__ == '__main__':
    application.run(host="0.0.0.0", port=5000)
