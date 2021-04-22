
# api.py
# Functions for APIs defined in assignment

# ========================================
# MANAGEMENT FUNCTION APIS
# ========================================


# /api/getteam
# API for name of team and list of student IDs on team
'''
E.g.:   {
        "team_name": "LegoManics",
        "Team_members_sids": ["12345678", "87654321"], 
        "app_status_code": "1"
        }
'''
def getteam():
    raise NotImplementedError


# /api/reset
# API for resetting all data
# Return: reset_status_code: 0 if not reset, 1 if reset
# E.g.:   { "reset_status_code": "1" }
def reset():
    raise NotImplementedError


# ========================================
# REAL-TIME REPORTING APIS
# ========================================


# /api/zipalertlist
# API for list of zip codes in alert status, being growth over 2X in 15s
# Return: ziplist: list of zip codes
# E.g.:   { "ziplist": ["40351","40513",40506"] }
def zipalertlist():
    raise NotImplementedError


# /api/alertlist
# API for alert if 5 or more zipcodes are in alert within 15 second window
# Return: state_status: 1 if state alert, 0 otherwise
# E.g.:   { "state_status": "0" }
def alertlist():
    raise NotImplementedError


# /api/testcount
# API for statewide positive and negative test numbers
# E.g.:   { "positive_test": "0", "negative_test": "0", }
def testcount():
    raise NotImplementedError


# ========================================
# LOGICAL AND OPERATING FUNCTIONS
# ========================================


# /api/getpatient/{mrn}
# API to search by mrn patient location (home or hospital)
# Return: mrn: medical record number
#         location_code: 0 for home, -1 for no assignment, or hospital ID
# E.g.:   {"mrn": "024c60d2-a1eb-498d-8739-02587ade42ac", "location_code": "11740202" }
def getpatient(mrn):
    raise NotImplementedError


# /api/gethospital{id}
# API to report hospital patient numbers
# E.g.:   { "total_beds": "404", "avalable_beds": "200", "zipcode": "40202", }
def gethospital(id):
    raise NotImplementedError
