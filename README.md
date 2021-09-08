# CS505 Spring 2021, COVID Final Project

The implementation of an application to support COVID-19 management

Background

Imagine you work for the Kentucky State Government and were tasked with developing solutions to assist in both the reporting and management of healthcare in relation to the COVID-19 pandemic.  Based on the request of Governor Beshear your application should provide real-time reporting and alerting of case growth by zipcode. In addition, your application should provide logic to route patients to appropriate facilities, if warranted, or determine if they should stay at home.  You will also need to provide methods to report on both individual patient information and provide up-to-date information on hospital status, such as capacity.
You will be provided several sources of data.  The first source of data is an event stream based on a patient record.  Some very clever CS505 students have already developed mobile applications that function both online and offline, so it is possible that patient events could come one at a time, or they could come in batches.  Data will be delivered to you using a message broker, with a payload as an array/list of dictionaries/maps in JSON format. You will also be provided a CSV list of hospitals with zipcode, number of beds, hospital id, and other information. In addition, you will be provided a CSV list of zipcodes in Kentucky, with distance to other zipcodes in Kentucky.  The messages and CSVs provide all the information you need to develop your application, but the rest is up to you.
You can use any programming language and any database technology you want to accomplish this project.  While the use of a relational database is allowed, it might not be the best choice for your project.  For example, what if in one thread I send you 1000 events and in another request a real-time report?  Everything is on the table, just make good decision, perhaps use something you learned in the class.  You will likely want to use more than one data management technology in the project, if your approach seems complicated, you are likely not using the correct technology.  Let the technology work for you.

You will be provided a detailed API list with expected input and output formats.  Since others will be using (and programmatically grading) this system, you must make sure you follow the API specifications exactly as described.  You will implement your system on your class VM. If you are part of a group only one VM needs to be used for implementation.  Grading will break down as follows:

Grading

    Application implementation (55%)
        The interfaces described in the project must be implemented on the class provided VM
        Your application must be able to run in the background, like previous homework projects
    Design as assessed by instructor (30%)
        We have discussed the many benefits of DBMS systems in this course, including DBMS attributes that also exist in non-traditional database and data management systems.  While much of this project could be done in custom code, you should be convinced at this point that various database management systems have their place and should be used where appropriate.  You choice and use of database(s) in your design will be used to determine your grade in this section.  If a database is not used at all in your design, it will be considered poor quality, and graded accordingly.
        Performance and application efficiency will also be graded in this section.  The system should respond with 100 incoming events close to how it would respond with 1 event.   
    Project Report (15%)
        A copy of the project report will be submitted by all team members
        Project report must include the following sections:
            Cover Page: Provide list team name,  team members, and team name
            Individual Contributions: A summary of contributions by individual  
            Project Code: Compressed project File 

Grading of Functions

    Implementation accounts for %55 if the grade, the functional section has a total of 100 points.
        Application Management Functions
            10pt: MF 1: API for name of team and list of student ids that are part of the team
            10pt: MF 2: This API is used for resetting all data
        Real-time Reporting Functions
            20pt: RTR 1: API alert on zipcode that is in alert state based on growth of cases
            10pt:  RTR 2: API alert on statewide when at least five zipcodes are in alert state (based on RT1) within the same 15 second window
            10pt:  RTR 3: API statewide positive and negative test counter
        Logic and Operational Functions
            (combined below) OF 1: API to route person to the best fit hospital based on patient status, provider status, distance (zipcode)
            20pt OF 2: API search by mrn patients location (home or specific hospital)
            20pt OF 3: API to report hospital patient numbers

Provided Data:
    Data 1: Patient status messages from provided message exchange
        Format:
            first_name: First name of person
            last_name: Last name of person
            mrn: medical record number (UUID)
            zip_code: The zipcode of the patient
            patient_status_code:
                0 // no symptoms, untested
                1 // no symptoms, tested negative
                2 // no symptoms, tested positive
                3 // symptoms, untested
                4 // symptoms, tested negative
                5 // symptoms, tested positive
                6 // critical/emergency symptoms, tested positive
        Example JSON:
            [{
              "first_name": "John",
              "last_name": "Prine",
              "mrn": "024c60d2-a1eb-498d-8739-02587ade42ac",
              "zipcode": "40351",
              "patient_status_code": "3"
            }]
        Notes
            MRN is unique / Sent exactly once
            No discharge from hospital, to make it easer 
            Any testing or hospital access, reduces bed count
        Credentials
            username = 'student'
            password = 'student01'
            hostname = TBD
            virtualhost = TBD 
                Your virtual host will be assigned based on your team
    Data 2: Distance between Ky zipcodes
        Data found in CSV file kyzipdistance.csv Download kyzipdistance.csv also details (not needed) kyzipdetails.csv Download kyzipdetails.csv
    Data 3:  List of hospitals in Ky by zipcode
        Data found in CSV file hospitals.csv Download hospitals.csv

API Function Descriptions:

    Management Functions: These functions are related to the management of your application
        MF 1: API for name of team and list of student ids that are part of the team
            Method: RESTful GET
            URL: /api/getteam
            Return Data:
                team_name: Name of your team
                team_member_sids: A list of the student ids of people on your team
                app_status_code: 0 = my app is offline, 1 = my app is online
            Example JSON Payload:
            {
              "team_name": "LegoManics",
              "Team_members_sids": ["12345678", "87654321"],
              "app_status_code": "1"
            }

        MF 2: This API is used for resetting all data. This function initializes your application.  This can be accomplished by dropping and recreating the databases and/or reinitializing any other services, variables, or processes you might be using to manage data.
            Method: RESTful GET
            URL: /api/reset
            Return Data:
                reset_status_code: 0 = my data could not be reset, 1 = my data was reset
            Example JSON Payload:
            {
              "reset_status_code": "1"
            }

    Real-time Reporting APIs: The functions are for real-time reporting and alerting
        RTR 1: API alert on zipcode that is in alert state based on growth of postive cases.  Models to characerize early epedemic growth can be complicated (https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5348083/ (Links to an external site.)), so we will go with a rather simple method to defined “alert” state.  We define alert state as a growth of 2X over a 15 second time interval. That is, if t0 - t14 there were 10 patients, and t15-t29 there were 25 patients, an alert state would be triggered.  However, if for time t15-t29 the new patient rate was 15, no alert would be generated.
            Method: RESTful GET
            URL: /api/zipalertlist
            Return Data:
                ziplist = list of zipcodes in alert status
            Example JSON Payload:
            {
              "ziplist": ["40351","40513",40506"]
            }
        RTR 2: API alert on statewide when at least five zipcodes are in alert state (based on RT1) within the same 15 second window.
            Method: RESTful GET
            URL: /api/alertlist
            Return Data:
                state_status = 0 = state is not in alert, 1 = state is in alert
            Example JSON Payload:
            {
              "state_status": "0"
            }
        RTR 3: API statewide positive and negative test counter
            Method: RESTful GET
            URL: /api/testcount
            Return Data:
                positive_test = count of positive test
                negative_test = count of negative_test

            Example JSON Payload:
            {
              "positive_test": "0",
              "negative_test": "0",
            }
    Logical and Operational Functions: These functions are for decision making and reporting
        OF 1: API to route pertson to the best fit hospital based on patient status, provider status, distance (zipcode)
        Method: Continuously process incoming messages from incoming exchange.  Store results using a method that can be used to report routing path in subsequent APIs

        Procedure based on Patient Status Code:
            0: no symptoms, untested
                Action: Stay at home until condition changes
            1: no symptoms, tested negative
                Action: Stay at home and practice distancing
            2: no symptoms, tested positive
                Action: Stay at home until condition changes
            3: symptoms, untested
                Action: Report to closest available facility for testing
            4: symptoms, tested negative
                Action: Stay at home until condition changes
            5: symptoms, tested positive
                Action: Report to closest available facility for treatment
            6: critical/emergency symptoms, tested positive
                Action: Report to closest available Level IV (I > II > III > IV) or better treatment facility

        OF 2: API search by mrn patients location (home or specific hospital)
            Method: RESTful GET
            URL: /api/getpatient/{mrn}
            Return Data:
                mrn = medical record number
                location_code = hospital ID, ID = 0 for home assignment, ID=-1 for no assignment
            Example JSON Payload:
            {
              "mrn": "024c60d2-a1eb-498d-8739-02587ade42ac",
              "location_code": "11740202"
            }

        OF 3: API to report hospital patient numbers
            Method: RESTful GET
            URL: /api/gethospital/{id}
            Return Data:
                total_beds = total number of beds
                avalable_beds = available number of beds
                zipcode = zipcode of hospital
            Example JSON Payload:
            {
              "total_beds": "404",
              "avalable_beds": "200",
              "zipcode": "40202",
            }
