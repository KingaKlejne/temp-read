# temp-read

Temp-read is a Flask API application allowing to insert temperature readings from different sensors at home and displaing basic statistics for specific locations. All data are storage in the SQL database, hence they are accessible even when server is down.

## Installation

Install with pip:

```
$ pip install -r requirements.txt
```

## Run Flask

```
$ python main.py
```
In Flask, Default port is `5000`

Swagger document page:  `http://127.0.0.1:5000/readings`

## POST Data
Requirements:
- Data must be provided as json file, with the following variables:
- time: string in ISO8601 format
- label: string provided as room and location where the sensor is located with no additional comma between, i.e.  "label": "garage,window"
- reading: float, temperature reading provided in Farenheit (while uploading to database it will be converted to Celsius)

### How to input data?
Run curl command as in the example below.

```
$ curl \
      --request POST \
      --header "Content-Type: application/json" \
      --data '{"time": "20220927T152159Z", "label": "kitchen,window", "reading": 68}' \
      http://localhost:5000/readings
```
Or connect to API through Python file as in the example below:

```
import requests

data = {"time": "2022-09-12T17:47:03Z", "label": "garage,window", "reading": 69}
response = requests.post('http://localhost:5000/readings', json=data)
```

## GET Data

Get request is providing simple statistics for the selected room and/or location such as listed below in dictionary format. 
- total number of samples
- minimum value of temperatures
- maximum value of temperatures
- median value of temperatures
- mean value of temperatures

To get data you must provide room and or location along with since and until time.

### How to get data?
Run curl command as any of the examples below.
```
$ curl "http://localhost:5000/readings?room=kitchen&since=20220927T152159Z&until=20220927T152159Z"
$ curl "http://localhost:5000/readings?room=bedroom&location=floor&since=2022-08-20T20:00:00&until=2022-10-13T20:00:00"
```
Or connect to API through Python file as in the example below:
```
response = requests.get("http://localhost:5000/readings?room=bedroom&since=2022-08-20T20:00:00&until=2022-10-13T20:00:00")
```

## Run tests
```
$ pytest test.py
```

## Reference

Offical Websites

- [Flask](http://flask.pocoo.org/)
- [Flask-SQLalchemy](https://flask-sqlalchemy.palletsprojects.com/en/3.0.x/)
