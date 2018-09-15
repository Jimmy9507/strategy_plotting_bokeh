# Copyright 2015 Ricequant All Rights Reserved
from setuptools import setup, find_packages


def readfile(filename):
    with open(filename, mode="rt") as f:
        return f.read()

setup(
    name='strategy_ploting',
    version='0.1.9',
    url="https://www.ricequant.com/",
    packages=find_packages(),
    author="Ricequant",
    install_requires=readfile("requirements.txt"),
    package_data={'strategy_ploting': ['*.yaml']},
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    description="anaysis"
)
