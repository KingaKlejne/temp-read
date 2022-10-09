from typing import Any
from flask import Flask, request
import statistics
from flask_sqlalchemy import SQLAlchemy
from dateutil.parser import parse
from dateutil.parser import ParserError

# TODO 1: Create Flask App
app = Flask(__name__)

# TODO 1A: Create Database
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///readings.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# TODO 1B: Create Table
class Readings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String(250), nullable=False)
    room = db.Column(db.String(250), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    reading = db.Column(db.Float, nullable=False)


with app.app_context():
    db.create_all()


# TODO 2: ISO8601 formatting
def datetime_valid(dt_str: str) -> str:
    return str(parse(dt_str))


# TODO 3: Converting Fahrenheit to Celsius
def convert_temp(temp: float) -> float:
    return round((temp - 32) / 1.8, 2)


# TODO 4: APP POST
@app.post('/readings')
def post_route() -> tuple[dict[str, str], int]:
    try:
        data = request.get_json()
        if not isinstance(data["reading"], int) \
                or not isinstance(data["time"], str) \
                or not isinstance(data["label"], str):
            return {"error": "Value-Type not supported!"}, 400
        try:
            iso_time = datetime_valid(data["time"])
        except ParserError:
            return {"error": "Time must be in ISO8601 format!"}, 400
        place = data['label'].split(",")
        temp_c = convert_temp(data["reading"])
        new_reading = Readings(time=iso_time, room=place[0], location=place[1],
                               reading=temp_c)
        db.session.add(new_reading)
        db.session.commit()
        return {"Success": "The request has succeeded."}, 200
    except TypeError:
        return {"error": "Content-Type not supported!"}, 415


# TODO 5: APP GET with basic statistics
@app.get("/readings")
def get_data() -> tuple[dict[str, Any], int]:
    room = request.args.get("room")
    location = request.args.get("location")
    since = request.args.get("since")
    until = request.args.get("until")
    readings = Readings.query \
        .where(Readings.time <= until, Readings.time >= since) \
        .where((Readings.room == room) | (Readings.location == location))
    temp_read = [row.reading for row in readings]
    if len(temp_read) > 0:
        sensors_statistics = {
            "samples": len(temp_read),
            "min": round(min(temp_read), 2),
            "max": round(max(temp_read), 2),
            "median": round(statistics.median(temp_read), 2),
            "mean": round(statistics.mean(temp_read), 2),
        }
        return {"Success": sensors_statistics}, 200
    else:
        return {"error": "No data for this room"}, 503


# TODO 6: Run App
if __name__ == "__main__":
    app.debug = True
    app.run(port=8080)
