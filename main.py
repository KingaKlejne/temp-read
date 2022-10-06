from flask import Flask, request, jsonify
import re
import statistics
import sqlite3
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

data_list = []
searched_data = []

# TODO 1: Create Flask App
app = Flask(__name__)

# TODO 1A: Create Database
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///readings.db"
# Optional: But it will silence the deprecation warning in the console.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# TODO 1B: Create Table
class Readings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String(250), nullable=False)
    room = db.Column(db.String(250), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    reading = db.Column(db.Float, nullable=False)


db.create_all()

# TODO 2: ISO8601 formatting
regex = r'^(-?(?:[1-9][0-9]*)?[0-9]{4})(1[0-2]|0[1-9])(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9])([0-5][0-9])' \
        r'([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9])[0-5][0-9])?$'
match_iso8601 = re.compile(regex).match


def datetime_valid(dt_str):
    return match_iso8601(dt_str) is not None


# TODO 3: Converting Fahrenheit to Celsius
def convert_temp(temp):
    return round((temp - 32) / 1.8, 2)


# TODO 4: APP POST
@app.post('/readings')
def post_route():
    try:
        data = request.get_json()
        place = data['label'].split(",")
        data["reading"] = convert_temp(data["reading"])
        new_reading = Readings(time=data['time'], room=place[0], location=place[1], reading=data['reading'])
        db.session.add(new_reading)
        db.session.commit()
        if not isinstance(data["reading"], int) and not isinstance(data["time"], str) and not isinstance(data["label"],
                                                                                                         str):
            return {"error": "Value-Type not supported!"}, 400
        if not datetime_valid(data["time"]):
            return {"error": "Time must be in ISO8601 format!"}, 400
        data_list.append(data)
        return jsonify(data_list)
    except TypeError:
        return {"error": "Content-Type not supported!"}, 415


# TODO 5: APP GET with basic statistics
@app.get("/readings/<room>/<since>/<until>")
def get_data(room, since, until):
    global data_list
    since = datetime.strptime(since, '%Y%m%dT%H%M%SZ')
    until = datetime.strptime(until, '%Y%m%dT%H%M%SZ')
    for i in data_list:
        if room in i["label"]:
            i["time"] = datetime.strptime(i["time"], '%Y%m%dT%H%M%SZ')
            if since <= i["time"] <= until:
                searched_data.append(i["reading"])
    if len(searched_data) > 0:
        sensors_statistics = {
            "samples": len(searched_data),
            "min": min(searched_data),
            "max": max(searched_data),
            "median": statistics.median(searched_data),
            "mean": statistics.mean(searched_data)
        }
        return jsonify(sensors_statistics)
    else:
        return {"error": "No data for this room"}, 503


# TODO 6: Run App
if __name__ == "__main__":
    app.debug = True
    app.run(port=8080)
