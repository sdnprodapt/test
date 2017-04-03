#!/usr/bin/env python

from setuptools import setup, find_packages
import os

# Allow to run setup.py from another directory.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# http://bugs.python.org/issue15881#msg170215
try:
    import multiprocessing
except ImportError:
    pass

version = '17.2.WS.3'

setup(
    name='rajuniper',
    version=version,
    url='http://cyaninc.com',
    license='CYAN',
    author='Cyan',
    author_email='support@cyaninc.com',
    description='Juniper RA',
    long_description="""\
Juniper Resource Adapter""",
    packages=find_packages(
        exclude=(
            '.*',
            'EGG-INFO',
            '*.egg-info',
            '_trial*',
            '*.tests',
            '*.tests.*',
            'tests.*',
            'tests',
            'examples.*',
            'examples*',
            )
        ),
    include_package_data=True,
    install_requires=[
        'netifaces',
        'bpprov[netconf]',
        'rasdk',
        ],
    entry_points={
        'console_scripts': [
            'rajuniper = rajuniper.main:main',
            ]
        },
    tests_require=[
        'mock',
        'nose',
        ],
    test_suite='nose.collector',
)
