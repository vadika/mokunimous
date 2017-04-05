from flask import Flask
from flask import request, redirect, session, render_template, flash, url_for
from flask_bootstrap import Bootstrap
import hashlib
import urllib.request
import urllib.parse
import json
# import redis
import uuid
from pprint import pprint
import yaml

app = Flask(__name__)

postapikey = "83293677-c7d4-4483-829e-7026aa0ac2e2"

def mokum_auth(apikey):
    try:
        req = urllib.request.Request("https://mokum.place/api/v1/whoami.json")
        req.add_header('Content-Type', 'application/json')
        req.add_header('Accept', 'application/json')
        req.add_header('X-API-Token', apikey)
        resp = urllib.request.urlopen(req)
        message = json.loads(resp.read().decode("utf-8"))
        if message["user"]["name"]:
            return message["user"]["name"]
    except:
        return False


def mokum_message(message):
    try:
        postdata = {"post": {"timelines": ["user"],
                             "text": message,
                             "comments_disabled": False,
                             "nsfw": False},
                    "_uuid": str(uuid.uuid4())
                    }

        req = urllib.request.Request("https://mokum.place/api/v1/posts.json")
        req.add_header('Content-Type', 'application/json')
        req.add_header('Accept', 'application/json')
        req.add_header('X-API-Token', postapikey)

        resp = urllib.request.urlopen(req, json.dumps(postdata).encode("utf-8"))

        message = json.loads(resp.read().decode("utf-8"))

        if message['post']['id']:
            return message['post']['id']
    except:
        return False


def mokum_comment(messageid, comment):
    try:
        posturl = "https://mokum.place/api/v1/posts/" + str(messageid) + "/comments.json"
        postdata = {"comment": {"text": comment,
                                # "platform": "anonymous device"
                                },
                    "_uuid": str(uuid.uuid4())}

        req = urllib.request.Request(posturl)
        req.add_header('Content-Type', 'application/json')
        req.add_header('Accept', 'application/json')
        req.add_header('X-API-Token', postapikey)

        resp = urllib.request.urlopen(req, json.dumps(postdata).encode("utf-8"))

        message = json.loads(resp.read().decode("utf-8"))

        if message['id']:
            return message['id']

    except:
        return False

@app.route('/')
def hello_world():
    return 'Hello World!'



# # mokum_message("проверка связи")
# mokum_comment(mokum_message("пр св"), "это комментарий к пост")

if __name__ == '__main__':
    app.run(debug=True)