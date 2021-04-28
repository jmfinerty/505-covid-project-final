# util.py
# Functions to be utilized by other functions

import pyorient
import pandas as pd

patient_status_map = {
    0: "no symptoms, untested",
    1: "no symptoms, tested negative",
    2: "no symptoms, tested positive",
    3: "symptoms, untested",
    4: "symptoms, tested negative",
    5: "symptoms, tested positive",
    6: "critical/emergency symptoms, tested positive"
}

stay_at_home = [0, 1, 2, 4]
report_hospital = [3, 5]
report_hospital_urgent = [6]
# location_code = hospital ID, ID = 0 for home assignment, ID=-1 for no
# assignment

hospital_filepath = 'hospitals.csv'
distance_filepath = 'kyzipdistance.csv'
# Level distribution of the hospitals.csv
#Counter({'NOT AVAILABLE': 80, 'LEVEL IV': 11, 'LEVEL III': 3, 'LEVEL I': 1, 'LEVEL I, LEVEL I PEDIATRIC': 1, 'LEVEL II': 1})

# Read from Data 1: Patient status messages from provided message exchange (RabbitMQ)
# in the format (eg.)
# [{
#   "first_name": "John",
#   "last_name": "Prine",
#   "mrn": "024c60d2-a1eb-498d-8739-02587ade42ac",
#   "zipcode": "40351",
#   "patient_status_code": "3"
# }]


def read_patients_data(client, data):
    for item in data:
        mrn = item["mrn"]
        zipcode = item["zipcode"]
        patient_status_code = item["patient"]
        location_code = -1
        client.command(
            "CREATE VERTEX patient SET mrn = \"" +
            mrn +
            "\", zipcode = \"" +
            zipcode +
            "\", patient_status_code = \"" +
            patient_status_code +
            "\"")
        location_code = findHospital(client, mrn, zipcode, patient_status_code)
        client.command(
            "UPDATE patient SET location_code = \"" +
            location_code +
            "\" WHERE mrn = \"" +
            mrn +
            "\"")

        if int(patient_status_code) in report_hospital or int(
                patient_status_code) in report_hospital_urgent:
            locs = client.query(
                "SELECT zipcode FROM zipcodes WHERE zipcode = \"" +
                zipcode +
                "\"")
            if len(locs) != 0:
                client.command(
                    "UPDATE zipcodes INCREMENT positive_test = 1 WHERE zipcode = \"" +
                    zipcode +
                    "\"")
            else:
                client.command(
                    "CREATE VERTEX zipcodes SET zipcode = \"" +
                    zipcode +
                    "\", positive_test = 1, last_test = 0,"
                    " ziplist = ' ', statealert = 0")


def read_hospital_data():
    # Name our database
    name = 'COVID-19-Report'
    # database login
    login = 'root'
    # password
    password = 'rootpwd'

    # Use pyorient to connect to our local orientdb docker container
    client = pyorient.OrientDB("localhost", 2424)
    session_id = client.connect(login, password)

    # open the database we are interested in
    client.db_open(name, login, password)

    # Now populate the hospital database with initialization total_beds ==
    # avalable_beds
    hospital_data = pd.read_csv(hospital_filepath)
    for i in range(len(hospital_data)):
        name = hospital_data.iloc[i]['NAME'].item()
        id = hospital_data.iloc[i]['ID'].item()
        zipcode = hospital_data.iloc[i]['ZIP'].item()
        level = hospital_data.iloc[i]['TRAUMA'].item()
        total_beds = hospital_data.iloc[i]['BEDS'].item()
        avalable_beds = total_beds  # Initially total beds == avalable beds
        state = "KY"  # Would be useful if we have to scale the DBMS to National scale
        client.command(
            "CREATE VERTEX hospital SET id = \"" +
            id +
            "\", name = \"" +
            str(name) +
            "\", state = \"" +
            state +
            "\", zipcode = \"" +
            zipcode +
            "\", level = \"" +
            level +
            "\", total_beds = \"" +
            total_beds +
            "\", avalable_beds = \"" +
            avalable_beds +
            "\"")


def findHospital(client, mrn, zipcode, patient_status_code):

    location_code = "-1"  # For no assignment

    if int(patient_status_code) in report_hospital or int(
            patient_status_code) in report_hospital_urgent:
        # patient is symptomatic and needs to be assigned to hospital
        if int(patient_status_code) in report_hospital_urgent:
            feasible_hospitals = client.command(
                "SELECT * FROM hospital WHERE avalable_beds > 0" +
                "\" AND level = 'LEVEL IV'")
            # IF NO LEVEL 4 Hospital found select at least normal hospital with
            # available beds
            if len(feasible_hospitals) == 0:
                feasible_hospitals = client.command(
                    "SELECT * FROM hospital WHERE avalable_beds > 0")
        else:
            feasible_hospitals = client.command(
                "SELECT * FROM hospital WHERE avalable_beds > 0")

        if len(feasible_hospitals) > 0:  # At least one hospital found
            best_hospital = findBestHospital(zipcode, feasible_hospitals)
            # Now assign this hospital and decrement the available bed counts
            # of this hospital
            location_code = str(best_hospital.oRecordData['id'])
            client.command(
                "UPDATE hospital INCREMENT avalable_beds = -1 WHERE id = \"" +
                location_code +
                "\"")

        else:  # No hospital found
            location_code = "-1"

    elif int(patient_status_code) in stay_at_home:
        location_code = "0"

    else:  # Patient status code unknown
        location_code = "-1"

    return location_code


def findBestHospital(zipcode, feasible_hospitals):
    distance_df = pd.read_csv(distance_filepath)
    dist = []
    for hospital in feasible_hospitals:
        hospital_zip = int(hospital.oRecordData['zipcode'])
        temp = float(distance_df[(distance_df['zip_from'] == int(zipcode)) & (
            distance_df['zip_to'] == int(hospital_zip))]['distance'].item())
        dist.append(temp)
    index_min = min(range(len(dist)), key=dist.__getitem__)

    return feasible_hospitals[index_min]
