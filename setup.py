# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme_ = f.read()

with open('LICENSE') as f:
    license_ = f.read()

setup(
    name='pycaro',
    version='0.0.1',
    description='Validate variables',
    long_description=readme_,
    author='@anteverse',
    url='https://github.com/anteverse/pycaro',
    license=license_,
    packages=find_packages(exclude=('tests', 'docs')),
    python_requires=">=3.6",
    install_requires=["click"],
    scripts=["bin/pycaro"],
)
