from flask import Flask
from flask import request, redirect, render_template
from flask_bootstrap import Bootstrap
import urllib.request
import urllib.parse
import json
import uuid
import yaml
import hashlib
from Crypto import Random
from Crypto.Cipher import AES
import base64




app = Flask(__name__)
Bootstrap(app)

with open("app_config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

postapikey = cfg['app']['postapikey']
mainurl = cfg['app']['mainurl']
appurl = cfg['app']['appurl']
secretkey = cfg['app']['secret']

# Some crypto staff

BLOCK_SIZE = 16


def trans(key):
    return hashlib.md5(key.encode("utf-8")).digest()


def encrypt(message, passphrase):
    passphrase = trans(passphrase)
    IV = Random.new().read(BLOCK_SIZE)
    aes = AES.new(passphrase, AES.MODE_CFB, IV)
    return base64.b64encode(IV + aes.encrypt(message)).decode("utf-8")


def decrypt(encrypted, passphrase):
    passphrase = trans(passphrase)
    encrypted = base64.b64decode(encrypted)
    IV = encrypted[:BLOCK_SIZE]
    aes = AES.new(passphrase, AES.MODE_CFB, IV)
    return aes.decrypt(encrypted[BLOCK_SIZE:]).decode("utf-8")


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
    mokum_comment(id, "click to comment --> " + appurl + "/c/" + encrypt(str(id), secretkey))
    return redirect(mainurl + str(id))


@app.route('/c/<cid>')
def comm(cid):
    return render_template('comment.html', cid=cid)


@app.route('/comment', methods=['POST'])
def commented():
    postid = decrypt(request.form['cid'], secretkey)
    posttext = request.form['comment']
    mokum_comment(postid, posttext)
    return redirect(mainurl + postid)


if __name__ == '__main__':
    app.run(debug=True)
