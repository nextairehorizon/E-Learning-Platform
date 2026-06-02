"""
Simple MQTT subscriber that listens to all messages with a specific topic and prints the messages
"""

# Use Eclipse Paho MQTT client implementation
# The documentation can be found here https://eclipse.dev/paho/files/paho.mqtt.python/html/client.html
import paho.mqtt.client as client_lib


def on_connect(mqtt_client, userdata, connect_flags, reason_code, properties):
    """The callback called when the broker reponds to our connection request.
    
    :param Client mqtt_client: the client instance for this callback
    :param userdata: the private user data as set in Client() or user_data_set()
    :param ConnectFlags connect_flags: the flags for this connection
    :param ReasonCode reason_code: the connection reason code received from the broken.
            In MQTT v5.0 it's the reason code defined by the standard.
            In MQTT v3, we convert return code to a reason code.
    :param Properties properties: the MQTT v5.0 properties received from the broker.
            For MQTT v3.1 and v3.1.1 properties is not provided and an empty Properties object is always used.
    """
    print("Connected with reason_code: " + str(reason_code))

def on_subscribe(mqtt_client, userdata, mid, reason_code_list, properties):
    """The callback called when the broker responds to a subscribe request.

    :param Client mqtt_client: the client instance for this callback
    :param userdata: the private user data as set in Client() or user_data_set()
    :param int mid: matches the mid variable returned from the corresponding subscribe() call.
    :param list[ReasonCode] reason_code_list: reason codes received from the broker for each subscription.
            In MQTT v5.0 it's the reason code defined by the standard.
            In MQTT v3, we convert granted QoS to a reason code.
            It's a list of ReasonCode instances.
    :param Properties properties: the MQTT v5.0 properties received from the broker.
            For MQTT v3.1 and v3.1.1 properties is not provided and an empty Properties object is always used.
    """
    print("Subscribed: " + str(mid) + " " + str(reason_code_list))

def on_message(mqtt_client, userdata, message):
    """The callback called when a message has been received on a topic
    that the client subscribes to.

    :param Client mqtt_client: the client instance for this callback
    :param userdata: the private user data as set in Client() or user_data_set()
    :param MQTTMessage message: the received message.
                This is a class with members topic, payload, qos, retain.
    """
    print(message.topic + " " + str(message.qos) + " " + str(message.payload))


# Create the client and define the call backs
callback_api_version = client_lib.CallbackAPIVersion.VERSION2  # Latest API Version
client_id = None                                               # None equals an auto-generates the client ID, caution the client ID must be unique on a broker
userdata = None                                                # Data passed to the call backs defined above
protocol = client_lib.MQTTv5                                   # Protocol version
client = client_lib.Client(callback_api_version=callback_api_version, client_id=client_id, userdata=userdata, protocol=protocol)
client.on_message = on_message
client.on_connect = on_connect
client.on_subscribe = on_subscribe


# Connect to the broker
# There are several free brokers on the internet for test:
# - broker.emqx.io
# - broker.hivemq.com
# - test.mosquitto.org
client.connect("broker.hivemq.com", 1883, 60)                 # Host, port and connection timeout

# Subscribe to the topic
# System messages can be collected from the topic $SYS/#
client.subscribe("$SYS/#")
client.subscribe("nextaire/test/message")

# Keep running
client.loop_forever()
