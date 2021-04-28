
# api.py
# Functions for APIs defined in assignment

import pyorient
import pika
import json
import sys
import multiprocessing as mp
from flask import Flask, jsonify
from util import read_hospital_data, read_patients_data
from DBLauncher import reset_db, load_db


app = Flask(__name__)
q = mp.Queue()

name = "COVID-19-Report"
login = 'root'
password = 'rootpwd'

# @app.route('/')
# def testapi():
#    return 'TestAPI'


def subscriber():

    username = 'student'
    password = 'student01'
    hostname = '128.163.202.50'
    virtualhost = '9'

    # CODE PARTIALLY SOURCED FROM EXAMPLE CODE GIVEN IN ASSIGNMENT
    credentials = pika.PlainCredentials(username, password)
    parameters = pika.ConnectionParameters(hostname,
                                           5672,
                                           virtualhost,
                                           credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    exchange_name = 'patient_data'

    channel.exchange_declare(exchange=exchange_name, exchange_type='topic')
    result = channel.queue_declare('', exclusive=True)
    queue_name = result.method.queue

    binding_keys = "#"
    if not binding_keys:
        sys.stderr.write("Usage: %s [binding_key]...\n" % sys.argv[0])
        sys.exit(1)
    for binding_key in binding_keys:
        channel.queue_bind(
            exchange=exchange_name, queue=queue_name, routing_key=binding_key)

    def callback(ch, method, properties, body):
        #print(" [x] %r:%r" % (method.routing_key, body))
        q.put(json.loads(body))
        # print(json.loads(body))

    channel.basic_consume(
        queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()


def data_to_db():
    client = pyorient.OrientDB("localhost", 2424)
    session_id = client.connect(login, password)
    client.db_open(name, login, password)
    while True:
        if not q.empty():
            data = q.get(0)
            # print("\n\n\n\n\n",data)
            read_patients_data(client, data)


# ========================================
# MANAGEMENT FUNCTION APIS
# ========================================


# /api/getteam
# API for name of team and list of student IDs on team
# E.g.:  {
#       "team_name": "LegoManics",
#       "Team_members_sids": ["12345678", "87654321"],
#       "app_status_code": "1"
#       }
@app.route('/api/getteam', methods=['GET'])
def getteam():
    return {
        'team_name': 'KhanalFinerty',
        'Team_members_sids': (
            '12331124',
            '12307438'),
        'app_status_code': '0'}


# /api/reset
# API for resetting all data
# Return: reset_status_code: 0 if not reset, 1 if reset
# E.g.:   { "reset_status_code": "1" }
@app.route('/api/reset', methods=['GET'])
def reset():
    return {"reset_status_code": reset_db()}


# ========================================
# REAL-TIME REPORTING APIS
# ========================================


# /api/zipalertlist
# API for list of zip codes in alert status, being growth over 2X in 15s
# Return: ziplist: list of zip codes
# E.g.:   { "ziplist": ["40351","40513",40506"] }
@app.route('/api/zipalertlist', methods=['GET'])
def zipalertlist():
    client = pyorient.OrientDB("localhost", 2424)
    session_id = client.connect(login, password)
    client.db_open(name, login, password)

    query_zipcodes = client.query(
        "select z from zipcodes where positive_test > 2*last_count")
    client.close()

    alert_zips = (zipcode.oRecordData['zipcode'] for zipcode in query_zipcodes)
    return jsonify(alert_zips)


# /api/alertlist
# API for alert if 5 or more zipcodes are in alert within 15 second window
# Return: state_status: 1 if state alert, 0 otherwise
# E.g.:   { "state_status": "0" }
@app.route('/api/alertlist', methods=['GET'])
def alertlist():
    client = pyorient.OrientDB("localhost", 2424)
    session_id = client.connect(login, password)
    client.db_open(name, login, password)

    query_state_status = client.query("select state_status from zipcodes")
    client.close()

    state_status = query_state_status[0].oRecordData['state_status']
    return {"state_status": state_status}


# /api/testcount
# API for statewide positive and negative test numbers
# E.g.:   { "positive_test": "0", "negative_test": "0", }
@app.route('/api/testcount', methods=['GET'])
def testcount():
    client = pyorient.OrientDB("localhost", 2424)
    session_id = client.connect(login, password)
    client.db_open(name, login, password)

    query_positive = client.query(
        "select count(*) from patient where patient_status_code in (2, 5, 6)")
    query_negative = client.query(
        "select count(*) from patient where patient_status_code in (1, 4)")
    client.close()

    positive_test_count = query_positive[0].oRecordData['count']
    negative_test_count = query_negative[0].oRecordData['count']

    return {"positive_test": positive_test_count,
            "negative_test": negative_test_count}


# ========================================
# LOGICAL AND OPERATING FUNCTIONS
# ========================================


# /api/getpatient/{mrn}
# API to search by mrn patient location (home or hospital)
# Return: mrn: medical record number
#         location_code: 0 for home, -1 for no assignment, or hospital ID
# E.g.:   {"mrn": "024c60d2-a1eb-498d-8739-02587ade42ac", "location_code":
# "11740202" }
@app.route('/api/getpatient/<string:mrn>', methods=['GET'])
def getpatient(mrn):
    client = pyorient.OrientDB("localhost", 2424)
    session_id = client.connect(login, password)
    client.db_open(name, login, password)

    data = client.query(
        "SELECT location_code FROM patient WHERE mrn = \"" +
        mrn +
        "\"")
    client.close()

    location_code = "-1"
    if len(data) != 0:
        location_code = str(data[0].oRecordData['location_code'])

    return {"mrn": mrn, "location_code": location_code}


# /api/gethospital/{id}
# API to report hospital patient numbers
# E.g.:   { "total_beds": "404", "avalable_beds": "200", "zipcode": "40202", }
@app.route('/api/gethospital/<string:id>', methods=['GET'])
def gethospital(id):
    client = pyorient.OrientDB("localhost", 2424)
    session_id = client.connect(login, password)
    client.db_open(name, login, password)

    # query the hospital database with given hospital id and return the details
    data = client.query("SELECT * FROM hospital WHERE id = \"" + id + "\"")
    client.close()

    # note: "avalable" (sic) from assignment
    total_beds, avalable_beds, zipcode = '0', '0', '0'
    if len(data) == 1:
        total_beds = str(data[0].oRecordData['total_beds'])
        avalable_beds = str(data[0].oRecordData['avalable_beds'])
        zipcode = str(data[0].oRecordData['zipcode'])

    return {
        "total_beds": total_beds,
        "avalable_beds": avalable_beds,
        "zipcode": zipcode}


load_db()
read_hospital_data()
mp.Process(target=subscriber).start()  # rabbit
mp.Process(target=data_to_db).start()

app.run(port=9000)
