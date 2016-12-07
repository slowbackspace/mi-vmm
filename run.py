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


def parse_float_or_none(value):
    if value == "":
        return None
    else:
        return float(value)


def parse_float_or_zero(value):
    if value == "":
        return None
    else:
        return 0


@app.route('/')
def index_page():
    return render_template('index.html')


@app.route('/result/', methods=["POST"])
def result_page():
    keyword = request.form.get("keyword")
    date = request.form.get("date") or None
    duration = parse_float_or_none(request.form.get("duration"))
    views = parse_float_or_none(request.form.get("views"))
    lat, lon = parse_float_or_none(request.form.get("lat")), parse_float_or_none(request.form.get("lon"))
    weight_views = float(request.form.get("weight-views"))
    weight_date = float(request.form.get("weight-date"))
    weight_duration = float(request.form.get("weight-duration"))
    weight_location = float(request.form.get("weight-location"))

    location = (lat, lon)

    if request.form.get("checkbox-location", None):
        location = None
    if request.form.get("checkbox-duration", None):
        duration = None
    if request.form.get("checkbox-views", None):
        views = None
    if request.form.get("checkbox-date", None):
        date = None

    if date:
        datetime_obj = datetime.datetime.strptime(date, "%m/%d/%Y").replace(tzinfo=datetime.timezone.utc)
    else:
        datetime_obj = None

    result = reranking.search(keyword=keyword, length=duration, lengthW=weight_duration, views=views,
                    viewsW=weight_views, location=location, locW=weight_location,
                    date=datetime_obj, dateW=weight_date)

    return render_template("vids.html", result=result)


# special file handlers
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'img/favicon.ico')



# server launchpad
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)