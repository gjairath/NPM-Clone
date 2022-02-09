# -*- coding: utf-8 -*-
"""
Created on Thu Nov 11 01:24:05 2021

@author: garvi
"""

#Libraries
import os
from dotenv import load_dotenv
load_dotenv()

#Packages
from Project2 import app

flask_app = app.app

if __name__ == '__main__':
    app.add_api('swagger.yaml')
    app.run()
