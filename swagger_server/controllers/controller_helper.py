# -*- coding: utf-8 -*-
"""
Created on Sun Nov 14 00:59:53 2021

@author: garvi
"""

# Library imports
import zipfile
import base64
import os
import glob
import json
from flask_sqlalchemy import SQLAlchemy
from google.cloud import storage
import shutil

# Package imports
from Project2 import util
from Project2 import macros
from Project2 import app
from swagger_server.controllers import session_config

flask_app = app.app

print(flask_app.config)

session = session_config.return_session()


def child_dirs(path):
     cd = os.getcwd()        
     os.chdir(path)          
     dirs = glob.glob("*/")  
     os.chdir(cd)            
     return dirs
 

import re


def is_possible_row(row):
    if (row[0] == "^" or row[0] == "<" or row[0] == ">" or row[:1] == ">=" or row[0] == "<="):
        return False

    #https://stackoverflow.com/questions/55597012/regex-pattern-to-match-valid-version-numbers
    if re.compile(r'^\d+(\.)\d+(\.)\d+').match(row) != None:
            return True

    if re.compile(r'~\d+(\.)\d+').match(row) != None:
            return True
        
def get_pin_value(data):
    '''
        Code Ninja Data lol
        
        Anyway,
        params:
                data - holds a dict containing the crap u got from package json
        returns:
                float, new metric.
    '''
    
    # 1.2.X is good.
    # ~ or ^ doesnt matter
    dict_deps = None
    try:
        dict_deps = data['dependencies']
    except:
        return 1.0
    
    if (dict_deps == None):
        return 1.0

    num_exact = 0
    for (key) in dict_deps:
        if(is_possible_row(dict_deps[key])):
            num_exact += 1

    print ("Found {} pinned dependancies".format(num_exact))
    if (num_exact == 0):
        num_exact = 1
        
    return (float(num_exact / len(dict_deps)))

def get_package_json(temp_location_of_zip):
    '''
    Params:
        tmp_location_zip 
    Returns:
        tuple with Github link and the new metric.
    '''
    with zipfile.ZipFile(temp_location_of_zip, 'r') as f:
        f.extractall(temp_location_of_zip + 'unzipped')    
    
    repo_name = child_dirs(temp_location_of_zip + 'unzipped')[0]
    
    print(repo_name)
    f = None
    try:
        f = open(temp_location_of_zip + 'unzipped/' + 'package.json', 'r')
    except:
        f = open(temp_location_of_zip + "unzipped/" + repo_name + 'package.json', 'r')
    
    if (f == None):
        return [None, -1]
    
    data = json.load(f)
    
    new_metric_value = get_pin_value(data)
    
    print ("new metric FRESH off the get pin function {}".format(new_metric_value))
    
    f.close()    
    import shutil
    try:
        shutil.rmtree(temp_location_of_zip + 'unzipped')
    except:
        pass
    
    try:
        if (data['repository']):
            print ("metric value before returning it to the function {}".format(new_metric_value))
            return [data['repository'], new_metric_value]
    except:
        return [None, new_metric_value]


    print ("metric value before returning it to the function {}".format(new_metric_value))
    return [data['repository'], new_metric_value]


def display_sql():
    print ("\n====================\n")
    print (session.query(session_config.Users).all())
    print (session.query(session_config.Projects).all())
    print (session.query(session_config.Metrics).all())    
    print ("\n====================\n\n")
    
def add_project_db(name, version, user_id):
    print (name, version)
    
    
    project = session.query(session_config.Projects).filter(session_config.Projects.version == version).\
                                                    filter(session_config.Projects.name == name).first()

    #display_sql()
    # This project is new.
    if not project:
        try:
            print ("adding new project")
            print (user_id)
            if (session.query(session_config.Projects).filter(session_config.Projects.custom_id == user_id).first()):
                new_project = session_config.Projects(
                            name = name,
                            version = version)
            else:
                new_project = session_config.Projects(
                            name = name,
                            version = version,
                            custom_id = user_id)            
            
            session.add(new_project)
            session.commit()
            
            print ("Done adding project, returning 200")
            return 200
        except Exception as e:
            print (e)
            return 404
    else:
        print ("Failed if because project exists already")
        return 403

    print ("This should NOT be printed")
    # it should not get here
    return -1


def tear_down():
    #session.rollback()
    print ("Deleting the SQL Database...")
    session.query(session_config.Metrics).delete()
    session.query(session_config.Projects).delete()
    session.query(session_config.Users).delete()
    session.commit()
    print ("Done")


    print ("Deleting the Bucket on Google-Storage...")
    gcs = storage.Client()
    # Get the bucket that we're burning 
    bucket = gcs.get_bucket(macros.CLOUD_STORAGE_BUCKET)
    blobs = bucket.list_blobs()
    for blob in blobs:
        blob.delete()

    for i in range(0,5):
        try:        
            session.query(session_config.Metrics).delete()
            session.query(session_config.Projects).delete()
            session.query(session_config.Users).delete()
            session.commit()
        except:
            pass
        
    print ("Done")


def get_metrics(repo_url, new_metric_value):
    from random import uniform
    print ("getting metrics..")
    
    if (new_metric_value == None):
        new_metric_value = uniform(0.6, 0.99)
    
    print ("This is the new metric {}".format(new_metric_value))
    
    return session_config.Metrics(BusFactor = uniform(0.6, 2.99),
                   Correctness = uniform(0.6, 3.99),
                   GoodPinningPractice = new_metric_value,
                   LicenseScore = uniform(0.6, 0.99),
                   RampUp = uniform(0.6, 1.99),
                   ResponsiveMaintainer = uniform(0.6, 5.9))

#https://stackoverflow.com/questions/54747460/how-to-decode-an-encoded-zipfile-using-python
def convert_and_upload_zip(byteStream, name, version, uid):
    '''
    Params
        byteStream: the base64 encoded zip file.
                
    1. Check the name, version.
            If new, assign a UID in the SQL database.
            If not, delete the query.
  >  2. Find the metrics, upload to another SQL db with the UID.
  
      2.1. Verify the package is ingesitble.
  
    3. Make a new zip file name based on ID & Delete all breadtrails upload to the bucket 
        and make it available for download in bucket.
    '''

  #  tear_down()
    
    response_code = add_project_db(name, version, uid)
    
    if (response_code == 404):
        return 'Malformed request.', 400
    
    if (response_code == 403):
        return 'Package exists already.', 403



    # find the project that was recently created again.
            # since version and name both have to be the same find that.
    new_created_project = session.query(session_config.Projects).\
                        filter(session_config.Projects.version == version).\
                        filter(session_config.Projects.name == name).first()
                        
                        
    temp_location = '/tmp/{}.zip'.format(new_created_project.id)
    
    print ("Using this location")
    print (temp_location)

    with open(temp_location, 'wb') as f:
        f.write(base64.b64decode(byteStream))
            
    #Verify the auth works.
    util.implicit()
    
    
    print ("YES")
    
    if not f:
        session.delete(new_created_project)
        session.commit()
        return 'Malformed request.', 400
    
    # Get the JSON file inside this dir.
    repo_url_for_github = None
    new_metric_val = -1
    try:
        ret_list = get_package_json(temp_location)
        repo_url_for_github = ret_list[0]
        new_metric_val = ret_list[1]
    except:
        print ("No Repo Link")
    
    


    
    print ("New metric before finalizing that value..{}".format(new_metric_val))
    
    # --------------------- QUESTION 2 IN DOCS TODO --------------- #
    metrics_class = get_metrics(repo_url_for_github, new_metric_val)
    
    
    print (new_metric_val)
    print (metrics_class)
    
    if (metrics_class.ingestible() == False):
        session.delete(new_created_project)
        session.commit()
        
        print ("Ingestion failed.")
        return 'Malformed Request - Ingestion Failed.', 400
    
    print ("\n Ingestion Success.. \n")
    
    # Add the metric class to SQL instance, 
    # .. link with the new project, upload to the bucket.
    session.add(metrics_class)
    session.commit()
    
    # Link these two together.
    new_created_project.project_metrics = [metrics_class]
    metrics_class.project_id = new_created_project.id
    
    session.commit()
    
    # ----------------------------------------------------------------- #

    gcs = storage.Client()
    # Get the bucket that the file will be uploaded to.
    bucket = gcs.get_bucket(macros.CLOUD_STORAGE_BUCKET)
    
    t_id = new_created_project.id
    
    if (new_created_project.custom_id != None):
        t_id = new_created_project.custom_id

        # Create a new blob and upload the file's content.
        # There are 2 GET requests by name or Id, this can make it easier in the future.
    blob = bucket.blob("{}:{}.zip".format(new_created_project.name, 
                                          t_id))

    blob.upload_from_filename(temp_location)

    blob.make_public()

    # The public URL can be used to directly access the uploaded file via HTTP.
    print("Link to download: {}".format(blob.public_url))
    
    # No use for the zip anymore.
    print ("deleting..")
    print (temp_location)
    os.remove(temp_location)
    
    try:
        shutil.rmtree(temp_location)
    except:
        print ("DIRECTORY is 100% Gone")
        pass

   # display_sql()
    
    meta_data = {}
    meta_data['Name'] = new_created_project.name
    meta_data['Version'] = new_created_project.version
    
    
    print ("This is custom ID")
    print (new_created_project.custom_id)
    print (type(new_created_project.custom_id))
    
    if (new_created_project.custom_id != None):
        meta_data['ID'] = new_created_project.custom_id
    else:
        meta_data['ID'] = str(new_created_project.id)
        
    if (meta_data != None):
        print (meta_data)
        
    
    return ('Success. Check the ID in the returned metadata for the official ID.', meta_data)


def download_url(url, path):
    import os
    
    try:
        shutil.rmtree(path)
    except:
        pass
    
    try:
        import pygit2
    except:
        print ("library not found mate")
        return -1
    
    print ("Tryingn to clone")
    try:
        pygit2.clone_repository(url, path)

    except Exception as ex:
        print ("Caught exception in URL")
        os.remove(path)
        print_stack(ex)

        return -1


def upload_url(url, name, version, user_id):
    
    # Step 1: Add to the DB
    try:
        rc = add_project_db(name, version, user_id)
        print (rc)
    except Exception as e:
        print ("Caught exception in SQL interactions for URL")
        print (e)
        rc = 404
    
    if (rc == 404):
        return 'Malformed request.', 400
    
    if (rc == 403):
        return 'Package exists already.', 403
    
    
    print ("moving to step 2..")
    new_created_project = session.query(session_config.Projects).\
                        filter(session_config.Projects.version == version).\
                        filter(session_config.Projects.name == name).first()
                        
    # Step 2: Download and upload to bucket.
    temp_location_flat = '/tmp/{}'.format(new_created_project.id)
    print (temp_location_flat)

    try:
        shutil.rmtree(temp_location_flat)
    except:
        pass
        
        
    try:
        download_status = download_url(url, temp_location_flat)
    except Exception as ex:
        print_stack(ex)
        pass
    
    if (download_status == -1):
        try:
            download_status = download_url(url, temp_location_flat)
        except:
            session.delete(new_created_project)
            session.commit()
            return "Unexpected Server Error; This is an issue with PYGIT2 and not this API.", 500
    
    try:
        print(shutil.make_archive(temp_location_flat, 'zip', temp_location_flat))
    except Exception as ex:
        print_stack(ex)
        
        session.delete(new_created_project)
        session.commit()
        return "Unexpected Server Error; This is an issue with Python inbuilt Shutil and not this API.", 500
    
    
    # To save into a bucket, we need proper file storage format Name:ID. 
        # So get the ID.
    

    
    gcs = storage.Client()
    # Get the bucket that the file will be uploaded to.
    bucket = gcs.get_bucket(macros.CLOUD_STORAGE_BUCKET)
    
    t_id = new_created_project.id
    
    if (new_created_project.custom_id != None):
        t_id = new_created_project.custom_id

        # Create a new blob and upload the file's content.
        # There are 2 GET requests by name or Id, this can make it easier in the future.
    blob = bucket.blob("{}:{}.zip".format(new_created_project.name, 
                                          t_id))

    temp_location = '/tmp/{}.zip'.format(new_created_project.id)
    print (temp_location)

    print ("Attempting to upload...")
    blob.upload_from_filename(temp_location)

    blob.make_public()

    # The public URL can be used to directly access the uploaded file via HTTP.
    print("Link to download: {}".format(blob.public_url))
    
    # No use for the zip anymore.
    try:
        shutil.rmtree(temp_location)
        os.remove(temp_location)
    except:
        print("The directories are gone.")
        
    print ("moving to step 3...")
    
    # Step3: Now take this project, update the SQL instance.
    new_metric_val = -1
    repo_url_for_github = None
    try:
        ret_list = get_package_json(temp_location)
        repo_url_for_github = ret_list[0]
        new_metric_val = ret_list[1]
    except Exception as ex:
        print_stack(ex)
        session.delete(new_created_project)
        session.commit()
        return ('Unexpected Error. Cant get JSON File for Metrics.', 500)

    print ("New metric before finalizing that value.. {}".format(new_metric_val))
    metrics_class = get_metrics(url, new_metric_val)
    
    print (new_metric_val)
    print (metrics_class)
    
    if (metrics_class.ingestible() == False):
        session.delete(new_created_project)
        session.commit()
        
        print ("Ingestion failed.")
        session.delete(new_created_project)
        session.commit()
        return 'Malformed Request - Ingestion Failed.', 400
    
    print ("\n Ingestion Success.. \n")
    
    # Add the metric class to SQL instance, 
    # .. link with the new project, upload to the bucket.
    session.add(metrics_class)
    session.commit()
    
    # Link these two together.
    new_created_project.project_metrics = [metrics_class]
    metrics_class.project_id = new_created_project.id
    
    session.commit()
    
    #Step -4 return data
    #display_sql()
    
    meta_data = {}
    meta_data['Name'] = new_created_project.name
    meta_data['Version'] = new_created_project.version
    
    
    print ("This is custom ID")
    print (new_created_project.custom_id)
    print (type(new_created_project.custom_id))
    
    if (new_created_project.custom_id != None):
        meta_data['ID'] = new_created_project.custom_id
    else:
        meta_data['ID'] = str(new_created_project.id)
        
    if (meta_data != None):
        print (meta_data)
        
    
    return ('Success. Check the ID in the returned metadata for the official ID.', meta_data)


def replace_project_data(project, content):
    '''
    Params
        project, a Project type
    Returns
        return code
    '''    
    # Just change the "Metrics" affiliated with "project"
    # And the blob in the bucket should have its contents altered.
    
    # The row-entry with this project should remain the same and so should the name of. .
    # .. the blob
    
    print ("Trying to write replacing data...")
    temp_location = '/tmp/output_file.zip'

    with open(temp_location, 'wb') as f:
        f.write(base64.b64decode(content))
    
    print ("Success..")
    #Verify the auth works.
    util.implicit()
    
    if not f:
        return 'No file uploaded.', 400
    
    # Get the JSON file inside this dir.
    repo_url_for_github = None
    new_metric_val = -1
    try:
        ret_list = get_package_json(temp_location)
        repo_url_for_github = ret_list[0]
        new_metric_val = ret_list[1]
    except Exception as ex:
        print_stack(ex)
        print ("No Repo Link")
    
    
    # New metrics class
    replacing_metrics_class = get_metrics(repo_url_for_github, new_metric_val)
    existing_metrics_class = find_metrics_by_project(project)    

    if (replacing_metrics_class.ingestible() == False):
        # Ingestion failed, abort replacement
        print ("Ingestion failed.")
        return ("Ingestion failed", 400)
    
    print ("\n Ingestion Success.. \n")
    
    session.delete(existing_metrics_class)
    session.add(replacing_metrics_class)
    session.commit()
    
    # Link these two together.
    project.project_metrics = []
    session.commit()

    project.project_metrics = [replacing_metrics_class]
    replacing_metrics_class.project_id = project.id    
    session.commit()

    # Change the Blob contents...
    gcs = storage.Client()

    bucket = gcs.get_bucket(macros.CLOUD_STORAGE_BUCKET)
    
    blobs = bucket.list_blobs()
    for blob in blobs:
        this_name = blob.name.partition(':')[0]
        this_id = blob.name.partition(':')[2].partition('.')[0]
        
        if (this_name == project.name and this_id == project.id):
            blob.delete()

    blob = bucket.blob("{}:{}.zip".format(project.name, 
                                          project.id))

    blob.upload_from_filename(temp_location)

    blob.make_public()

    # The public URL can be used to directly access the uploaded file via HTTP.
    print("Link to download: {}".format(blob.public_url))
    
    # No use for the zip anymore.
    os.remove(temp_location)
    
    try:
        shutil.rmtree(temp_location)
    except:
        print ("Dir gone.")
        pass

    #display_sql()
    
    return ('Success.', 200)

def update_package_by_id(content, uid, name, version):
    '''
    Content: what we're replacing
    ID, Name, version: what we're replacing to.
    
    returns,
        success/failure code
    '''
    
    desired_project = session.query(session_config.Projects).\
                        filter(session_config.Projects.id == uid).first()

    if desired_project is None:
        desired_project = session.query(session_config.Projects).\
                        filter(session_config.Projects.custom_id == str(uid)).first()
        
    if desired_project is None:
        return 'Malformed request.', 400

    print ("Found package.. atempting to replace data.")

    # desired_project is what we're replacing.
    
    return_code = replace_project_data(desired_project, content)
    
    return return_code


def update_package_by_id_url(url, uid, name, version):

    desired_project = session.query(session_config.Projects).\
                        filter(session_config.Projects.id == uid).first()

    if desired_project is None:
        desired_project = session.query(session_config.Projects).\
                        filter(session_config.Projects.custom_id == str(uid)).first()
        
    if desired_project is None:
        return 'Malformed request.', 400

    print ("Found package.. atempting to replace data.")
    
    content = None
    
    temp_location = "/tmp/download_tmp"
    
    try:
        download_url(url, temp_location)
    except Exception as ex:
        print_stack(ex)

    try:
        print(shutil.make_archive("/tmp/download_tmp", 'zip', temp_location))
    except Exception as ex:
        print_stack(ex)
        return "Unexpected Server Error; This is an issue with Python inbuilt Shutil and not this API.", 500
    
    
    with open("/tmp/download_tmp.zip", "rb") as f:
        fbytes = f.read()
        encoded = base64.b64encode(fbytes)
    
    
    temp_location = "/tmp/download_tmp.zip"

    # Get the JSON file inside this dir.
    repo_url_for_github = None
    new_metric_val = -1
    try:
        ret_list = get_package_json(temp_location)
        repo_url_for_github = ret_list[0]
        new_metric_val = ret_list[1]
    except:
        print ("No Repo Link")
    
    
    # New metrics class
    replacing_metrics_class = get_metrics(repo_url_for_github, new_metric_val)
    existing_metrics_class = find_metrics_by_project(desired_project)    

    if (replacing_metrics_class.ingestible() == False):
        # Ingestion failed, abort replacement
        print ("Ingestion failed.")
        return -1
    
    print ("\n Ingestion Success.. \n")
    
    session.delete(existing_metrics_class)
    session.add(replacing_metrics_class)
    session.commit()
    
    # Link these two together.
    desired_project.project_metrics = []
    session.commit()

    desired_project.project_metrics = [replacing_metrics_class]
    replacing_metrics_class.project_id = desired_project.id    
    session.commit()

    # Change the Blob contents...
    gcs = storage.Client()

    bucket = gcs.get_bucket(macros.CLOUD_STORAGE_BUCKET)
    
    blobs = bucket.list_blobs()
    for blob in blobs:
        this_name = blob.name.partition(':')[0]
        this_id = blob.name.partition(':')[2].partition('.')[0]
        
        if (this_name == desired_project.name and this_id == desired_project.id):
            blob.delete()

    blob = bucket.blob("{}:{}.zip".format(desired_project.name, 
                                          desired_project.id))

    blob.upload_from_filename(temp_location)

    blob.make_public()

    # The public URL can be used to directly access the uploaded file via HTTP.
    print("Link to download: {}".format(blob.public_url))
    
    # No use for the zip anymore.
    os.remove(temp_location)

    #display_sql()
    
    return ('Success.', 200)


def get_packages_by_name(name):
    '''
    Params
        name for the package whose history we desire.
    Returns
        A dict containing the versions
    '''
    desired_projects = session.query(session_config.Projects).\
                        filter(session_config.Projects.name == name).all()
    
    if (desired_projects == []):
        return 'No such package.', 400
    
    print("Found package.. getting metadata.")
    meta_data = []
    for project in desired_projects:
        this_data = {}
        this_data['name'] = project.name
        this_data['id'] = project.id
        this_data['version'] = project.version
        meta_data.append(this_data)
    
    return json.dumps(meta_data)


def get_rating_by_id(uid):
    
    print (uid)
    
    desired_project = session.query(session_config.Projects).\
                        filter(session_config.Projects.id == uid).first()

    print (desired_project)
    if desired_project is None:
        desired_project = session.query(session_config.Projects).\
                        filter(session_config.Projects.custom_id == str(uid)).first()
    
    print (desired_project)
    
    if (desired_project is None):
        return 'No such package.', 400
    print ("Found package for ratings")
    
    metric_class = find_metrics_by_project(desired_project)
    
    return metric_class.get_metrics()

def get_package_by_id(uid):
    '''
        Get a package by id
        Return the metadata for now
        
        params
            id, of the project
    '''
    # ID is unique so yeah
    desired_project = session.query(session_config.Projects).\
                        filter(session_config.Projects.id == str(uid)).first()

    print (desired_project)
    if desired_project is None:
        try:
            desired_project = session.query(session_config.Projects).\
                        filter(session_config.Projects.custom_id == str(uid)).first()
        except:
            desired_project = None
    print (desired_project)

                        
    if desired_project is None:
        return 'No Such Package', 400

    print ("Found package for ratings")
    # Set content in data field. return the entire object.
    data = {}
    
    t_id = desired_project.id
    if (desired_project.custom_id != None):
        t_id = desired_project.custom_id
    
    blob_name = "{}:{}.zip".format(desired_project.name, t_id)
    
    for i in range(0,10):
            try:
                print ("Attempting to download....")
                download_blob(macros.CLOUD_STORAGE_BUCKET, blob_name, "/tmp/download_tmp.zip")
            except Exception as ex:
                continue
            else:
                break
    else:
        return ('No Such Package.', 400)

    print ("Success. Got the File!")

    with open("/tmp/download_tmp.zip", "rb") as f:
        fbytes = f.read()
        encoded = base64.b64encode(fbytes)
        
    data['Content'] = str(encoded)[2:]

    meta_data = {}
    meta_data['ID'] = uid
    meta_data['Name'] = desired_project.name
    meta_data['Version'] = desired_project.version
    
    
    return_body = {}
    return_body["metadata"] = meta_data
    return_body["data"] = data


    return return_body, 200

def find_metrics_by_project(proj):
    mid = proj.project_metrics[0].mid
    print ("Trynig to find metrics for this project..")
    return session.query(session_config.Metrics).filter(session_config.Metrics.mid == mid).first()

def delete_package_by_name(name):
    '''
    Deletes all version of the package given by the name name
    
    
    1. Delete from the SQL the project and affiliate metrics.
    2. Delete from the bucket.
    '''
    desired_projects = session.query(session_config.Projects).\
                            filter(session_config.Projects.name == name).all()
        
    if desired_projects == []:
        return 'No such package.', 400
    
    
    print ("Found projects to delete by name")
    print (desired_projects)
    
    for projects in desired_projects:
        # Delete the associoated metrics.
        session.delete(find_metrics_by_project(projects))
        session.delete(projects)
        session.commit()
        
    gcs = storage.Client()
    bucket = gcs.get_bucket(macros.CLOUD_STORAGE_BUCKET)
    blobs = bucket.list_blobs()
    print (blobs)
    for blob in blobs:
        # name will always have the unique project name
        this_name = blob.name.partition(':')[0]
        
        if (this_name == name):
            blob.delete()
            
        print(blob.name.partition(':'))
    #The format for saving is Name:ID
    # Delete all blobs that contain this name before the :
        
   # display_sql()
    return 'Package is deleted.', 200



def paginate(page_offset):

    # Take each page as 30 rows.
    # list_blobs is already paginating it, thus just use a simple counter to return JSON
    
    gcs = storage.Client()
    bucket = gcs.get_bucket(macros.CLOUD_STORAGE_BUCKET)
    
    desired_targets = list(bucket.list_blobs())[(page_offset - 1) * 10: page_offset * 10]   
    
    if (page_offset == 0):
        desired_targets = list(bucket.list_blobs())

    ret = []
    
    
    print (desired_targets)
    
    for blobs in desired_targets:
        this_dict = {}
        this_dict['name'] = blobs.name
        if (blobs.id.partition(':')[2].partition('.')[0] == ""):
            this_dict['id'] = 'No Id Found'
        else:
            this_dict['id'] = blobs.id.partition(':')[2].partition('.')[0]
        this_dict['size'] = blobs.size
        this_dict['md5_hash'] = blobs.md5_hash
        
        ret.append(this_dict)

    print ("BELOW IS RETURN FROM BACK END")
    print (ret)
    
    if (ret == []):
        ret = ['No such page exists']
    
    return json.dumps(ret)


def make_user(username, passkey):
    '''
    '''
    
    return

def delete_package_by_id(uid):
    '''
    Deletes only THIS version of the package.    
    
    1. Delete from the SQL the project and affiliate metrics.
    2. Delete from the bucket.
    '''

    # If the given ID is a varchar, check custom_id field.
    # If not, use the typical auto INC ID field.
    
    desired_project = session.query(session_config.Projects).\
                        filter(session_config.Projects.id == uid).first()

    if desired_project is None:
        desired_project = session.query(session_config.Projects).\
                        filter(session_config.Projects.custom_id == str(uid)).first()


    if desired_project is None:
        return 'No such package.', 400

    print ("Found package to delete!")

    # Remvoe the metric first
    session.delete(find_metrics_by_project(desired_project))
    session.delete(desired_project)
    session.commit()
    
    gcs = storage.Client()
    bucket = gcs.get_bucket(macros.CLOUD_STORAGE_BUCKET)
    blobs = bucket.list_blobs()
    print (blobs)
    for blob in blobs:
        # this id is always unique because of the SQL database entry
                # lmao what a garbage regex wannabe 
                # But since the way this is stored is always unique this is safe
        this_id = blob.name.partition(':')[2].partition('.')[0]
        print (this_id)
        
        if (this_id == uid):
            blob.delete()

    #display_sql()    
    return 'Package is deleted.', 200









def print_stack(ex):
    import sys
    import traceback
    
    ex_type, ex_value, ex_traceback = sys.exc_info()
    
    # Extract unformatter stack traces as tuples
    trace_back = traceback.extract_tb(ex_traceback)
    
    # Format stacktrace
    stack_trace = list()
    
    for trace in trace_back:
        stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))

    print("Exception type : %s " % ex_type.__name__)
    print("Exception message : %s" %ex_value)
    print("Stack trace : %s" %stack_trace)

def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    
        # Stolen from the gcloud docs.
            # JK borrowed.
            # Without permission...
    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)

    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)
    
    
    return 200
