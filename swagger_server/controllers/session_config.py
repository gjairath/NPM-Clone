# -*- coding: utf-8 -*-
"""
Created on Sat Dec  4 05:53:00 2021

@author: garvi
"""


# -*- coding: utf-8 -*-
"""
Created on Fri Dec  3 10:57:38 2021

@author: garvi
"""

import os
from flask_sqlalchemy import SQLAlchemy
from google.cloud.sql.connector import connector
import pymysql

from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy import Column, Integer, String, create_engine, Float, ForeignKey

Base = declarative_base()
from sqlalchemy import Sequence


# ------ ORMS ----------------
class Projects(Base):
    __tablename__ = 'projects'
    id = Column(Integer, primary_key = True, nullable = False, unique = True, autoincrement=True)
    name = Column(String(50), nullable = False, unique = False)
    version = Column(String(50), nullable = False, unique = False)
    
    custom_id = Column(String(50), nullable = True, unique = True)
    
    # 1 row of metrics, forward link
    project_metrics = relationship("Metrics", back_populates="project_owner")    

    
    def __repr__(self):
        return f'\n========\nID: {self.id}\nName: {self.name}\nVersion: {self.version}\nMetrics: {self.project_metrics}\n=======\n'



class Metrics(Base):
    __tablename__ = 'metrics'
    mid = Column(Integer, 
                    primary_key=True, nullable = False, unique = True, autoincrement=True)
    
    BusFactor = Column(Float, 
                         index=True)
    Correctness = Column(Float, index = True)
    GoodPinningPractice = Column(Float, index = True)
    LicenseScore = Column(Float, index = True)
    RampUp = Column(Float, index = True)
    ResponsiveMaintainer = Column(Float, index=True)

    
    # Back link to the project that can have 1 row of metrics.
    project_id = Column(Integer, ForeignKey('projects.id'))


    # There is no reason to set this.
    project_owner = relationship("Projects", back_populates="project_metrics")
    
    
    def ingestible(self):
        return (self.BusFactor >= 0.5 and 
                self.Correctness >= 0.5 and
                self.GoodPinningPractice >= 0.5 and
                self.LicenseScore >= 0.5 and
                self.RampUp >= 0.5 and
                self.ResponsiveMaintainer >= 0.5)


    def get_metrics(self):
        ret = {}
        ret['BusFactor'] = self.BusFactor
        ret['Correctness'] = self.Correctness
        ret['GoodPinningPractice'] = self.GoodPinningPractice
        ret['LicenseScore'] = self.LicenseScore
        ret['RampUp'] = self.RampUp
        ret['ResponsiveMaintainer'] = self.ResponsiveMaintainer
        
        return ret
    
    def __repr__(self):
        return 'ID:{}\n<METRICS \nBus: {} \
            \nCorrec: {}\nPins {}\nLicense Score: {}\
            \nRampup:{}\nResponsive:{}>'.format(self.mid,
                                                self.BusFactor, 
                                                self.Correctness, 
                                                self.GoodPinningPractice,
                                                self.LicenseScore,
                                                self.RampUp,
                                                self.ResponsiveMaintainer)

class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column(String(50))
    password = Column(String(50))

    def __repr__(self):
        return "<User(name='%s')>" % (
                                self.name)


# --------- Pool ---------
def getconn() -> pymysql.connections.Connection:
    conn: pymysql.connections.Connection = connector.connect(
        "purde-final-project:us-east1-d:project-db",
        "pymysql",
        user="root",
        password="CckioCDDqEwDL2kD",
        db="projects_v2"
    )
    return conn

pool = create_engine(
    "mysql+pymysql://",
    creator=getconn,
)        



def return_session():
    db = pool.connect()
    Session = sessionmaker(bind=pool)
    session = Session()

    return session


def update_session():
     db = pool.connect()
     Session = sessionmaker(bind=pool)
     Base.metadata.create_all(pool)
     
     
def tear_session():
    db = pool.connect()
    Session = sessionmaker(bind=pool)
    session = Session()

    session.query(Metrics).delete()
    session.query(Projects).delete()
    session.query(Users).delete()
    session.commit()
    
def drop_it_like_its_HOT():
    Base.metadata.drop_all(bind=pool, tables=[Metrics.__table__])
    Base.metadata.drop_all(bind=pool, tables=[Users.__table__])
    Base.metadata.drop_all(bind=pool, tables=[Projects.__table__])

def make_table():
    db = pool.connect()
    Session = sessionmaker(bind=pool)
    
    Base.metadata.create_all(pool) 
    