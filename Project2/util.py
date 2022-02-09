# -*- coding: utf-8 -*-
"""
Created on Sat Nov 13 22:55:09 2021

@author: garvi
"""

#Library imports
from google.cloud import storage


def implicit():
    '''
    Borrowed from google-docs,
    Ensure the implicit auth works.
    
    Returns, none.
    '''
    # If you don't specify credentials when constructing the client, the
    # client library will look for credentials in the environment.
    storage_client = storage.Client()

    # Make an authenticated API request
    buckets = list(storage_client.list_buckets())
    print(buckets)
