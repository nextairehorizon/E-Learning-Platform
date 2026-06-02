"""
Simple MQTT publisher that send just a singe message
"""

# Use Eclipse Paho MQTT client implementation
# The documentation can be found here: https://eclipse.dev/paho/files/paho.mqtt.python/html/helpers.html#paho.mqtt.publish.single
import paho.mqtt.publish as publish
import paho.mqtt.client as client_lib

topic = "nextaire/test/message"     # Topic we want to publish to
payload = "hello from NextAIRE!"    # Data we want to publish
qos = 0                             # Quality of Service (QoS)
                                    # 0: At most once
                                    # 1: At least once
                                    # 2: Exactly once
hostname = "broker.hivemq.com"      # Broker to connect to, there are a few free ones on the internet
                                    # - broker.emqx.io
                                    # - broker.hivemq.com
                                    # - test.mosquitto.org
port = 1883                         # Port to connect to
client_id  = None                   # None equals an auto-generates the client ID, caution the client ID must be unique on a broker
keepalive = 60                      # Timeout for each sending try
retain = False                      # Ask the broker to not keep the messages in its storage
protocol = client_lib.MQTTv5        # Protocol version


publish.single(topic=topic, payload=payload, qos=qos, 
               hostname=hostname, port=port, 
               client_id=client_id, keepalive=keepalive, retain=retain, protocol=protocol )
