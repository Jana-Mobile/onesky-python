#!/usr/bin/env python

from setuptools import setup

setup(
    name='onesky-python',
    version='1.0.2',
    description='python wrapper for the OneSky REST API',
    author='Jana Mobile',
    author_email='technology@jana.com',
    maintainer='Dan OBrien',
    maintainer_email='danob@jana.com',
    install_requires=[
        'requests>=2.3.0,<3.0',
        'termcolor>=1.1.0,<2.0'
    ],
    license='LICENSE.txt',
    packages=['onesky'],
    url='https://github.com/Jana-Mobile/onesky-python'
)
