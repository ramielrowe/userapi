#!/usr/bin/env python

from setuptools import setup, find_packages


setup(name='userapi',
      version='0.0.1',
      description="userapi",
      author='Andrew Melton',
      author_email='ramielrowe@gmail.com',
      packages=find_packages(),
      entry_points={
           'console_scripts': [
               'userapi-db = userapi.db.cli:main'
           ],
       })
