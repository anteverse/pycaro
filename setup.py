# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    packages=find_packages(exclude=("tests", "docs")),
    scripts=["bin/pycaro"],
)
