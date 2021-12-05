import time

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
MAXLIMIT = 2


# help function for pagination
def handle_links(url, offset, limit):
    if "?" not in url:
        url += "?offset=" + str(offset) + "&limit=" + str(limit)
    else:
        if "offset" not in url:
            url = url + "&offset=" + str(offset)
        if "limit" not in url:
            url = url + "&limit=" + str(limit)
    links = []
    nexturl = re.sub("offset=\d+", "offset=" + str(offset + limit), url)
    prevurl = re.sub("offset=\d+", "offset=" + str(max(0, offset - limit)), url)
    links.append({"rel": "self", "href": url})
    links.append({"rel": "next", "href": nexturl})
    links.append({"rel": "prev", "href": prevurl})
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
        res = {"data": data, "links": links}
        if (data):
            resp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
            return resp
        else:
            resp = Response(json.dumps('404 Not Found: No Games Available Now.', default=str), status=404,
                            content_type="application/json")
            return resp
    if request.method == 'POST':
        id = int(time.time())
        game_name = request.form['Game_name']
        type = request.form['G_Type']
        type = type.split(',')

        dev = request.form['DEVELOPER']
        if len(game_name) != 0 and len(type) and len(dev) != 0:
            create_data = {
                "id": id,
                "Game_name": game_name,
                "G_Type": type,
                "insertedAtTimestamp": time.asctime(time.localtime(time.time())),
                "DEVELOPER": dev
            }
            res = GameResource.create(create_data)
            print(res)
            succ = 'Created ' + str(create_data) + ' with ID ' + str(id)
            resp = Response(json.dumps(succ, default=str), status=201, content_type="application/json")

        else:
            resp = Response(json.dumps('Status Code: 400 Bad Data', default=str), status=400,
                            content_type="application/json")

        return resp


@application.route('/Game/id/<game_id>', methods=['GET', 'DELETE'])
def get_game_by_id(game_id):
    if request.method == 'GET':
        template = {"id": game_id}
        offset = int(request.args.get("offset", OFFSET))
        limit = int(request.args.get("limit", MAXLIMIT))
        if limit > MAXLIMIT:
            limit = MAXLIMIT
        res = GameResource.find_by_template(template, limit, offset)
        if (res):
            resp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
            return resp
        else:
            resp = Response(json.dumps('404 Not Found: No such games.', default=str), status=404,
                            content_type="application/json")
            return resp
    elif request.method == 'DELETE':
        template = {"id": int(game_id)}
        res = GameResource.delete(template)
        if (res):
            resp = Response(json.dumps('Status Code: 204 Delete Successfully', default=str),
                            status=200, content_type="application/json")
            return resp
        else:
            resp = Response(json.dumps('Status Code: 400 Bad Data', default=str), status=200,
                            content_type="application/json")
            return resp


@application.route('/Game/name/<name>', methods=['GET', 'DELETE'])
def get_game_by_name(name):
    if request.method == 'GET':
        template = {"Game_name": name}
        offset = int(request.args.get("offset", OFFSET))
        limit = int(request.args.get("limit", MAXLIMIT))
        if limit > MAXLIMIT:
            limit = MAXLIMIT
        res = GameResource.find_by_template(template, limit, offset)
        print(res[0]['id'])
        if (res):
            resp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
            return resp
        else:
            resp = Response(json.dumps('404 Not Found: No such games.', default=str), status=404,
                            content_type="application/json")
            return resp
    elif request.method == 'DELETE':
        template = {"Game_name": name}
        offset = int(request.args.get("offset", OFFSET))
        limit = int(request.args.get("limit", MAXLIMIT))
        ID = GameResource.find_by_template(template, limit, offset)[0]['id']
        template = {'id': ID}
        res = GameResource.delete(template)
        if (res):
            resp = Response(json.dumps('Status Code: 204 Delete Successfully', default=str),
                            status=200, content_type="application/json")
            return resp
        else:
            resp = Response(json.dumps('Status Code: 400 Bad Data', default=str), status=200,
                            content_type="application/json")
            return resp


@application.route('/Game/addType', methods=['POST'])
def update_game_type():
    if request.method == 'POST':
        offset = int(request.args.get("offset", OFFSET))
        limit = int(request.args.get("limit", MAXLIMIT))

        game_name = request.form['Game_name']
        type = request.form['G_Type'].split(',')
        template = {'Game_name': game_name}
        ID = GameResource.find_by_template(template, limit, offset)[0]['id']

        if len(game_name) != 0 and len(type) != 0:
            resp = GameResource.insert({'id': ID}, type)
            return resp


@application.route('/Game/updateGame', methods=['POST'])
def update_game():
    if request.method == 'POST':
        offset = int(request.args.get("offset", OFFSET))
        limit = int(request.args.get("limit", MAXLIMIT))

        game_name = request.form['Game_name']
        game_info = RDBService.find_by_template({'Game_name': game_name}, limit, offset)

        ID = game_info[0]['id']
        select_data = {
            "Game_name": game_name,
            "G_Type": game_info[0]['G_Type'],
            "DEVELOPER": game_info[0]['DEVELOPER'],
            "version": game_info[0]['version'],
            "insertedAtTimestamp": game_info[0]['insertedAtTimestamp']
        }
        update_data = select_data
        update_data['insertedAtTimestamp'] = time.asctime(time.localtime(time.time()))
        for k,v in request.form.items():
            update_data[k] = v

        if len(game_name) != 0:
            resp = GameResource.update(ID, update_data)
            resp = Response(json.dumps(resp, default=str), status=201, content_type="application/json")
            return resp


@application.route('/Game/type/<type>', methods=['GET'])
def get_game_by_type(type):
    if request.method == 'GET':
        Type = []
        Type += type.split(',')
        template = {'G_Type': Type}
        offset = int(request.args.get("offset", OFFSET))
        limit = int(request.args.get("limit", MAXLIMIT))
        if limit > MAXLIMIT:
            limit = MAXLIMIT
        data = GameResource.find_by_template(template, limit, offset)
        links = handle_links(request.url, offset, limit)
        res = {"data": data, "links": links}
        if (data):
            resp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
            return resp
        else:
            resp = Response(json.dumps('404 Not Found: No such games.', default=str), status=404,
                            content_type="application/json")
            return resp


@application.route('/Game/dev/<dev>', methods=['GET'])
def get_game_by_dev(dev):
    if request.method == 'GET':
        print(dev)
        template = {'DEVELOPER': dev}
        offset = int(request.args.get("offset", OFFSET))
        limit = int(request.args.get("limit", MAXLIMIT))
        if limit > MAXLIMIT:
            limit = MAXLIMIT
        data = GameResource.find_by_template(template, limit, offset)
        links = handle_links(request.url, offset, limit)
        res = {"data": data, "links": links}
        if (data):
            resp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
            return resp
        else:
            resp = Response(json.dumps('404 Not Found: No such games.', default=str), status=404,
                            content_type="application/json")
            return resp


if __name__ == '__main__':
    application.run(host="0.0.0.0", port=5000)
