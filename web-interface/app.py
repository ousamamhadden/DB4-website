from flask import Flask, render_template, request, jsonify
import requests
import json
import sys
from Adafruit_IO import MQTTClient
from datetime import datetime
ADAFRUIT_IO_KEY = "aio_beVb385lySKos5Xj8rOW4RBLTcnY"

# Set to your Adafruit IO username.
# (go to https://accounts.adafruit.com to find your username)
ADAFRUIT_IO_USERNAME = 'ousamamhadden'

# Set to the ID of the feed to subscribe to for updates.
FEED_ID = 'temperature'


# Define callback functions which will be called when certain events happen.
def connected(client):
    # Connected function will be called when the client is connected to Adafruit IO.
    # This is a good place to subscribe to feed changes.  The client parameter
    # passed to this function is the Adafruit IO MQTT client so you can make
    # calls against it easily.
    print('Connected to Adafruit IO!  Listening for {0} changes...'.format(FEED_ID))
    # Subscribe to changes on a feed named DemoFeed.
    client.subscribe(FEED_ID)

def subscribe(client, userdata, mid, granted_qos):
    # This method is called when the client subscribes to a new feed.
    print('Subscribed to {0} with QoS {1}'.format(FEED_ID, granted_qos[0]))

def disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print('Disconnected from Adafruit IO!')
    sys.exit(1)

def message(client, feed_id, payload):
    # Message function will be called when a subscribed feed has a new value.
    # The feed_id parameter identifies the feed, and the payload parameter has
    # the new value.
    global temp
    temp = payload

    print('Feed {0} received new value: {1}'.format(feed_id, payload))



# Create an MQTT client instance.
client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

# Setup the callback functions defined above.
client.on_connect    = connected
client.on_disconnect = disconnected
client.on_message    = message
client.on_subscribe  = subscribe

# Connect to the Adafruit IO server.
client.connect()
# Start a message loop that blocks forever waiting for MQTT messages to be
# received.  Note there are other options for running the event loop like doing
# so in a background thread--see the mqtt_client.py example to learn more.
client.loop_background()
response = requests.get("https://io.adafruit.com/api/v2/ousamamhadden/feeds/temperature/data/?X-AIO-Key=aio_beVb385lySKos5Xj8rOW4RBLTcnY")
a = response.json()
b = a[0]
value = b['value']
temp = value
app = Flask(__name__)

@app.route("/_stuff", methods= ["GET"])
def stuff():
    return jsonify(result = temp)

@app.route("/", methods=["POST","GET"])
def home():
    if request.method == "POST":
        inte =  int(request.form["tmp"])
        sent = {"datum":{"value": str(inte)}}
        requests.post("https://io.adafruit.com/api/v2/ousamamhadden/feeds/temperature/data/?X-AIO-Key=aio_beVb385lySKos5Xj8rOW4RBLTcnY", json=sent)


    return render_template("index.html")

@app.route("/graph")
def graph():
    query = {'start_time':'2021/08/07 1:00:00AM', 'end_time':datetime.now().isoformat()}
    response2 = requests.get("https://io.adafruit.com/api/v2/ousamamhadden/feeds/temperature/data/chart/?X-AIO-Key=aio_beVb385lySKos5Xj8rOW4RBLTcnY",params=query)
    alldata = response2.json()
    data = alldata['data']
    #data = [["1",1],["2",2],["3",3],["4",4],["5",5],["6",6]]
    labels = [row[0] for row in data]
    values = [row[1] for row in data]


    return render_template("graph.html", labels = labels, values = values)


if __name__ == "__main__":
    app.run(debug=True)
