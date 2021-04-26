import pyorient
import json
import re
import logging
import pandas as pd

# Adapted from https://github.com/codybum/genparse/blob/master/DBTools.py

def reset_db():

    name = "COVID-19-Report"
    #database login
    login = 'root'
    #password
    password = 'rootpwd'
    #Use pyorient to connect to our local orientdb docker container
    client = pyorient.OrientDB("localhost", 2424)
    session_id = client.connect(login, password)
    status = 0
     
    if client.db_exists(name):
        # Reset the existing database
        client.db_drop(name)
        logging.info(name,"Database Reset")
        status = 1
    else:
        # Create New Database
        client.db_create(name,
        pyorient.DB_TYPE_GRAPH,
        pyorient.STORAGE_TYPE_PLOCAL)
        logging.info(name,"New Database created")
        status = 1
    return status


def load_db():

    #Name our database
    name = 'COVID-19-Report'
    #database login
    login = 'root'
    #password
    password = 'rootpwd'

    #Use pyorient to connect to our local orientdb docker container
    client = pyorient.OrientDB("localhost", 2424)
    session_id = client.connect(login, password)

    #remove old database and create new one
    reset_db()

    #open the database
    client.db_open(name, login, password)

    #Create Classes for three types of data and their derived attributes based on requirements of the project

    #Data 1: Patient status messages from provided message exchange broker (RabbitMQ)
    client.command("CREATE CLASS patient extends V")
    client.command("CREATE PROPERTY patient.first_name String")
    client.command("CREATE PROPERTY patient.last_name String")
    client.command("CREATE PROPERTY patient.mrn String")
    client.command("CREATE PROPERTY patient.zipcode integer")
    client.command("CREATE PROPERTY patient.patient_status_code integer")
    client.command("CREATE PROPERTY patient.location_code integer") #Required by OF2:API search by mrn patients location (home or specific hospital)

    #Data 2: Distance between Ky zipcodes
    client.command("CREATE CLASS zipcodes extends V")
    client.command("CREATE PROPERTY zipcodes.zipcode Integer") 
    client.command("CREATE PROPERTY zipcodes.last_test Integer")
    client.command("CREATE PROPERTY zipcodes.ziplist String") #Required by RTR 1: API alert on zipcode that is in alert state based on growth of postive cases. 
    client.command("CREATE PROPERTY zipcodes.state_status Integer") #Required by RTR 2: API alert on statewide when at least five zipcodes are in alert state (based on RT1) within the same 15 second window.
    client.command("CREATE PROPERTY zipcodes.positive_test Integer") #Required by RTR 3: API statewide positive and negative test counter
    client.command("CREATE PROPERTY zipcodes.negative_test Integer") #Required by RTR 3: API statewide positive and negative test counter

    #Data 3:List of hospitals in Ky by zipcode
    client.command("CREATE CLASS hospital extends V")
    client.command("CREATE PROPERTY hospital.name String")
    client.command("CREATE PROPERTY hospital.id Integer")
    client.command("CREATE PROPERTY hospital.zipcode Integer") #Required by OF3: API to report hospital patient numbers
    client.command("CREATE PROPERTY hospital.level String") #Required by OF1: API to route pertson to the best fit hospital based on patient status, provider status, distance (zipcode)
    client.command("CREATE PROPERTY hospital.total_beds Integer")  #Required by OF3: API to report hospital patient numbers
    client.command("CREATE PROPERTY hospital.state String")
    client.command("CREATE PROPERTY hospital.avalable_beds Integer") #Required by OF3: API to report hospital patient numbers

    client.close()
