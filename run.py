#!/usr/bin/env python3

import os
import json
from flask import Flask
from flask import render_template, send_from_directory, Response, url_for, request

# app initialization
app = Flask(__name__)
app.config.update(
    TEMPLATES_AUTO_RELOAD = True,
    DEBUG = True,
    SECRET_KEY = 'e535b3c89a1288055e335fba78cc5b84c5a8ef5620b6b3f1'
)

# controllers
@app.route('/')
def index_page():
    return render_template('index.html')

@app.route('/result/', methods=["POST"])
def result_page():
    keyword = request.form.get("keyword", None)
    date = request.form.get("date", None)
    length = request.form.get("length", None)
    views = request.form.get("views", None)
    lat, lon = request.form.get("lat", None), request.form.get("lon", None)

    # call reranking function

    return "result"


# special file handlers
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'img/favicon.ico')

# error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# server launchpad
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)