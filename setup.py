#!/usr/bin/python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name='clementine-last-export',
      version='0.1',
      description='Tool to import playcounts and loved tracks from your last.fm account into Clementine',
      author='Vincent Verdeil',
      author_email='vincent.verdeil@gmail.com',
      url='http://code.google.com/p/clementine-last-export/',
      packages=['clementine-last-export'],
      package_data={'clementine-last-export': ['*.png']},
      )
