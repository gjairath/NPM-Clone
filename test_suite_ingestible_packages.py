# -*- coding: utf-8 -*-
"""
Created on Mon Dec 13 15:46:11 2021

@author: garvi
"""


urls = ['https://github.com/expressjs/express',
        'https://github.com/lquixada/cross-fetch',
        'https://github.com/debug-js/debug',
        'https://github.com/inversify/InversifyJS',
        'https://github.com/prettier/prettier']


import requests
import base64
import pygit2
import os

import shutil

def reset():
  requestUrl = "https://purde-final-project.appspot.com/reset"
  requestHeaders = {
    "X-Authorization": "gdsgds",
    "Accept": "application/json"
  }
  
  print ("Resetting.")
  request = requests.delete(requestUrl, headers=requestHeaders)


def test_put_url(url, name):
  print ("\n@{}".format(url))
 
  requestUrl = "https://purde-final-project.appspot.com/package/462"
  
  requestBody = {
    "metadata": {
      "Name": name,
      "Version": "1.2.3",
      "ID": "462"
    },
    "data": {
      "JSProgram": "",
      "URL": url
    }
  }
  requestHeaders = {
    "Content-Type": "application/json",
    "Accept": "application/json"
  }

    # This request posts the package.
  f = requests.put(requestUrl, headers=requestHeaders, json=requestBody)
  
  print (f.content)


if __name__ == "__main__":
   #  test_get_package_true()
#    print ("\nTesting Post with ingestible packages...")
    # reset()
    # names = "Hello"
    # for url in urls:
    #     test_post_package_valid_url(url, names)
    #     names += "1"
        
    # get_pages_empty()
    
    # Test put by URL test put by Content
    # Test put wit invalid.
    
    test_put_url(urls[2], "Hello1111")
      