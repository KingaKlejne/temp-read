from flask import Flask, request, jsonify
import re
import statistics
from datetime import datetime

data_list = []
searched_data = []

# TODO 1: Create Flask App
app = Flask(__name__)

# TODO 2: ISO8601 formatting
regex = r'^(-?(?:[1-9][0-9]*)?[0-9]{4})(1[0-2]|0[1-9])(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9])([0-5][0-9])' \
        r'([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9])[0-5][0-9])?$'
match_iso8601 = re.compile(regex).match


def datetime_valid(dt_str):
    if match_iso8601(dt_str) is not None:
        return True
    else:
        return False


# TODO 3: Converting Fahrenheit to Celsius
def convert_temp(temp):
    return round((temp - 32) / 1.8, 2)


# TODO 3: APP POST
@app.post('/readings')
def post_route():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        data = request.get_json()
        if isinstance(data["reading"], int) and isinstance(data["time"], str) and isinstance(data["label"], str):
            if datetime_valid(data["time"]):
                data["reading"] = convert_temp(data["reading"])
                data_list.append(data)
                return data_list
            return {"error": "Time must be in ISO8601 format!"}, 415
        return {"error": "Value-Type not supported!"}, 415
    return {"error": "Content-Type not supported!"}, 415


# http://localhost:8080/readings?room=kitchen&since=20220927T130000Z&until=20220927T140000Z
# http://localhost:8080/readings/kitchen/20220927T152159Z/20220927T152159Z
# TODO 4: APP GET with basic statistics
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
        return "No data for this room"


# TODO 5: Run App
if __name__ == "__main__":
    # app.debug = True
    app.run(port=8080)
