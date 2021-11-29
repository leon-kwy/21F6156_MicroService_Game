from flask import Flask, Response, request
from flask_cors import CORS
import json
import logging
import re

from application_services.GameResource.game_service import GameResource

from database_services.RDBService import RDBService as RDBService

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# pagination data
OFFSET = 0
MAXLIMIT = 20

# help function for pagination
def handle_links(url, offset, limit):
    if "?" not in url:
        url += "?offset=" +str(offset)+"&limit=" +str(limit)
    else:
        if "offset" not in url:
            url = url + "&offset=" +str(offset)
        if "limit" not in url:
            url = url +"&limit=" +str(limit)
    links = []
    nexturl = re.sub("offset=\d+","offset="+str(offset+limit), url)
    prevurl = re.sub("offset=\d+","offset="+str(max(0,offset-limit)), url)
    links.append({"rel":"self","href":url})
    links.append({"rel":"next","href":nexturl})
    links.append({"rel":"prev","href":prevurl})
    return links

application = Flask(__name__)
CORS(application)


@application.route('/')
def hello_world():
    return '<u>Hello World!</u>'

@application.route('/Game', methods=['GET', 'POST'])
def get_game():
    if request.method == 'GET':
        offset = int(request.args.get("offset", OFFSET))
        limit = int(request.args.get("limit", MAXLIMIT))
        if limit > MAXLIMIT:
            limit = MAXLIMIT
        data = GameResource.find_by_template(None, limit, offset)
        links = handle_links(request.url, offset, limit)
        res ={"data":data,"links":links}
        resp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
        return  resp
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
        offset = int(request.args.get("offset", OFFSET))
        limit = int(request.args.get("limit", MAXLIMIT))
        if limit > MAXLIMIT:
            limit = MAXLIMIT
        data = GameResource.find_by_type(template, limit, offset)
        links = handle_links(request.url, offset, limit)
        res ={"data":data,"links":links}
        resp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
        return resp

@application.route('/game_dev/<dev>', methods = ['GET'])
def get_game_by_dev(dev):
    if request.method == 'GET':
        print(dev)
        template = dev
        offset = int(request.args.get("offset", OFFSET))
        limit = int(request.args.get("limit", MAXLIMIT))
        if limit > MAXLIMIT:
            limit = MAXLIMIT
        data = GameResource.find_by_dev(template, limit, offset)
        links = handle_links(request.url, offset, limit)
        res ={"data":data,"links":links}
        resp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
        return resp


if __name__ == '__main__':
    application.run(host="0.0.0.0", port=5000)
