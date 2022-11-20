# -*- coding: utf-8 -*-

import logging
import sys
import uuid

import paho.mqtt.client as mqtt

from drivermanager.drivermanager import Driver, Connection

sys.path.append('../')



class MqttDriver(Driver):
    """ MQTT Driver """

    def connect(self, topic=None):
        connection = topic['connection'].split(":")
        return MqttConnection(str(connection[0]), int(connection[1]))


class MqttConnection(Connection):
    """ MQTT Connection """

    def __init__(self, hostname, port):
        self.callbacks = {}
        self.client = mqtt.Client(client_id=str(uuid.uuid4()), clean_session=True, userdata=None)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(hostname, port, 60)
        self.client.loop_start()

    def publish(self, topic, payload):
        logging.info("MQTT: Sending to topic \"{}\": {}".format(topic, payload))
        self.client.publish(topic=topic, payload=payload, qos=0, retain=False)

    def subscribe(self, topic, callback):
        logging.info("MQTT: Subscribed to topic \"{}\"".format(topic))
        self.client.subscribe(topic)
        self.callbacks[topic] = callback

    def close(self):
        for topic in self.callbacks.keys():
            self.client.unsubscribe(topic)
        self.client.loop_stop(True)

    def on_connect(self, client, userdata, flags, rc):
        logging.info("MQTT: Connected to broker, client={}, userdata={}, flags={}, rc={}"
                     .format(client, userdata, flags, rc))

    def on_message(self, client, userdata, message):
        cb = self.callbacks.get(message.topic, None)
        if cb is not None:
            logging.info("MQTT: Received message on topic \"{}\": {}".format(message.topic, message.payload))
            cb(message.payload)
