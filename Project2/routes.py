# -*- coding: utf-8 -*-
"""
Created on Thu Nov 11 01:22:59 2021

@author: garvi
"""

#File imports
from Project2 import app
from Project2 import util
from Project2 import macros

#Library imports
import os
from flask import render_template, flash, request
from google.cloud import storage
import requests 

@app.route("/")
@app.route("/home")
def homepage():
    if (macros.first_load == True):
        flash('Welcome back!')
        macros.first_load = False
    return render_template("index.html", title="NPM-Registry Group 19")

@app.route("/docs")
def docs():
    return render_template("index.html", title="docs page")


@app.route("/upload", methods=['POST', 'GET'])
def upload():
    '''
    Code borrowed from google-docs.
        https://cloud.google.com/appengine/docs/flexible/python/using-cloud-storage
    '''
    if request.method ==  "POST":
                
        f = request.files['file']
        
        if not f:
            return 'No file uploaded.', 400
        
        name = request.form.get('name')

        if not name:
            return 'No Name mentioned', 400

        version = request.form.get('version')
        
        if not version:
            return 'No Version mentioned', 400
        
        
        # Lazy-load the libraries.
        import base64
        
        data = f.read()
        requestUrl = "https://purde-final-project.appspot.com/package"
        
        encoded = base64.b64encode(data)
        s_encoded = str(encoded)[2:]
        
        requestBody = {
          "metadata": {
            "Name": name,
            "Version": version,
            "ID": "69"
          },
          "data": {
            "Content": s_encoded,
            "JSProgram": "",
            "URL": ""
          }
        }
        requestHeaders = {
          "Content-Type": "application/json",
          "Accept": "application/json"
        }
        
        r = requests.post(requestUrl, headers=requestHeaders, json=requestBody)
        
        if (r.status_code == 201):
            flash("File added to the Cloud.")
    else:
        print ("wtf")
        
    return render_template("index.html", title="docs page")

@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/view")
def view():
    import requests

    requestUrl = "https://purde-final-project.appspot.com/packages"
    requestHeaders = {
      "Accept": "application/json"
    }
    
    response = requests.post(requestUrl, headers=requestHeaders)

    names_array = []
    id_array = []
    size_array = []
    
    
    print ("BELOW is repsonse..")
    print (response.json())
    
    if (response.json() == ['No such page exists']):
        return render_template("view.html", result=zip(['Nothing here bud'], ['N/A'], ['0']))        
    
    for item in (response.json()):
        names_array.append(item['name'].partition(':')[0])
        id_array.append(item['id'])
        size_array.append(item['size'])
        
    return render_template("view.html", result=zip(names_array, id_array, size_array))


@app.route("/ui1")
def show_ui():
    return render_template("ui.html")        
