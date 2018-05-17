
#!/usr/bin/python
import MySQLdb
import sys
from src.app import create_app
from src.db import *
import src.config as config
import requests

def populate_users():
    print "Populating users table.."
    cursor1.execute("select * from va_users")
    data = cursor1.fetchall()

    for row in data:
        if row[1] == "Prof. (Dr.) K. Kamal":
            name = Name("Prof.Dr.K. Kamal")
        else:
            name = Name(row[1].strip())
        email = Email(row[2].strip())
        if row[5] == 1:
            role = Role.get_by_id(2)
        elif row[5] == 2:
            role = Role.get_by_id(3)
        elif row[5] == None:
            role = Role.get_by_id(4)
        else:
            continue

        created = str(row[14])
        if row[15] == None:
            last_active = "Null"
        else:
            last_active = str(row[15])
        new_user = User(name=name, email=email, role=role, created=created,
                        last_active=last_active)
       # print new_user.name, new_user.email
        new_user.save()

def populate_workshops():
    print "Populating workshops table.."
    cursor1.execute("select * from workshop")
    data = cursor1.fetchall()

    for row in data:
        name = row[1].strip()
        location = row[2].strip()
        participants_attended = int(row[5])
        no_of_sessions = 0
        date = ''
        labs_planned = len(row[9].split(","))

        if row[12] == 3 or row[12] == 4 or row[12] == 5:
            no_of_participants_expected = 1000
        elif row[12] == 13:
            no_of_participants_expected = 100
        else:
            no_of_participants_expected = 0

        if row[12] == 3:
            user = User.query.filter_by(name="Rakesh T").first()
            status = Status.get_by_id(3)
        elif row[12] == 5:
            user = User.query.filter_by(name="P Saikumar").first()
            status = Status.get_by_id(3)
        elif row[12] == 4:
            user = User.query.filter_by(name="M Srinath Reddy").first()
            status = Status.get_by_id(3)
        elif row[12] == 13:
            user = User.get_by_id(4)
            status = Status.get_by_id(3)
        else:
            continue

        if row[0] == 3 or row[0] == 4 or row[0] == 5:
            experiments_conducted = 10000
        elif row[0] == 35 or row[0] == 41 or row[0] == 46:
            experiments_conducted = 22
        elif row[0] == 32 or row[0] == 33:
            experiments_conducted = 2000
        elif row[0] == 11 or row[0] == 28:
            experiments_conducted = 3000
        elif row[0] == 20 or row[0] == 27:
            experiments_conducted = 6000
        elif row[0] == 12 or row[0] == 15:
            experiments_conducted = 10
        elif row[0] == 13:
            experiments_conducted = 30
        elif row[0] == 10:
            experiments_conducted = 5000
        elif row[0] == 19:
            experiments_conducted = 2973
        elif row[0] == 21:
            experiments_conducted = 1080
        elif row[0] == 22:
            experiments_conducted = 3750
        elif row[0] == 23:
            experiments_conducted = 800
        elif row[0] == 24:
            experiments_conducted = 2880
        elif row[0] == 25:
            experiments_conducted = 2700
        elif row[0] == 26:
            experiments_conducted = 584
        elif row[0] == 34:
            experiments_conducted = 12
        elif row[0] == 36:
            experiments_conducted = 37
        elif row[0] == 39:
            experiments_conducted = 23
        elif row[0] == 42:
            experiments_conducted = 66
        else:
            experiments_conducted = 0


        participating_institutes = row[3].strip()

        if row[4] == '' or row[5] == '' or row[6] == '' or row[9] == '':
            pass
        else:
            no_of_sessions = int(row[6])
            date = str(row[4])

        new_workshop = Workshop(name=name, location=location, user=user,
                                participating_institutes=participating_institutes,
                                participants_attended = participants_attended,
                                no_of_sessions=no_of_sessions,
                                no_of_participants_expected = no_of_participants_expected,
                                experiments_conducted=experiments_conducted,
                                labs_planned=labs_planned,
                                status=status, date=date)

        new_workshop.save()


def populate_nodal_centres():
    print "Populating nodal centres table.."
    cursor1.execute("select * from va_users")
    data = cursor1.fetchall()

    for row in data:
        name = ''
        location = ''
     #   user = User.query.filter_by(name=row[1]).first()
        if row[8] == 1:
            user = User.query.filter_by(name="sripathi").first()
        elif row[8] == 2:
            user = User.query.filter_by(name="Geeta Bose").first()
        elif row[8] == 6:
            user = User.query.filter_by(name="karunakar").first()
        elif row[8] == 8:
            user = User.query.filter_by(name="Kantesh Balani").first()
        elif row[8] == 9:
            user = User.query.filter_by(name="Pushpdeep Mishra").first()
        elif row[8] == 16:
            user = User.query.filter_by(name="Yogesh").first()
        elif row[8] == 20:
            user = User.query.filter_by(name="Sanjeet Kumar").first()
        elif row[8] == 22:
            user = User.query.filter_by(name="Dr Vinod Kumar").first()
        else:
            continue

        if row[6] == 'TASK':
            name = 'TASK'
            location = 'Null'
        elif row[6] == None:
            name = 'Null'
            location = 'Null'
        elif ',' in row[6]:
            name_location = row[6].split(",")
            name = name_location[0].strip()
            location = name_location[1].strip()
        else:
            name = row[6]
            location = 'Null'
            #new_centre.save()
        if user == None:
            user = User.query.filter_by(name="dummyuseroc").first()

        new_centre = NodalCentre(name=name, location=location, created_by=user)
        new_centre.save()
       # print new_centre.name, new_centre.location, new_centre.created_by.name

def populate_nodal_coordinator_details():
    print "Populating nodal coordinator details table.."
    cursor1.execute("select * from va_users")
    data = cursor1.fetchall()

    for row in data:
        if row[9] == None:
            target_workshops = 0
        else:
            target_workshops = int(row[9])
        if row[10] == None or row[10] == '':
            target_participants = 0
        else:
            target_participants = int(row[10])
        if row[11] == None:
            target_experiments = 0
        else:
            target_experiments = int(row[11])

        nodal_centre = NodalCentre.get_by_id(1)
#        user1 = User.query.filter_by(name=row[1]).first()
#        user2 = User.get_by_id(2)

        if  row[1] == 'test':
            continue
        else:
            user1 = User.query.filter_by(name=row[1]).first()
#        if row[8] == None:
#            continue

        if row[8] == 1:
            user2 = User.query.filter_by(name="sripathi").first()
        elif row[8] == 2:
            user2 = User.query.filter_by(name="Geeta Bose").first()
        elif row[8] == 6:
            user2 = User.query.filter_by(name="karunakar").first()
        elif row[8] == 8:
            user2 = User.query.filter_by(name="Kantesh Balani").first()
        elif row[8] == 9:
            user2 = User.query.filter_by(name="Pushpdeep Mishra").first()
        elif row[8] == 16:
            user2 = User.query.filter_by(name="Yogesh").first()
        elif row[8] == 20:
            user2 = User.query.filter_by(name="Sanjeet Kumar").first()
        elif row[8] == 22:
            user2 = User.query.filter_by(name="Dr Vinod Kumar").first()
        else:
            continue

        if row[6] == "Modern Institute of Technology and Research Centre, Alwar":
            nodal_centre = NodalCentre.query.filter_by(name="Modern Institute of Technology and Research Centre").first()
        if row[6] == "Noida Institute of Engineering and Technology, Greater Noida":
            nodal_centre = NodalCentre.query.filter_by(name="Noida Institute of Engineering and Technology").first()
        if row[6] == "Asia Pacific Institute of Information Technology, Panipat":
            nodal_centre = NodalCentre.query.filter_by(name="Asia Pacific Institute of Information Technology").first()
        if row[6] == "Meerut Institute of Technology, Meerut":
            nodal_centre = NodalCentre.query.filter_by(name="Meerut Institute of Technology").first()
        if row[6] == "Desh Bhagat University, Punjab":
            nodal_centre = NodalCentre.query.filter_by(name="Desh Bhagat University").first()
        if row[6] == "Lingaya's University, Faridabad":
            nodal_centre = NodalCentre.query.filter_by(name="Lingaya's University").first()
        if row[6] == "Krishna Institute of Engineering and Technology, Ghaziabad":
            nodal_centre = NodalCentre.query.filter_by(name="Krishna Institute of Engineering and Technology").first()
        if row[6] == "Dronacharya College of Engineering, Gurgaon":
            nodal_centre = NodalCentre.query.filter_by(name="Dronacharya College of Engineering").first()
        if row[6] == "Dronacharya Group of Institution, Greater Noida":
            nodal_centre = NodalCentre.query.filter_by(name="Dronacharya Group of Institution").first()
        if row[6] == "IIMT College of Engineering, Greater Noida":
            nodal_centre = NodalCentre.query.filter_by(name="IIMT College of Engineering").first()
        if row[6] == "Chandigarh University, Gauruan, Punjab.":
            nodal_centre = NodalCentre.query.filter_by(name="Chandigarh University, Gauruan").first()
        if row[6] == "Swami Vivekanand College of Engineering, Indore":
            nodal_centre = NodalCentre.query.filter_by(name="Swami Vivekanand College of Engineering").first()
        if row[6] == "Global Group of Institutions, Lucknow":
            nodal_centre = NodalCentre.query.filter_by(name="Global Group of Institutions").first()
        if row[6] == "Dr. Ambedkar Institute of Technology for Handicapped, Kanpur":
            nodal_centre = NodalCentre.query.filter_by(name="Dr. Ambedkar Institute of Technology for Handicapped").first()
        if row[6] == "Hindustan Institute of Technology and Management, Agra":
            nodal_centre = NodalCentre.query.filter_by(name="Hindustan Institute of Technology and Management").first()
        if row[6] == "Pranveer Singh Institute of Technology, Kanpur":
            nodal_centre = NodalCentre.query.filter_by(name="Pranveer Singh Institute of Technology").first()
        if row[6] == "Saraswati Gyan Mandir Inter College, Indira Nagar, Kanpur":
            nodal_centre = NodalCentre.query.filter_by(name="Saraswati Gyan Mandir Inter College, Indira Nagar").first()
        if row[6] == "Kendriya Vidyalaya, IIT Kanpur":
            nodal_centre = NodalCentre.query.filter_by(name="Kendriya Vidyalaya").first()
        if row[6] == "Babu Banarasi Das University, Lucknow":
            nodal_centre = NodalCentre.query.filter_by(name="Babu Banarasi Das University").first()
        if row[6] == "Krishna Engineering College, Ghaziabad":
            nodal_centre = NodalCentre.query.filter_by(name="Krishna Engineering College").first()
        if row[6] == "Bharat Institute of Technology, Meerut":
            nodal_centre = NodalCentre.query.filter_by(name="Bharat Institute of Technology").first()
        if row[6] == "JSSATE, Noida":
            nodal_centre = NodalCentre.query.filter_by(name="JSSATE").first()
        if row[6] == "Seth Anandram Jaipuria, Kanpur":
            nodal_centre = NodalCentre.query.filter_by(name="Seth Anandram Jaipuria").first()
        if row[6] == "KV Cant, Kanpur":
            nodal_centre = NodalCentre.query.filter_by(name="KV Cant").first()
        if nodal_centre == None:
            nodal_centre = NodalCentre.query.filter_by(name="dummycentre").first()

        if user2 == None:
            user2 = User.query.filter_by(name="dummyuseroc").first()
        if user1 == None:
            user1 = User.query.filter_by(name="dummyusernc").first()


        nodal_coordinator_detail = NodalCoordinatorDetail(user=user1,
                                                          target_workshops=target_workshops,
                                                          created_by=user2,
                                                          nodal_centre=nodal_centre,
                                                          target_participants=target_participants,
                                                          target_experiments=target_experiments)
        print nodal_coordinator_detail.user.name, nodal_coordinator_detail.target_workshops,
        print nodal_coordinator_detail.created_by.name, nodal_coordinator_detail.nodal_centre.name,
        print nodal_coordinator_detail.target_participants, nodal_coordinator_detail.target_experiments
        nodal_coordinator_detail.save()

def populate_workshop_reports():
    print "Populating workshop reports table.."
    cursor1.execute("select * from workshop_report")
    data = cursor1.fetchall()

    for row in data:
        if row[1] == 11:
            workshop = Workshop.get_by_id(6)
        elif row[1] == 12:
            workshop = Workshop.get_by_id(7)
        else:
            workshop = Workshop.get_by_id(row[1])

        if row[5] != None:
            name = "Attendance Sheet"
            path = "/static/uploads/" + row[5]
            new_workshop_report = WorkshopReport(name=name, workshop=workshop,
                                                 path=path)
            new_workshop_report.save()

        if row[8] != None:
            name = "Workshop Photos"
            path = "/static/uploads/" + row[8]

            new_workshop_report = WorkshopReport(name=name, workshop=workshop,
                                                 path=path)
            new_workshop_report.save()

        if row[7] != None:
            name = "College Report"
            path = "/static/uploads/" + row[7]

            new_workshop_report = WorkshopReport(name=name, workshop=workshop,
                                                 path=path)
            new_workshop_report.save()

def populate_reference_documents():
    print "Populating reference documents table.."
    user = User.query.filter_by(name="admin").first()

    name1 = Name("Prerequisites of Workshop")
    path1 = "/static/uploads/1440048323-17.pdf"
    new_reference_document1 = ReferenceDocument(name=name1, user=user,
                                                path=path1)
    new_reference_document1.save()

    name2 = Name("Eligibility System Configuration Infrastructure")
    path2 = "/static/uploads/1440048369-12.doc"
    new_reference_document2 = ReferenceDocument(name=name2, user=user,
                                                path=path2)
    new_reference_document2.save()

    name3 = Name("Virtual Labs Handout")
    path3 = "/static/uploads/1440044856-79.pdf"
    new_reference_document3 = ReferenceDocument(name=name3, user=user,
                                                path=path3)
    new_reference_document3.save()

    name4 = Name("Feedback Form")
    path4 = "/static/uploads/1440045014-23.pdf"

    new_reference_document4 = ReferenceDocument(name=name4, user=user,
                                                path=path4)
    new_reference_document4.save()

    name5 = Name("Attendance Sheet")
    path5 = "/static/uploads/1440045279-57.pdf"
    new_reference_document5 = ReferenceDocument(name=name5, user=user,
                                                path=path5)
    new_reference_document5.save()

    name6 = Name("College Report Format")
    path6 = "/static/uploads/1437747400-13.docx"
    new_reference_document6 = ReferenceDocument(name=name6, user=user,
                                                path=path6)
    new_reference_document6.save()

    user7 = User.get_by_id(4)
    name7 = Name("Attendance Sheet")
    path7 = "/static/uploads/Screenshot-1.png"
    new_reference_document7 = ReferenceDocument(name=name7, user=user7,
                                                path=path7)
    new_reference_document7.save()

    user8 = User.get_by_id(4)
    name8 = Name("College Report")
    path8 = "/static/uploads/APSEC2015-Visa-Invitation letter to Dongjin Yu.pdf"
    new_reference_document8 = ReferenceDocument(name=name8, user=user8,
                                                path=path8)
    new_reference_document8.save()

    user9 = User.get_by_id(6)
    name9 = Name("College Report")
    path9 = "/static/uploads/IMG_20151003_213714039_HDR.jpg"
    new_reference_document9 = ReferenceDocument(name=name9, user=user9,
                                                 path=path9)
    new_reference_document9.save()

    user10 = User.get_by_id(6)
    name10 = Name("College Report")
    path10 = "/static/uploads/IMG_20151003_213448124_HDR.jpg"
    new_reference_document10 = ReferenceDocument(name=name10, user=user10,
                                                 path=path10)
    new_reference_document10.save()

    user11 = User.get_by_id(6)
    name11 = Name("College Report")
    path11 = "/static/uploads/Bits Clg report.pdf"
    new_reference_document11 = ReferenceDocument(name=name11, user=user11,
                                                 path=path11)
    new_reference_document11.save()

    user12 = User.get_by_id(15)
    name12 = Name("College Report")
    path12 = "/static/uploads/APSEC2015-Visa-Invitation letter to Dongjin Yu.pdf"
    new_reference_document12 = ReferenceDocument(name=name12, user=user12,
                                                 path=path12)
    new_reference_document12.save()

    
if __name__ == "__main__":
    connection1 = MySQLdb.connect(host="localhost", user="root",
                                  passwd="root", db="old_outreach")
    cursor1 = connection1.cursor()

    connection2 = MySQLdb.connect(host="localhost", user="root",
                                  passwd="root", db="outreach")
    cursor2 = connection2.cursor()

    db.create_all(app=create_app(config))
    populate_users()
    populate_workshops()
    populate_nodal_centres()
    populate_nodal_coordinator_details()
    populate_workshop_reports()
    populate_reference_documents()

    cursor1.close()
    connection1.close()

    cursor2.close()
    connection2.close()
