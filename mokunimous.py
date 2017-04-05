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
Bootstrap(app)

with open("app_config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

postapikey = cfg['app']['postapikey']


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
                             "comments_disabled": True,
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
def main():
    return render_template('post.html')


@app.route('/post', methods=['POST'])
def post():
    posttext = request.form['post']
    id = mokum_message(posttext)
    mokum_comment(id, "click to comment --> http://127.0.0.1:5000/c/" + str(id))
    return render_template('posted.html', posturl="https://mokum.place/anonymous/" + str(id), postid=str(id))


@app.route('/c/<cid>')
def comm(cid):
    return render_template('comment.html', cid=cid)


@app.route('/comment', methods=['POST'])
def commented():
    postid = request.form['cid']
    posttext = request.form['comment']
    mokum_comment(postid, posttext)
    return redirect("https://mokum.place/anonymous/" + postid)


# # mokum_message("проверка связи")
# mokum_comment(mokum_message("пр св"), "это комментарий к пост")

if __name__ == '__main__':
    app.run(debug=True)
