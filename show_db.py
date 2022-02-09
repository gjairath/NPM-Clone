# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 10:57:38 2021

@author: garvi
"""

from swagger_server.controllers import session_config


session = session_config.return_session()


def display_sql():
    print ("\n====================\n")
    print (session.query(session_config.Users).all())
    print (session.query(session_config.Projects).all())
    print (session.query(session_config.Metrics).all())    
    print ("\n====================\n\n")

# session_config.tear_session()
# #print ("Dropping pojrect")
# session_config.drop_it_like_its_HOT()
# session_config.make_table()

display_sql()

#session.rollback()
#session.flush()

