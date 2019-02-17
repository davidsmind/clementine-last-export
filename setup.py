#!/usr/bin/python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name='clementine_last_export',
      version='0.5',
      description='Tool to import playcounts and loved tracks from your last.fm account into Clementine',
      author='David Mattatall',
      author_email='davidsmind@gmail.com',
      url='https://github.com/davidsmind/clementine-last-export',
      scripts=['bin/clementine_last_export'],
      packages=['clementine_last_export'],
      package_data={'clementine_last_export': ['*.png']},
      )
