# temp-read

Temp-read is a simple Flask application to insert temperature readings from different sensors at home and display basic statistics.

### How to use
To use the application run it on your local computer. It will run a local server to which you may insert the data running curl command in your Terminal like in the example below. Remember that data needs to be provided in the json format only. "time" and "label" needs to be string and "time" needs to be provided in  ISO8601 format. Furthermore, "reading" is a temperature value in Farenheit which must be provided as an integer.
```
curl \
      --request POST \
      --header "Content-Type: application/json" \
      --data '{"time": "20220927T152159Z", "label": "kitchen,window", "reading": 68}' \
      http://localhost:8080/readings
```
 Once you’ll input the data you can gather basic statistics such as maximum and minimum values of provided samples, but also mean, median and number of samples for specific room location. The numbers may be different to what you expect as at this point the temperature readings are changed to Celsius. 
 
 To get the statistics use curl command as present below. The following parts after '/' refers to ".../room/since/until"
```
curl http://localhost:8080/readings/kitchen/20220927T152159Z/20220927T152159Z
```
