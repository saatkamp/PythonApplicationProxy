# -*- coding: utf-8 -*-
import datetime
import json
import logging
import time

import yaml

from pydoc import locate
from collections import namedtuple

from yaml import UnsafeLoader


class DriverManager(object):
    """ Used by the application developer """

    callback_response = None

    def __init__(self, filespec) -> None:
        self.cfg = DriverManagerConfig(filespec)
        self.connection_cache = {}

    def publish(self, sensor_name, payload):
        # (1) Determine topic definitions based on given sensor name
        # (2) Send payload to all topic definitions
        # (3) Therefore, create a connection with the determined driver
        # (4) Publish payload through the created connection (threaded)
        topics = self.cfg.get_topics(sensor_name)
        for topic in topics:
            # Create or get a cached connection
            key = "[{}][{}][{}][{}]".format(topic['name'], topic['sensor'], topic['driver'], topic['connection'])
            conn = self.connection_cache.get(key, None)
            if conn is None:
                logging.info("Creating a new connection with driver \"{}\"".format(topic['driver']))
                driver = Driver.for_name(topic['driver'])
                conn = driver.connect(topic)
                self.connection_cache[key] = conn
            # Sending message
            sensor = self.cfg.get_sensors()[sensor_name]
            message = Message(sensor, payload)
            conn.publish(topic['name'], json.dumps(message.__dict__))

    def subscribe(self, sensor_name, callback):
        # (1) Determine topic definitions based on given type
        # (2) Subscribe to all topic definitions
        # (3) Therefore, get a connection with the determined driver
        topics = self.cfg.get_topics(sensor_name)
        for topic in topics:
            # Create or get a cached connection
            key = "[{}][{}][{}][{}]".format(topic['name'], topic['sensor'], topic['driver'], topic['connection'])
            conn = self.connection_cache.get(key, None)
            if conn is None:
                logging.info("Creating a new connection with driver \"{}\"".format(topic['driver']))
                driver = Driver.for_name(topic['driver'])
                conn = driver.connect(topic)
                self.connection_cache[key] = conn
            conn.subscribe(topic['name'], lambda message: callback(
                json.loads(message, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))))

    def request_response(self, payload):
        self.callback_response = None
        config = self.cfg.get_request_topic()
        # Establish connection to reply topic
        driver = Driver.for_name(config['driver'])
        reply_to = "response/" + str(time.time())
        logging.info("Reply Topic is " + reply_to)
        conn = driver.connect(config)
        conn.subscribe(reply_to, lambda message: self.response_callback(message))

        key = "[{}][{}][{}]".format(config['name'], config['driver'], config['connection'])
        conn = self.connection_cache.get(key, None)
        if conn is None:
            logging.info("Creating a new connection with driver \"{}\"".format(config['driver']))
            driver = Driver.for_name(config['driver'])
            conn = driver.connect(config)
            self.connection_cache[key] = conn
        # Sending message
        message = ReqRepMessage(reply_to, payload)
        conn.publish(config['name'], json.dumps(message.__dict__), reply_to)

        while self.callback_response is None:
            logging.info("Waiting for response on " + reply_to)
            time.sleep(1)

        return self.callback_response

    def response_callback(self, response):
        self.callback_response = response


def close(self):
    for conn in self.connection_cache.values():
        conn.close()


class DriverManagerConfig(object):
    """ Helper class to work with the configuration """

    def __init__(self, filespec) -> None:
        with open(filespec, 'r') as file:
            self.cfg = yaml.load(file, Loader=UnsafeLoader)

    def get_sensors(self):
        return self.cfg['sensors']

    def get_topics(self, sensor_name=None):
        if sensor_name is None:
            return self.cfg['topics']
        topics = []
        for topic in self.cfg['topics']:
            if sensor_name == topic['sensor']:
                topics.append(topic)
        return topics

    def get_request_topic(self):
        return self.cfg['requestReplyTopic']


class Message(object):
    """ Generic message object """

    def __init__(self, sensor={}, payload=None) -> None:
        self.sensor = sensor
        self.payload = payload


class ReqRepMessage(object):
    """ Generic message object """

    def __init__(self, replyTo, payload=None) -> None:
        self.replyTo = replyTo
        self.payload = payload


class Driver(object):
    """ Abstract Driver class """

    def connect(self, topic=None):
        """ Creates a connection to a Message Broker with the given arguments. """
        raise NotImplementedError('connect(): Driver is supposed to be an abstract class')

    @staticmethod
    def for_name(name):
        """ Factory method to create a concrete Driver instance object. """
        clazz = locate(name)
        if clazz is None:
            logging.warning("Could not load driver \"{}\", falling back to noop driver implementation".format(name))
            clazz = locate("drivermanager.NoopDriver")
        return clazz()


class Connection(object):
    """ Abstract Connection class """

    def publish(self, topic, payload, reply_to=None):
        """ Sends a payload to a given topic """
        raise NotImplementedError('publish(): Connection is supposed to be an abstract class')

    def subscribe(self, topic, callback):
        """ Subscribes to given topic """
        raise NotImplementedError('subscribe(): Connection is supposed to be an abstract class')

    def close(self):
        """ Closes the connection to the Message Broker """
        raise NotImplementedError('close(): Connection is supposed to be an abstract class')


class NoopDriver(Driver):
    """ No-op Driver """

    def connect(self, topic=None):
        return NoopConnection()


class NoopConnection(Connection):
    """ No-op Connection """

    def publish(self, topic, payload):
        logging.info("NOOP: Sending to topic \"{}\": {}".format(topic, payload))

    def subscribe(self, topic, callback):
        logging.info("NOOP: Subscribing to topic \"{}\"".format(topic))

    def close(self):
        logging.info("NOOP: Connection closed")
