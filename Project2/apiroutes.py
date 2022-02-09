# -*- coding: utf-8 -*-
"""
Created on Thu Dec  2 02:12:38 2021

@author: garvi
"""


'''

This file is a bridge between the auto-generated server stubs and the existing front-end 
.. impl.

'''

# Files
from Project2 import app
from swagger_server.models.authentication_request import AuthenticationRequest  # noqa: E501
from swagger_server.models.authentication_token import AuthenticationToken  # noqa: E501
from swagger_server.models.enumerate_offset import EnumerateOffset  # noqa: E501
from swagger_server.models.error import Error  # noqa: E501
from swagger_server.models.package import Package  # noqa: E501
from swagger_server.models.package_history_entry import PackageHistoryEntry  # noqa: E501
from swagger_server.models.package_id import PackageID  # noqa: E501
from swagger_server.models.package_metadata import PackageMetadata  # noqa: E501
from swagger_server.models.package_name import PackageName  # noqa: E501
from swagger_server.models.package_query import PackageQuery  # noqa: E501
from swagger_server.models.package_rating import PackageRating  # noqa: E501
from swagger_server import util

from swagger_server.controllers import controller_helper

# Libraries
import connexion

@app.route("/authenticate", methods=['PUT'])
def create_auth_token():
    return 'This system does not support authentication.', 501


@app.route("/package", methods=['POST'])
def package_create(body=None, x_authorization=None):  # noqa: 

    if connexion.request.is_json:
            body = connexion.request.get_json()  # noqa: E501
            
    print ("Checking if body is none..")
    response = None
    try:
        if (body == None):
            print ("BODY NULL")
            print (body)
            return "Malformed Request.", 400
    except:
        return "Malformed Request.", 400

    print ("Going into the first try block..")

    try:    
        if (body["data"]["Content"] != None):
            if (body["data"]["Content"] != ""):
                response = controller_helper.convert_and_upload_zip(body["data"]["Content"], 
                                                                    body["metadata"]["Name"],
                                                                    body["metadata"]["Version"],
                                                                    body["metadata"]["ID"])
    except Exception as ex:
        print ("Caught exception in Content [Can be false alarm, checking URL]")
        import sys
        import traceback

        ex_type, ex_value, ex_traceback = sys.exc_info()
    
        # Extract unformatter stack traces as tuples
        trace_back = traceback.extract_tb(ex_traceback)
    
        # Format stacktrace
        stack_trace = list()
    
        for trace in trace_back:
            stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))

        print (response)
        print(ex)
        print("Exception type : %s " % ex_type.__name__)
        print("Exception message : %s" %ex_value)
        print("Stack trace : %s" %stack_trace)
        pass
    
    # At this point, if response is still None, it means its the second case.
    
    try:
        if (response == None):
            if (body["data"]["URL"] != "") :
                response = controller_helper.upload_url(body["data"]["URL"],
                                                        body["metadata"]["Name"],
                                                        body["metadata"]["Version"],
                                                        body["metadata"]["ID"])

    except Exception as ex:
        print ("Caught exception in URL")
        import sys
        import traceback

        ex_type, ex_value, ex_traceback = sys.exc_info()
    
        # Extract unformatter stack traces as tuples
        trace_back = traceback.extract_tb(ex_traceback)
    
        # Format stacktrace
        stack_trace = list()
    
        for trace in trace_back:
            stack_trace.append("File : %s , Line : %d, Func.Name : %s, Message : %s" % (trace[0], trace[1], trace[2], trace[3]))

        print (response)
        print(ex)
        print("Exception type : %s " % ex_type.__name__)
        print("Exception message : %s" %ex_value)
        print("Stack trace : %s" %stack_trace)

        return "Malformed Request.", 400


    if (response == None):
        print ("RESPONSE IS NULL")
        print (response)
        return 'Unexpected Error', 500
    
    print (response)
    print (response[1])
    
    if (isinstance(response[1], int)):
        return response[0], response[1]
    
    return response[1], 201



@app.route("/package/<id>", methods=["GET"])
def package_retrieve(id=None, x_authorization=None):  # noqa: E501
    """package_retrieve

    Return this package. # noqa: E501

    :param id: ID of package to fetch
    :type id: dict | bytes
    :param x_authorization: 
    :type x_authorization: dict | bytes

    :rtype: Package
    """
    if connexion.request.is_json:
        id = PackageID.from_dict(connexion.request.get_json())  # noqa: E501
    
    
    ret = controller_helper.get_package_by_id(id)
    return ret[0], ret[1]


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

@app.route("/package/<id>", methods=["PUT"])
def package_update(id=None, body=None, x_authorization=None):  # noqa: E501
    """Update this version of the package.

    The name, version, and ID must match.  The package contents (from PackageData) will replace the previous contents. # noqa: E501

    :param body: 
    :type body: dict | bytes
    :param id: 
    :type id: dict | bytes
    :param x_authorization: 
    :type x_authorization: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = Package.from_dict(connexion.request.get_json())  # noqa: E501    
    
    print ("Going into the first try block..")
    ret = None
    try:    
        if (body.data.content != None):
            if (body.data.content != ""):
                ret = controller_helper.update_package_by_id(body.data.content,
                                                          body.metadata.id,
                                                          body.metadata.name,
                                                          body.metadata.version)
    except Exception as ex:
        print ("Caught exception in Content [Can be false alarm, checking URL]")
        print_stack(ex)
        pass
        
    try:
        if (ret == None):
            if (body.data.url != "") :
                ret = controller_helper.update_package_by_id_url(body.data.url,
                                                          body.metadata.id,
                                                          body.metadata.name,
                                                          body.metadata.version)

    except Exception as ex:
        print ("Caught exception in URL")
        print_stack(ex)
        return "Malformed Request.", 400


    if (ret == None):
        print ("RESPONSE IS NULL")
        return 'Unexpected Error', 500    
    
    return ret[0], ret[1]


@app.route("/package/<id>", methods=["DELETE"])
def package_delete(id, x_authorization=None):  # noqa: E501
    """Delete this version of the package.

     # noqa: E501

    :param id: Package ID
    :type id: dict | bytes
    :param x_authorization: 
    :type x_authorization: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        id = PackageID.from_dict(connexion.request.get_json())  # noqa: E501
    
    
    ret = controller_helper.delete_package_by_id(id)
    return ret

@app.route("/package/<id>/rate", methods=["GET"])
def package_rate(id=None, x_authorization=None):  # noqa: E501
    """package_rate

     # noqa: E501

    :param id: 
    :type id: dict | bytes
    :param x_authorization: 
    :type x_authorization: dict | bytes

    :rtype: PackageRating
    """
    if connexion.request.is_json:
        id = PackageID.from_dict(connexion.request.get_json())  # noqa: E501

    ret = controller_helper.get_rating_by_id(id)

    return ret


@app.route("/package/byName/<name>", methods=["GET"])
def package_by_name_get(name, x_authorization=None):  # noqa: E501
    """package_by_name_get

    Return the history of this package (all versions). # noqa: E501

    :param name: 
    :type name: dict | bytes
    :param x_authorization: 
    :type x_authorization: dict | bytes

    :rtype: List[PackageHistoryEntry]
    """
    if connexion.request.is_json:
        name = PackageName.from_dict(connexion.request.get_json())  # noqa: E501
    
    ret = controller_helper.get_packages_by_name(name)
    return ret


@app.route("/package/byName/<name>", methods=["DELETE"])
def package_by_name_delete(name, x_authorization=None):  # noqa: E501
    """Delete all versions of this package.

     # noqa: E501

    :param name: 
    :type name: dict | bytes
    :param x_authorization: 
    :type x_authorization: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        name = PackageName.from_dict(connexion.request.get_json())  # noqa: E501
    
    ret = controller_helper.delete_package_by_name(name)
    return ret


@app.route("/packages", methods=["POST"])
def packages_list():
    offset = 1
    try:
        offset = (connexion.request.args.get("offset"))  # noqa: E501
    except:
        pass

    if (offset == None):
        offset = 0
    print (offset)
    ret = controller_helper.paginate(int(offset))
    
    print ("HERE IS IT IN THE FNAL RETURN")
    return ret



@app.route("/reset", methods=['DELETE'])
def registry_reset(x_authorization=None):  # noqa: E501
    """registry_reset

     # noqa: E501

    :param x_authorization: 
    :type x_authorization: dict | bytes

    :rtype: None
    """
    controller_helper.tear_down()
    return 'Registry is reset.', 200


@app.route("/user", methods=['POST'])
def add_user(x_auth=None):
    if connexion.request.is_json:
        body = (connexion.request.get_json())  # noqa: E501
    
    return body["metadata"]
