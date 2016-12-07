#!/usr/bin/env python3

import os
import json
from flask import Flask
from flask import render_template, send_from_directory, Response, url_for, request
import reranking
import datetime

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
    duration = float(request.form.get("duration", None))
    views = float(request.form.get("views", None))
    lat, lon = float(request.form.get("lat", None)), float(request.form.get("lon", None))
    weight_views = float(request.form.get("weight-views", 0))
    weight_date = float(request.form.get("weight-date", 0))
    weight_duration = float(request.form.get("weight-duration", 0))
    weight_location = float(request.form.get("weight-location", 0))

    # call reranking function
    datetime_obj = datetime.datetime.strptime(date, "%m/%d/%Y").replace(tzinfo=datetime.timezone.utc)
    result = reranking.search(keyword=keyword, length=duration, lengthW=weight_duration, views=views,
                    viewsW=weight_views, location = (lat, lon), locW=weight_location,
                    date=datetime_obj, dateW=weight_date)

    return str(result)


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