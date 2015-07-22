#!/usr/bin/env python

from setuptools import setup, find_packages
import sys
import os

# Allow to run setup.py from another directory.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# http://bugs.python.org/issue15881#msg170215
try:
    import multiprocessing
except ImportError:
    pass

version = '2.0.0.dev3'

setup(
    name='juniper',
    version=version,
    url='http://cyaninc.com',
    license='CYAN',
    author='Cyan',
    author_email='support@cyaninc.com',
    description='Juniper EA',
    long_description="""\
Juniper Rest based Adapter""",
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
        'cymlrest',
        'bpeamodels',
        'easdk',
        ],
    entry_points={
        'console_scripts': [
            'juniper = juniper.main:main',
            ]
        },
    tests_require=[
        'mock',
        'nose',
        ],
    test_suite='nose.collector',
)
