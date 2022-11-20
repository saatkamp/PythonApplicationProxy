# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='drivermqtt',
    version='0.0.1',
    description='OpenTOSCA MQTT Driver',
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=[
        "drivermanager",
        "paho-mqtt",
    ],
)
