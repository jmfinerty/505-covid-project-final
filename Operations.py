##Operational Functions (OF) to be used in our DBMS
import util

# For API search by mrn patients location (home or specific hospital)
def OF2(mrn):
    name = "COVID-19-Report"
    #database login
    login = 'root'
    #password
    password = 'rootpwd'
    #Use pyorient to connect to our local orientdb docker container
    client = pyorient.OrientDB("localhost", 2424)
    session_id = client.connect(login, password)

    #open the database
    client.db_open(name, login, password)

    data = client.query("SELECT location_code FROM patient WHERE mrn = \"" + mrn + "\"")
    client.close()
    if len(data) != 0:
        location_code = str(data[0].oRecordData['location_code'])
        return location_code
    else:
        return "Some Error we should at least get -1"

# For API to report hospital patient numbers
def OF3(id):
    name = "COVID-19-Report"
    #database login
    login = 'root'
    #password
    password = 'rootpwd'
    #Use pyorient to connect to our local orientdb docker container
    client = pyorient.OrientDB("localhost", 2424)
    session_id = client.connect(login, password)

    #open the database
    client.db_open(name, login, password)

    #query the hospital database with given hospital id and return the details
    data = client.query("SELECT * FROM hospital WHERE id = \"" + id + "\"")
    client.close()
    if len(data) == 1:
        total_beds = str(data[0].oRecordData['total_beds'])
        avalable_beds = str(data[0].oRecordData['avalable_beds'])
        zipcode = str(data[0].oRecordData['zipcode'])
        hospital_data = [total_beds, avalable_beds, zipcode]
        return hospital_data
    else:
        return ["NA","NA","NA"]







