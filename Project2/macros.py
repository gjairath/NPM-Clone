# -*- coding: utf-8 -*-
"""
Created on Sat Nov 13 23:04:33 2021

@author: garvi
"""

'''
    This file has all the config variables at the top level.
'''

#Library imports
import os




CLOUD_STORAGE_BUCKET = os.getenv('CLOUD_STORAGE_BUCKET')

first_load = True