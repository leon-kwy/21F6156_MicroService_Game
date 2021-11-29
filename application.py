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
        if (data):
            resp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
            return resp
        else:
            resp = Response(json.dumps('404 Not Found: No Games Available Now.', default=str), status=404,
                            content_type="application/json")
            return resp
    if request.method == 'POST':
        id = None
        game_name = request.form['name']
        type1 = request.form['type1']
        type2 = request.form['type2']
        type3 = request.form['type3']
        type4 = request.form['type4']
        type5 = request.form['type5']
        dev = request.form['dev']
        if(len(game_name) != 0 and len(type1) != 0 and len(type2) != 0 and len(type3) != 0 and len(type4) != 0 and
                len(type5) != 0 and len(dev) != 0):

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
            print(res)
            ans = GameResource.find_by_template({"Game_name": game_name})
            ans = ans[len(ans) - 1]['Game_id']

            succ = 'Created ' + str(create_data) + ' with ID ' + str(ans)
            # print(request.content)
            resp = Response(json.dumps(succ, default=str), status=201, content_type="application/json")
        else:
            resp = Response(json.dumps('Status Code: 400 Bad Data', default=str), status=400, content_type="application/json")

            return resp

@application.route('/Game/id/<game_id>', methods = ['GET', 'DELETE'])
def get_game_by_id(game_id):
    if request.method == 'GET':
        template = {"Game_id": game_id}
        offset = int(request.args.get("offset", OFFSET))
        limit = int(request.args.get("limit", MAXLIMIT))
        if limit > MAXLIMIT:
            limit = MAXLIMIT
        res = GameResource.find_by_template(template, limit, offset)
        if(res):
            resp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
            return resp
        else:
            resp = Response(json.dumps('404 Not Found: No such games.', default = str), status=404,
                            content_type="application/json" )
            return resp
    elif request.method == 'DELETE':
        template = {"Game_id": game_id}
        res = GameResource.delete(template)
        if(res):
            resp = Response(json.dumps('Status Code: 204 Delete Successfully', default=str),
                            status=200, content_type="application/json")
            return resp
        else:
            resp = Response(json.dumps('Status Code: 400 Bad Data', default=str), status=200, content_type="application/json")
            return resp


@application.route('/Game/name/<name>', methods = ['GET', 'DELETE'])
def get_game_by_name(name):
    if request.method == 'GET':
        template = {"Game_name": name}
        offset = int(request.args.get("offset", OFFSET))
        limit = int(request.args.get("limit", MAXLIMIT))
        if limit > MAXLIMIT:
            limit = MAXLIMIT
        res = GameResource.find_by_template(template, limit, offset)
        if(res):
            resp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
            return resp
        else:
            resp = Response(json.dumps('404 Not Found: No such games.', default = str), status=404,
                            content_type="application/json" )
            return resp
    elif request.method == 'DELETE':
        template = {"Game_name": name}
        res = GameResource.delete(template)
        if (res):
            resp = Response(json.dumps('Status Code: 204 Delete Successfully', default=str),
                            status=200, content_type="application/json")
            return resp
        else:
            resp = Response(json.dumps('Status Code: 400 Bad Data', default=str), status=200,
                            content_type="application/json")
            return resp


@application.route('/Game/type/<type>', methods = ['GET'])
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
        if (data):
            resp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
            return resp
        else:
            resp = Response(json.dumps('404 Not Found: No such games.', default=str), status=404,
                            content_type="application/json")
            return resp

          
@application.route('/Game/dev/<dev>', methods = ['GET'])
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
        if (data):
            resp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
            return resp
        else:
            resp = Response(json.dumps('404 Not Found: No such games.', default=str), status=404,
                            content_type="application/json")
            return resp


if __name__ == '__main__':
    application.run(host="0.0.0.0", port=5000)
