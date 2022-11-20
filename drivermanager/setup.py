# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='drivermanager',
    version='0.0.1',
    description='OpenTOSCA Driver Manager',
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=[],
)
