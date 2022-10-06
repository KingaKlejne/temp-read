from flask import Flask, request, jsonify
import re
import statistics
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


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
# Next: to update
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
        if not isinstance(data["reading"], int) or not isinstance(data["time"], str) \
                or not isinstance(data["label"], str):
            return {"error": "Value-Type not supported!"}, 400
        if not datetime_valid(data["time"]):
            return {"error": "Time must be in ISO8601 format!"}, 400
        place = data['label'].split(",")
        data["reading"] = convert_temp(data["reading"])
        new_reading = Readings(time=data['time'], room=place[0], location=place[1], reading=data['reading'])
        db.session.add(new_reading)
        db.session.commit()
        return {"Success": "The request has succeeded."}, 200
    except TypeError:
        return {"error": "Content-Type not supported!"}, 415


# TODO 5: APP GET with basic statistics
# Next: What if user provide only room or only location?
@app.get("/readings/<room>/<location>/<since>/<until>")
def get_data(room, location, since, until):
    readings = Readings.query.where(Readings.time <= until, Readings.time >= since, Readings.room == room,
                                    Readings.location == location).all()
    temp_read = [row.reading for row in readings]
    if len(temp_read) > 0:
        sensors_statistics = {
            "samples": len(temp_read),
            "min": min(temp_read),
            "max": max(temp_read),
            "median": statistics.median(temp_read),
            "mean": statistics.mean(temp_read)
        }
        return jsonify(sensors_statistics)
    else:
        return {"error": "No data for this room"}, 503


# TODO 6: Run App
if __name__ == "__main__":
    app.debug = True
    app.run(port=8080)
