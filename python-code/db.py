
# -*- coding: utf-8 -*-

from collections import OrderedDict

from flask_sqlalchemy import SQLAlchemy
from flask import current_app, request
from sqlalchemy.orm import relationship
import sqlalchemy.types as types

from flask import current_app

import os
import re
from urlparse import urlparse
from datetime import datetime
import json

from op_exceptions import AttributeRequired
from utils import typecheck


db = SQLAlchemy()


# Abstract class to hold common methods
class Entity(db.Model):

    __abstract__ = True

    # save a db.Model to the database. commit it.
    def save(self):
        db.session.add(self)
        db.session.commit()

    # update the object, and commit to the database
    def update(self, **kwargs):
        for attr, val in kwargs.iteritems():
            setter_method = "set_" + attr
            try:
                self.__getattribute__(setter_method)(val)
            except Exception as e:
                raise e

        self.save()

    #print "Setting new val"
    #print "Calling %s on %s" % (method_to_set, curr_entity)
    #try:
    #    getattr(record, method_to_set)(new_val)
    #except Exception as e:
    #pass

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Name(object):
    def __init__(self, value):
        # if the string contains any non-alphabet and non-space character, raise
        # a type error
        if re.search('[^a-zA-Z. ]+', value):
            current_app.logger.debug("%s is not a Name type! "  % value)
            raise TypeError('%s is not a Name type!' % value)

        self.value = value

class Email(object):
    def __init__(self, value):
        if not re.search('[^@]+@[^@]+\.[^@]+', value):
            current_app.logger.debug("%s is not an Email type! "  % value)
            raise TypeError('%s is not an email!' % value)
        self.value = value
        

class Role(Entity):

    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)

    users = db.relationship('User', backref='role')
        

    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            current_app.logger.debug("mandatory attribute `name` is missing")
            raise AttributeRequired("mandatory attribute `name` is missing")
        self.set_name(kwargs['name'])

    @staticmethod
    def get_by_id(id):
        current_app.logger.debug("get by Role id: %s"  % id)
        return Role.query.get(id)

    @staticmethod
    def get_all():
        current_app.logger.debug("get all rows of Role entity")
        return Role.query.all()

    def get_name(self):
        current_app.logger.debug("get name of the Role: %s" % self.name)
        return self.name

    @typecheck(name=Name)
    def set_name(self, name):
        self.name = name.value

    def to_client(self):
        return {
            'id': self.id,
            'name': self.name
        }

class User(Entity):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True)
    institute_name = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    reference_documents = db.relationship('ReferenceDocument', backref='user')
    created = db.Column(db.String(128))
    last_active = db.Column(db.String(128))
    workshops = db.relationship('Workshop', backref='user')

    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            current_app.logger.debug("mandatory attribute `name` is missing")
            raise AttributeRequired("mandatory attribute `name` is missing")
        self.set_name(kwargs['name'])

        if 'email' not in kwargs:
            current_app.logger.debug("mandatory attribute `email` is missing")
            raise AttributeRequired("mandatory attribute `email` is missing")
        self.set_email(kwargs['email'])

        if 'role' not in kwargs:
            current_app.logger.debug("mandatory attribute `role` is missing")
            raise AttributeRequired("mandatory attribute `role` is missing")
        self.set_role(kwargs['role'])

        if 'last_active' in kwargs:
            current_app.logger.debug("mandatory attribute `last_active` is missing")
            self.set_last_active(kwargs['last_active'])

        if 'created' in kwargs:
            self.set_toc(kwargs['created'])

        if 'institute_name' in kwargs:
            self.set_institute_name(kwargs['institute_name'])
        
        
    def __str__(self):
        return "Name = %s, e-mail id = %s,\ created = %s,\
        institute_name = %s, role=%s, last_active = %s"\
        % (self.name, self.email, self.created,
           self.institute_name, self.role.name,
           self.last_active)

    def __repr__(self):
        return "Name = %s, e-mail id = %s, created=%s\
        institute_name = %s, role=%s, last_active = %s"\
        % (self.name, self.email, self.created,
           self.institute_name, self.role.name,
           self.last_active)

    @staticmethod
    def get_all():
        current_app.logger.debug("get all rows of User entity")
        return User.query.all()

    @staticmethod
    def get_by_id(id):
        current_app.logger.debug("get by User id: %s"  % id)
        return User.query.get(id)

    def get_name(self):
        current_app.logger.debug("get name of the User: %s" % self.name)
        return self.name

    def get_email(self):
        current_app.logger.debug("get email of the User: %s" % self.email)
        return self.email

    def get_institute_name(self):
        current_app.logger.debug("get institute_name of the User: %s" % self.institute_name)
        return self.institute_name

    def get_role(self):
        current_app.logger.debug("get role of the User: %s" % self.role)
        return self.role

    def get_created(self):
        current_app.logger.debug("get time of creation of the User: %s" % self.created)
        return self.created

    def get_last_active(self):
        current_app.logger.debug("get last active time of the User: %s" % self.last_active)
        return self.last_active

    @typecheck(name=Name)
    def set_name(self, name):
        self.name = name.value

    @typecheck(email=Email)
    def set_email(self, email):
        self.email = email.value

    def set_institute_name(self, institute_name):
        self.institute_name = institute_name

    def set_last_active(self, last_active):
        self.last_active = last_active

    def set_toc(self, created):
        self.created = created

    @typecheck(role=Role)
    def set_role(self, role):
        self.role = role

    def to_client(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'role': self.role.to_client(),
            'last_active': self.last_active,
            'institute_name': self.institute_name,
            'created': self.created
        }

class ReferenceDocument(Entity):

    __tablename__ = 'reference_documents'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    path = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    

    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            raise AttributeRequired("mandatory attribute `name` is missing")
        self.set_name(kwargs['name'])

        if 'user' not in kwargs:
            raise AttributeRequired("mandatory attribute `user` is missing")
        self.set_user(kwargs['user'])
        
        if 'path' in kwargs:
            self.set_path(kwargs['path'])

    def __str__(self):
        return "Name = %s, user = %s, path = %s" % \
            (self.name, self.user.name, self.path)

    def __repr__(self):
        return "Name = %s, user = %s, path = %s" % \
            (self.name, self.user.name, self.path)

    @staticmethod
    def get_all():
        current_app.logger.debug("get all rows of Reference Document entity")

        return ReferenceDocument.query.all()

    @staticmethod
    def get_by_id(id):
        current_app.logger.debug("get by ReferenceDocument id: %s"  % id)
        return ReferenceDocument.query.get(id)

    def get_name(self):
        current_app.logger.debug("get name of the Reference Document: %s" % self.name)
        return self.name

    def get_path(self):
        current_app.logger.debug("get path of the Reference Document: %s" % self.path)
        return self.path

    def get_user(self):
        current_app.logger.debug("get user of the Reference Document: %s" % self.user)
        return self.user

    def set_name(self, name):
        self.name = name

    def set_path(self, path):
        self.path = path

    @typecheck(user=User)
    def set_user(self, user):
        self.user = user

    def to_client(self):
        return {
            'id': self.id,
            'name': self.name,
            'path': self.path,
            'user': self.user.to_client()
        }

class Status(Entity):

    __tablename__ = 'status'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)

    workshop = db.relationship('Workshop', backref='status')
        

    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            raise AttributeRequired("mandatory attribute `name` is missing")
        self.set_name(kwargs['name'])

    @staticmethod
    def get_by_id(id):
        current_app.logger.debug("get by Status id: %s"  % id)
        return Status.query.get(id)

    @staticmethod
    def get_all():
        current_app.logger.debug("get all rows of Status entity")

        return Status.query.all()

    def get_name(self):
        current_app.logger.debug("set the name of the status: %s" % self.name)
        return self.name

    @typecheck(name=Name)
    def set_name(self, name):
        self.name = name.value

    def to_client(self):
        return {
            'id': self.id,
            'name': self.name
        }

class Workshop(Entity):

    __tablename__ = 'workshops'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    location = db.Column(db.String(128))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))

    date = db.Column(db.String(128), nullable=False)
    created = db.Column(db.DateTime(), default=datetime.utcnow)
    last_updated = db.Column(db.String(128))
    participating_institutes = db.Column(db.String(128))
    no_of_participants_expected = db.Column(db.Integer)
    participants_attended = db.Column(db.Integer)
    no_of_sessions = db.Column(db.Integer)
    duration_of_sessions = db.Column(db.String(128))
    labs_planned = db.Column(db.Integer)
    disciplines = db.Column(db.String(128))
    experiments_conducted = db.Column(db.Integer)
    other_details = db.Column(db.String(128))
    cancellation_reason = db.Column(db.String(128))
    not_approval_reason = db.Column(db.String(128))
    gateway_ip = db.Column(db.String(128))
    version = db.Column(db.String(60))
    workshop_reports = db.relationship('WorkshopReport', backref='workshop')

    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            raise AttributeRequired("mandatory attribute `name` is missing")
        self.set_name(kwargs['name'])

        if 'location' not in kwargs:
            raise AttributeRequired("mandatory attribute `location` is missing")
        self.set_location(kwargs['location'])

        if 'user' not in kwargs:
            raise AttributeRequired("mandatory attribute `user` is missing")
        self.set_user(kwargs['user'])

        if 'participating_institutes' not in kwargs:
            raise AttributeRequired("mandatory attribute `participating_institutes` is missing")
        self.set_participating_institutes(kwargs['participating_institutes'])

        if 'no_of_participants_expected' not in kwargs:
            raise AttributeRequired("mandatory attribute `no_of_participants_\
            expected` is missing")
        self.set_no_of_participants_expected(kwargs['no_of_participants_expected'])

        if 'no_of_sessions' not in kwargs:
            raise AttributeRequired("mandatory attribute `no_of_sessions` is\
            missing")
        self.set_no_of_sessions(kwargs['no_of_sessions'])

        if 'labs_planned' not in kwargs:
            raise AttributeRequired("mandatory attribute `labs_planned` is\
            missing")
        self.set_labs_planned(kwargs['labs_planned'])

        if 'status' not in kwargs:
            raise AttributeRequired("mandatory attribute `status` is missing")
        self.set_status(kwargs['status'])

        if 'date' not in kwargs:
            raise AttributeRequired("mandatory attribute `date` is missing")
        self.set_date(kwargs['date'])

        if 'version' not in kwargs:
            raise AttributeRequired("mandatory attribute `version` is\
            missing")
        self.set_version(kwargs['version'])

        if 'participants_attended' in kwargs:
            self.set_participants_attended(kwargs['participants_attended'])

        if 'duration_of_sessions' in kwargs:
            self.set_duration_of_sessions(kwargs['duration_of_sessions'])

        if 'experiments_conducted' in kwargs:
            self.set_experiments_conducted(kwargs['experiments_conducted'])

        if 'disciplines' in kwargs:
            self.set_disciplines(kwargs['disciplines'])

        if 'other_details' in kwargs:
            self.set_other_details(kwargs['other_details'])

        if 'cancellation_reason' in kwargs:
            self.set_cancellation_reason(kwargs['cancellation_reason'])

        if 'not_approval_reason' in kwargs:
            self.set_not_approval_reason(kwargs['not_approval_reason'])

        if 'gateway_ip' in kwargs:
            self.set_gateway_ip(kwargs['gateway_ip'])

        if 'last_updated' in kwargs:
            self.set_last_updated(kwargs['last_updated'])

        
    def __str__(self):
        return "Name = %s, location = %s, user = %s, participating_institutes = %s,\
        no_of_participants_expected = %s, no_of_sessions = %s, labs_planned = %s,\
        status = %s, date = %s, participants_attended = %s, duration_of_sessions = %s,\
        experiments_conducted = %s, disciplines = %s, other_details = %s,\
        cancellation_reason = %s, not_approval_reason = %s, last_updated = %s"\
            % (self.name, self.location, self.user.name,\
               self.participating_institutes, self.no_of_participants_expected,\
               self.no_of_sessions, self.labs_planned, self.status, self.date,\
               self.participants_attended, self.duration_of_sessions,\
               self.experiments_conducted, self.disciplines,\
               self.other_details, self.cancellation_reason,\
               self.not_approval_reason, self.last_updated)

    
    def __repr__(self):
        return "Name = %s, location = %s, user = %s, participating_institutes = %s,\
        no_of_participants_expected = %s, no_of_sessions = %s, labs_planned = %s,\
        status = %s, date = %s, participants_attended = %s, duration_of_sessions = %s,\
        experiments_conducted = %s, disciplines = %s, other_details = %s,\
        cancellation_reason = %s, not_approval_reason = %s, last_updated = %s"\
            % (self.name, self.location, self.user.name,\
               self.participating_institutes, self.no_of_participants_expected,\
               self.no_of_sessions, self.labs_planned, self.status, self.date,\
               self.participants_attended, self.duration_of_sessions,\
               self.experiments_conducted, self.disciplines,\
               self.other_details, self.cancellation_reason,\
               self.not_approval_reason, self.last_updated)

    @staticmethod
    def get_all():
        current_app.logger.debug("get all rows of Workshop entity")
        return Workshop.query.all()

    @staticmethod
    def get_by_id(id):
        current_app.logger.debug("get by Status id: %s"  % id)
        return Workshop.query.get(id)

    def get_name(self):
        current_app.logger.debug("get the name of the Workshop: %s" % self.name)
        return self.name

    def get_location(self):
        current_app.logger.debug("get the name of the Workshop: %s" % self.name)
        return self.location

    def get_date(self):
        current_app.logger.debug("get the date of the Workshop: %s" % self.date)
        return self.date

    def get_user(self):
        current_app.logger.debug("get the user of the Workshop: %s" % self.user)
        return self.user

    def get_created(self):
        current_app.logger.debug("get the time of creation of the Workshop: %s" % self.created)
        return self.created

    def get_last_updated(self):
        current_app.logger.debug("get the last updated time of the Workshop: %s" % self.last_updated)
        return self.last_updated

    def get_participating_institutes(self):
        current_app.logger.debug("get the participating_institutes of the Workshop: %s" % self.participating_institutes)
        return self.participating_institutes

    def get_no_of_participants_expected(self):
        current_app.logger.debug("get the no_of_participants_expected of the Workshop: %s" % self.no_of_participants_expected)
        return self.no_of_participants_expected

    def get_no_of_participants_attended(self):
        current_app.logger.debug("get the participants_attended for the Workshop: %s" % self.participants_attended)
        return self.participants_attended

    def get_other_details(self):
        current_app.logger.debug("get the participants_attended for the Workshop: %s" % self.participants_attended)
        return self.other_details

    def get_no_of_expts_conducted(self):
        current_app.logger.debug("get the number of experiments conducted for the Workshop: %s" % self.experiments_conducted)
        return self.experiments_conducted

    def get_duration_of_sessions(self):
        current_app.logger.debug("get the duration_of_sessions for the Workshop: %s" % self.duration_of_sessions)
        return self.duration_of_sessions

    def get_disciplines(self):
        current_app.logger.debug("get the disciplines for the Workshop: %s" % self.disciplines)
        return self.disciplines

    def get_no_of_sessions(self):
        current_app.logger.debug("get the no_of_sessions for the Workshop: %s" % self.no_of_sessions)
        return self.no_of_sessions

    def get_planned_labs(self):
        current_app.logger.debug("get the labs_planned for the Workshop: %s" % self.labs_planned)
        return self.labs_planned

    def get_status(self):
        current_app.logger.debug("get the status of the Workshop: %s" % self.status)
        return self.status

    def get_cancellation_reason(self):
        current_app.logger.debug("get the cancellation_reason for the Workshop: %s" % self.cancellation_reason)
        return self.cancellation_reason

    def get_not_approval_reason(self):
        current_app.logger.debug("get the not_approval_reason for the Workshop: %s" % self.not_approval_reason)
        return self.not_approval_reason

    def get_gateway_ip(self):
        current_app.logger.debug("get the gateway_ip: %s" % self.gateway_ip)
        return self.gateway_ip

    def get_version(self):
        current_app.logger.debug("get version: %s" % self.version)
        return self.version

    @typecheck(name=str)
    def set_name(self, name):
        self.name = name

    @typecheck(location=str)
    def set_location(self, location):
        self.location = location

    @typecheck(user=User)
    def set_user(self, user):
        self.user = user

    @typecheck(date=str)
    def set_date(self, date):
        self.date = date

    @typecheck(participating_institutes=str)
    def set_participating_institutes(self, participating_institutes):
        self.participating_institutes = participating_institutes

    @typecheck(no_of_participants_expected=int)
    def set_no_of_participants_expected(self, no_of_participants_expected):
        self.no_of_participants_expected = no_of_participants_expected

    @typecheck(participants_attended=int)
    def set_participants_attended(self, participants_attended):
        self.participants_attended = participants_attended

    @typecheck(no_of_sessions=int)
    def set_no_of_sessions(self, no_of_sessions):
        self.no_of_sessions = no_of_sessions

    @typecheck(duration_of_sessions=str)
    def set_duration_of_sessions(self, duration_of_sessions):
        self.duration_of_sessions = duration_of_sessions

    @typecheck(disciplines=str)
    def set_disciplines(self, disciplines):
        self.disciplines = disciplines

    @typecheck(last_updated=str)
    def set_last_updated(self, last_updated):
        self.last_updated = last_updated

    @typecheck(labs_planned=int)
    def set_labs_planned(self, labs_planned):
        self.labs_planned = labs_planned

    @typecheck(experiments_conducted=int)
    def set_experiments_conducted(self, experiments_conducted):
        self.experiments_conducted = experiments_conducted

    @typecheck(other_details=str)
    def set_other_details(self, other_details):
        self.other_details = other_details

    @typecheck(status=Status)
    def set_status(self, status):
        self.status = status

    @typecheck(cancellation_reason=str)
    def set_cancellation_reason(self, cancellation_reason):
        self.cancellation_reason = cancellation_reason

    @typecheck(not_approval_reason=str)
    def set_not_approval_reason(self, not_approval_reason):
        self.not_approval_reason = not_approval_reason

    @typecheck(gateway_ip=str)
    def set_gateway_ip(self, gateway_ip):
        self.gateway_ip = gateway_ip

    @typecheck(version=str)
    def set_version(self, version):
        self.version = version

    def to_client(self):
        return {
            'id': self.id,
            'location': self.location,
            'name': self.name,
            'user': self.user.to_client(),
            'last_updated': self.last_updated,
            'created': self.created.isoformat(),
            'date': self.date,
            'participating_institutes': self.participating_institutes,
            'no_of_participants_expected': self.no_of_participants_expected,
            'participants_attended': self.participants_attended,
            'no_of_sessions': self.no_of_sessions,
            'duration_of_sessions': self.duration_of_sessions,
            'labs_planned': self.labs_planned,
            'disciplines': self.disciplines,
            'experiments_conducted': self.experiments_conducted,
            'other_details': self.other_details,
            'status': self.status.to_client(),
            'cancellation_reason': self.cancellation_reason,
            'not_approval_reason': self.not_approval_reason,
            'gateway_ip': self.gateway_ip,
            'version': self.version
        }

class NodalCentre(Entity):

    __tablename__ = 'nodal_centres'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    location = db.Column(db.String(128))
    pincode = db.Column(db.String(128))
    longitude = db.Column(db.String(128))
    lattitude = db.Column(db.String(128))
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    created_by = relationship('User', foreign_keys=[created_by_id])

    def __init__(self, **kwargs):
        if 'name' not in kwargs:
            raise AttributeRequired("mandatory attribute `name` is missing")
        self.set_name(kwargs['name'])

        if 'location' not in kwargs:
            raise AttributeRequired("mandatory attribute `location` is missing")
        self.set_location(kwargs['location'])

        if 'created_by' not in kwargs:
            raise AttributeRequired("mandatory attribute `created_by` is missing")
        self.set_created_by(kwargs['created_by'])
        
        if 'longitude' in kwargs:
            self.set_longitude(kwargs['longitude'])
            
        if 'lattitude' in kwargs:
            self.set_lattitude(kwargs['lattitude'])

        if 'pincode' in kwargs:
            self.set_pincode(kwargs['pincode'])

        
    def __str__(self):
        return "Name = %s, location = %s, created_by = %s" % \
            (self.name, self.location, self.created_by)

    def __repr__(self):
        return "Name = %s, location = %s, created_by = %s" % \
            (self.name, self.location, self.created_by)

    @staticmethod
    def get_all():
        current_app.logger.debug("get all rows of Nodal Centre entity")
        return NodalCentre.query.all()

    @staticmethod
    def get_by_id(id):
        current_app.logger.debug("get by NodalCentre id: %s"  % id)
        return NodalCentre.query.get(id)

    def get_created_by(self):
        current_app.logger.debug("get of the user who created the NodalCentre: %s"  % self.created_by)
        return self.created_by

    def get_name(self):
        current_app.logger.debug("get name of the NodalCentre: %s"  % self.name)
        return self.name

    def get_location(self):
        current_app.logger.debug("get location of the NodalCentre : %s"  % self.location)
        return self.location

    @typecheck(created_by=User)
    def set_created_by(self, created_by):
        self.created_by = created_by

    @typecheck(name=str)
    def set_name(self, name):
        self.name = name

    @typecheck(location=str)
    def set_location(self, location):
        self.location = location

    @typecheck(longitude=str)
    def set_longitude(self, longitude):
        self.longitude = longitude

    @typecheck(pincode=str)
    def set_pincode(self, pincode):
        self.pincode = pincode

    @typecheck(lattitude=str)
    def set_lattitude(self, lattitude):
        self.lattitude = lattitude

    def to_client(self):
        return {
            'id': self.id,
            'created_by': self.created_by.to_client(),
            'name': self.name,
            'location': self.location,
            'pincode': self.pincode,
            'longitude': self.longitude,
            'lattitude': self.lattitude
        }

class NodalCoordinatorDetail(Entity):

    __tablename__ = 'nodal_coordinator_details'

    id = db.Column(db.Integer, primary_key=True)

    created = db.Column(db.DateTime(), default=datetime.utcnow)
    last_updated = db.Column(db.String(128))
    target_workshops = db.Column(db.Integer)
    target_participants = db.Column(db.Integer)
    target_experiments = db.Column(db.Integer)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    nodal_centre_id = db.Column(db.Integer, db.ForeignKey('nodal_centres.id'))

    user = relationship('User', foreign_keys=[user_id])
    created_by = relationship('User', foreign_keys=[created_by_id])
    nodal_centre = relationship('NodalCentre', foreign_keys=[nodal_centre_id])

    def __init__(self, **kwargs):

        if 'user' not in kwargs:
            raise AttributeRequired("mandatory attribute `user` is missing")
        self.set_user(kwargs['user'])

        if 'last_updated' in kwargs:
            self.set_last_updated(kwargs['last_updated'])

        if 'created_by' not in kwargs:
            raise AttributeRequired("mandatory attribute `created_by` is missing")
        self.set_created_by(kwargs['created_by'])

        if 'nodal_centre' not in kwargs:
            raise AttributeRequired("mandatory attribute `nodal_centre` is missing")
        self.set_nodal_centre(kwargs['nodal_centre'])

        if 'target_workshops' not in kwargs:
            raise AttributeRequired("mandatory attribute `target_workshops` is missing")
        self.set_target_workshops(kwargs['target_workshops'])

        if 'target_participants' not in kwargs:
            raise AttributeRequired("mandatory attribute `target_participants` is missing")
        self.set_target_participants(kwargs['target_participants'])

        if 'target_experiments' in kwargs:
            self.set_target_experiments(kwargs['target_experiments'])

        
    def __str__(self):
        return "last_updated = %s, user = %s, created_by = %s,\
        nodal_centre = %s, target_workshops = %s,  target_participants = %s,\
        target_experiments = %s" %  (self.last_updated, self.user,
                                     self.created_by, self.nodal_centre,
                                     self.target_workshops,
                                     self.target_participants,
                                     self.target_experiments)


    def __repr__(self):
        return "last_updated = %s, user = %s, created_by = %s,\
        nodal_centre = %s, target_workshops = %s,  target_participants = %s,\
        target_experiments = %s" %  (self.last_updated, self.user,
                                     self.created_by, self.nodal_centre,
                                     self.target_workshops,
                                     self.target_participants,
                                     self.target_experiments)

    @staticmethod
    def get_all():
        current_app.logger.debug("get all rows of NodalCoordinatorDetail entity")
        return NodalCoordinatorDetail.query.all()

    @staticmethod
    def get_by_id(id):
        current_app.logger.debug("get by NodalCoordinatorDetail id: %s"  % id)
        return NodalCoordinatorDetail.query.get(id)

    def get_user(self):
        current_app.logger.debug("get user from NodalCoordinatorDetail Entity: %s"  % self.user)
        return self.user

    def get_created_by(self):
        current_app.logger.debug("get created_by user from NodalCoordinatorDetail: %s"  % self.created_by)
        return self.created_by

    def get_nodal_centre(self):
        current_app.logger.debug("get nodal_centre from NodalCoordinatorDetail: %s"  % self.nodal_centre)
        return self.nodal_centre

    def get_created(self):
        current_app.logger.debug("get time of creation from NodalCoordinatorDetail: %s"  % self.created)
        return self.created

    def get_last_updated(self):
        current_app.logger.debug("get created_by user from NodalCoordinatorDetail: %s"  % self.last_updated)
        return self.last_updated

    def get_target_workshops(self):
        current_app.logger.debug("get target_workshops from NodalCoordinatorDetail: %s"  % self.target_workshops)
        return self.target_workshops

    def get_target_participants(self):
        current_app.logger.debug("get target_participants from NodalCoordinatorDetail: %s"  % self.target_participants)
        return self.target_participants

    def get_target_experiments(self):
        current_app.logger.debug("get target_experiments from NodalCoordinatorDetail: %s"  % self.target_experiments)
        return self.target_experiments

    def set_last_updated(self, last_updated):
        current_app.logger.debug("set last updated time of the NodalCoordinatorDetail: %s" % last_updated)
        self.last_updated = last_updated

    @typecheck(user=User)
    def set_user(self, user):
        current_app.logger.debug("set user of the NodalCoordinatorDetail: %s" % user)
        self.user = user

    @typecheck(created_by=User)
    def set_created_by(self, created_by):
        current_app.logger.debug("set created by user of the NodalCoordinatorDetail: %s" % created_by)
        self.created_by = created_by

    @typecheck(nodal_centre=NodalCentre)
    def set_nodal_centre(self, nodal_centre):
        current_app.logger.debug("set target workshops of the NodalCoordinatorDetail: %s" % nodal_centre)
        self.nodal_centre = nodal_centre

    def set_target_workshops(self, target_workshops):
        current_app.logger.debug("set target workshops of the NodalCoordinatorDetail: %s" % target_workshops)
        self.target_workshops = target_workshops

    def set_target_participants(self, target_participants):
        current_app.logger.debug("set target participants of the NodalCoordinatorDetail: %s" % target_participants)
        self.target_participants = target_participants

    def set_target_experiments(self, target_experiments):
        current_app.logger.debug("set target experiments of the NodalCoordinatorDetail: %s" % target_experiments)
        self.target_experiments = target_experiments

    def to_client(self):
        return {
            'id': self.id,
            'user': self.user.to_client(),
            'created_by': self.created_by.to_client(),
            'nodal_centre': self.nodal_centre.to_client(),         
            'last_updated': self.last_updated,
            'created': self.created.isoformat(),
            'target_workshops': self.target_workshops,
            'target_participants': self.target_participants,
            'target_experiments': self.target_experiments
        }

class WorkshopReport(Entity):

    __tablename__ = 'workshop_reports'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    path = db.Column(db.String(128))
    workshop_id = db.Column(db.Integer, db.ForeignKey('workshops.id'))

    def __init__(self, **kwargs):

        if 'workshop' not in kwargs:
            raise AttributeRequired("mandatory attribute `workshop` is missing")
        self.set_workshop(kwargs['workshop'])
        
        if 'path' in kwargs:
            self.set_path(kwargs['path'])

        if 'name' not in kwargs:
            raise AttributeRequired("mandatory attribute `name` is missing")
        self.set_name(kwargs['name'])

    def __str__(self):
        return "workshop = %s, name = %s, path = %s" % \
            (self.workshop, self.name, self.path)

    def __repr__(self):
        return "workshop = %s, name=%s, path = %s" % \
            (self.workshop, self.name, self.path)

    @staticmethod
    def get_all():
        current_app.logger.debug("get all rows of WorkshopReport entity")
        return WorkshopReport.query.all()

    @staticmethod
    def get_by_id(id):
        current_app.logger.debug("get by WorkshopReport id: %s"  % id)
        return WorkshopReport.query.get(id)

    def get_path(self):
        current_app.logger.debug("get path of the WorkshopReport: %s"  % self.path)
        return self.path

    def get_name(self):
        current_app.logger.debug("get name of the WorkshopReport: %s"  % self.name)
        return self.name

    def get_workshop(self):
        current_app.logger.debug("get workshop of the WorkshopReport: %s"  % self.workshop)
        return self.workshop

    @typecheck(path=str)
    def set_path(self, path):
        current_app.logger.debug("set path of the WorkshopReport: %s" % path)
        self.path = path

    @typecheck(name=str)
    def set_name(self, name):
        current_app.logger.debug("set name of the WorkshopReport: %s" % name)
        self.name = name

    @typecheck(workshop=Workshop)
    def set_workshop(self, workshop):
        current_app.logger.debug("set workshop of the WorkshopReport: %s" % workshop)
        self.workshop = workshop

    def to_client(self):
        return {
            'id': self.id,
            'name': self.name,
            'path': self.path,
            'workshop': self.workshop.to_client()
        }
