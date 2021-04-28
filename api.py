
# api.py
# Functions for APIs defined in assignment

import util
import pyorient
from flask import Flask, jsonify
from DBLauncher import reset_db

app = Flask(__name__)

name = "COVID-19-Report"
login = 'root'
password = 'rootpwd'

# @app.route('/')
# def testapi():
#    return 'TestAPI'


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
            '12307438',
            'SUBASHID'),
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
def OF3(id):
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


app.run()
