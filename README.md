# project-2-project-2-19
<h1>Table of contents</h1>


| Item | Description | Location |
|------|-------------|----------|
| ADA compatible frontend | Source code for the ADA compliant website for the NPM registry, all files call the back-end.       | Project2/ |
| SQL server          | Source code for setting up the Backend of the registry; Check controller/ for core-logic.             | swagger_server/ |
| Main app files          | code for main.py, configuration files, test files.       | / |

<h1>Features</h1>
<br>
This project is a NPM-registry with authentication. <br>

<br>
The registry supports the following operations:<br>
    GET requests:
    
1. Getting package history when package is requested by name. 
2. Getting package by package id. 
3. Rating uploaded packages on Ramp-up time, correctness, bus factor, maintainer responsivity, license compatibility, dependency pinning. 

POST requests:

1. Creating/uploading a new package
2. Ingestion of public npm packages when package is posted with URL field but without content field.
4. Ingestion of packages with at least a 0.5 rating on all relevant metrics. 
5. Gets paginated list of all packages currently in the registry

PUT requests:
1. Update the version of a package already in the registry using its name, id, and version.

DELETE requests:
1. Deleting a particular version of a package
2. Deleting all versions of a package
3. Resetting the entire registry to its default state.

The registry uses Google App Engine, Google Compute Engine, and a MySQL Database while exposing a single api instance to users. 

The webpage is ADA compliant as verified by axeDev automated accessibility checks.  

Trustworthy Modules Registry by Group 19.

<h1>Access to registry</h1>
The link to access the registry is:

    https://purde-final-project.appspot.com
    
<h1>Website guide</h1>
Use the link given above to access an instance of and send requests to our registry through our API. 


The webpage also has a view tab to view packages currently stored in the registry,
along with an endpoints tab to provide information for requests to the API.

These pages can be accessed by adding the following path relative to the home link given above:
    
    View: /view
    Endpoints: /ui1

The packages should be zipped before uploading. 

When using requests to upload/create a package, ensure that the content field is encoded in base64/the URL points to 
a public repository. 

<h1>Tests</h1>
Use the following command to run our test suite:

python test_suite.py

If the suite fails, consider running pip install -r requirements.txt or activating the venv p2env.
