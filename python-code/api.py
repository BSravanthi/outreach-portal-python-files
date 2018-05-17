
# -*- coding: utf-8 -*-

import os
import csv
import requests
from datetime import datetime
import inspect
from flask import session, render_template, Blueprint, request, jsonify, abort,\
    current_app, redirect, url_for
from config import *
from flask import current_app

from flask import Flask, redirect, url_for
from werkzeug import secure_filename
from flask_oauthlib.client import OAuth
from db import *
from utils import parse_request, jsonify_list
from maps import *
api = Blueprint('APIs', __name__)

session_list = {}
oauth = OAuth()

google_oauth = oauth.remote_app(
    'google',
    consumer_key=CONSUMER_KEY,
    consumer_secret=CONSUMER_SECRET,
    request_token_params={
        'scope': 'email', 'prompt' : 'select_account'
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

def get_college_name(mac_addr):
    index_name = "college_cloud"
    doc_name = "details"
    ELASTIC_URL = "%s/%s/%s/_search" % (ELASTIC_IP, index_name, doc_name)
    current_app.logger.debug("ELASTIC_URL %s" % (ELASTIC_URL))
    colleges = requests.get(ELASTIC_URL)
    if colleges.status_code == 200:
        for college in colleges.json()['hits']['hits']:            
            mac_addr_of_elastic_data = str(college['_source']['mac_addr'])
            current_app.logger.debug("college_details %s" % (mac_addr_of_elastic_data))
            if mac_addr == mac_addr_of_elastic_data:
                return str(college['_source']['college_name'])
        abort(int(college.status_code), "Error in getting college name from elastic db")

@api.route('/login')
def login():
    return google_oauth.authorize(callback=url_for('APIs.authorized', _external=True))

@api.route('/logout')
def logout():
    if 'google_token' in session:
        session.pop('google_token', None)
        session.pop('role', None)
        session.pop('email', None)
        session.pop('id', None)
        session.pop('name', None)
    if 'error' in session:
        session.pop('error', None)

    return redirect("/")

@api.route('/authorized')
def authorized():
    try:
        resp = google_oauth.authorized_response()
        if resp is None:
            return redirect("/")
        session['google_token'] = (resp['access_token'], '')
        user_info = google_oauth.get('userinfo')
        email = str(user_info.data['email'])

    except Exception as e:
        session['error'] = "Error in Google Authentication : " + str(e)            
        return redirect("/")
    try:
        url_for_getting_the_user = "%s/users?email=%s" % \
                                   (APP_URL, email)
        backend_resp = requests.get(url_for_getting_the_user)

        if (len(backend_resp.text.encode('ascii')) != 2):
            if 'error' in session:
                session.pop('error', None)

            session['email'] = email
            role = backend_resp.json()[0]['role']['name'].encode('ascii')
            name = backend_resp.json()[0]['name'].encode('ascii')
            session['role'] = role
            session['name'] = name
            session['id'] = backend_resp.json()[0]['id']
            
            if role == "OC":
                return redirect("/oc")
            
            elif role == "NC":
                return redirect("/nc")
            
            elif role == "admin":
                return redirect("/admin")

        else:        
            session.pop('google_token', None)
            session['error'] = "Unauthorized Email : "+email            
            return redirect("/")
          
    except Exception as e:
        session['error'] = "Error in Outreach Authentication : "+str(e)            
        return redirect("/")

@google_oauth.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

@api.route("/")
def index():
    remote_url = request.url
    if remote_url.find("vlabs.ac.in") != -1:
        return redirect(APP_URL)
    elif remote_url.find("localhost") != -1:
        return render_template("index.html")
    else:
        return render_template("index.html")

@api.route("/get_usage", methods=['GET','POST'])
def get_usage():
    if request.method == 'GET':
        return "This method is not allowed"
    
    if request.method == 'POST':  
        doc_name = "feedback"
        data_dict = request.get_json()
        oldformat = str(data_dict['date'])
        datetimeobject = datetime.strptime(oldformat,'%Y-%m-%d')
        date = datetimeobject.strftime('%d-%m-%Y')
        version = str(data_dict['version'])
        current_app.logger.debug("json = %s" % (data_dict))

        if version == 'offline':
            mac_addr = str(data_dict['mac_addr'])
            index_name = "%s_%s" % (get_college_name(mac_addr), mac_addr)
        else:
            gateway_ip = str(data_dict['gateway_ip'])
            current_app.logger.debug("gateway_ip %s" % (gateway_ip))
            index_name = "vlabs"            

        ELASTIC_URL = "%s/%s/%s/_search?size=10000" % (ELASTIC_IP, index_name, doc_name)
        current_app.logger.debug("ELASTIC_URL %s" % (ELASTIC_URL))
        count = 0
        usages = requests.get(ELASTIC_URL)
        
        if usages.status_code == 200:
            current_app.logger.debug("usages %s" % (usages.json()))
            for feedback in usages.json()['hits']['hits']:
                date_of_elastic_data = feedback['_source']['date']
                if version == "offline":
                    current_app.logger.debug("date %s" % (feedback['_source']['date']))
                    if date == date_of_elastic_data:
                        current_app.logger.debug("true")
                        count = count+1                    
                else:
                    gateway_ip_of_e_db = feedback['_source']['gateway_ip']
                    current_app.logger.debug("gateway_ip %s" % (feedback['_source']['gateway_ip']))
                    if date == date_of_elastic_data and gateway_ip == gateway_ip_of_e_db:
                        current_app.logger.debug("true")
                        count = count + 1                        
            return jsonify({"usage" : count})
        elif usages.status_code == 404:
            return jsonify({"usage" : count})
        else:
            abort(int(usages.status_code), "Error in getting usage from elastic db")

@api.route("/ws_details")
def ws_details():
    return render_template("ws_details.html")

@api.route("/ws_details_offline")
def ws_details_offline():
    return render_template("ws_details_offline.html")

@api.route("/ncentres")
def ncentres():
    return render_template("ncentres.html")

@api.route("/usage")
def usage():
    return render_template("usage.html")

@api.route("/admin", methods=['GET','POST'])
def admin():
    if request.method == 'GET':
	if ('email' in session) and (session['role'] == 'admin'):
	    rg = requests.get(APP_URL + "/reference_documents?user_id="+str(session['id']))
	    rg_json = json.loads(rg.text)
	    documents =  rg_json
	    return render_template("admin.html", documents=documents)
	else:
	    return redirect("/")

@api.route("/oc")
def outreach_coordinator():

    if ('email' in session) and (session['role'] == 'OC'):
	return render_template("oc.html")
    else:
	return redirect("/")

@api.route("/nc")
def nodal_coordinator():
    if ('email' in session) and (session['role'] == 'NC'):
	return render_template("nc.html")
    else:
	return redirect("/")

@api.route('/get_nc_wise_usage', methods=['GET'])
def get_nc_wise_usage():
    return_dict = {}
    if request.method == 'GET':
	usage_url = APP_URL + "/workshops?status_id=3"
	ws_usage_response = requests.get(usage_url)
	try:
	    if ws_usage_response.ok:
		ws = ws_usage_response.text
		ws_dict = json.loads(ws)
		#print len(ws_dict)
		inst_ws_usage_dict= []
		for workshop in ws_dict:
		   # print"here"
		    user_id = workshop['user']['id']
		    user_url = APP_URL + "/users?id=" + str(user_id)
		    user_response = requests.get(user_url)
		    try:
			if user_response.ok:
			    users = user_response.text
			    users_dict = json.loads(users)
			    if users_dict[0]['role']['id'] == 2 and \
			      users_dict[0]['institute_name'] is not None:
			       # print "users_dict = %s" % users_dict[0]
				institute_name = users_dict[0]['institute_name']
			       # print "institute_name = %s" % institute_name
				if workshop['experiments_conducted'] is None:
				    usage = 0
				else:
				    usage = workshop['experiments_conducted']
				if institute_name in return_dict:
				    return_dict[institute_name]['usage'] += \
				      usage
				    return_dict[institute_name]['workshops'] += 1
				else:
				    temp_dict = {}
				    temp_dict['usage'] = usage
				    temp_dict['workshops'] = 1
				    nc_count = get_nodal_center_count_for_OC(user_id)
				    temp_dict['nc_count'] = nc_count
				    return_dict[institute_name] = temp_dict

			    elif users_dict[0]['role']['id'] == 3:
			      #  print"NC user dict = %s" % users_dict[0]
				ncd_url = APP_URL + "/nodal_coordinator_details?user_id=" + str(user_id)

				ncd_response = requests.get(ncd_url)
				try:
				    if ncd_response.ok:
					nc_users = ncd_response.text
					nc_users_dict = json.loads(nc_users)
					institute_name = nc_users_dict[0]['created_by']['institute_name']
			       #         print "NC institute_name = %s" % institute_name
					if workshop['experiments_conducted'] is None:
					    usage = 0
					else:
					    usage = workshop['experiments_conducted']
					if institute_name in return_dict:
					    return_dict[institute_name]['usage'] += \
					      usage
					    return_dict[institute_name]['workshops'] += 1
					else:
					    temp_dict = {}
					    temp_dict['usage'] = usage
					    temp_dict['workshops'] = 1
					    nc_count = get_nodal_center_count_for_OC(nc_users_dict[0]['created_by']['id'])
					    temp_dict['nc_count'] = nc_count
					    return_dict[institute_name]  = temp_dict
				except Exception as err:
				    raise err
		    except Exception as err:
			raise err
	except Exception as err:
	    raise err

    return jsonify(return_dict)

def get_nodal_center_count_for_OC(user_id):
    nc_count_url = APP_URL + "/nodal_centres?created_by_id=" + str(user_id)
    try:
	nc_count_response = requests.get(nc_count_url)
	if nc_count_response.ok:
	    return len(json.loads(nc_count_response.text))
	else:
	    raise Exception("Cannot get nodal center count")

    except Exception as err:
	raise err


@api.route('/get_outreach_usage', methods=['GET'])
def get_outreach_portal_usage():
    if request.method == 'GET':
	usage_url = APP_URL + "/workshops?status_id=3"
	ws_usage_response = requests.get(usage_url)
	try:
	    if ws_usage_response.ok:
		ws_usages = ws_usage_response.text
		ws_usage_dict = json.loads(ws_usages)
		usage=0
		participants_attended=0
		for i in range(0, len(ws_usage_dict)):
		    if ws_usage_dict[i]['experiments_conducted'] != None and \
			ws_usage_dict[i]['participants_attended'] != None:
			usage += ws_usage_dict[i]['experiments_conducted']
			participants_attended += ws_usage_dict[i]['participants_attended']
		op_usage_data = {"usage": usage, 'participants_attended': participants_attended}
		return jsonify(op_usage_data)

	except Exception as err:
	    current_app.logger.error("Exception = %s" % str(err))
	    raise err

@api.route('/get_outreach_analytics', methods=['GET'])
def get_outreach_portal_analytics():
    if request.method == 'GET':
	nc_url = APP_URL + "/nodal_centres"
	ws_url = APP_URL + "/workshops?status_id=3"
	upcoming_ws_url = APP_URL + "/workshops?status_id=1"
	usage_url = APP_URL + "/get_outreach_usage"
	nc_response = requests.get(nc_url)
	ws_response = requests.get(ws_url)
	upcoming_ws_response = requests.get(upcoming_ws_url)
	ws_usage_response = requests.get(usage_url)
	try:
	    if nc_response.ok and ws_response.ok and ws_usage_response.ok and \
		upcoming_ws_response.ok:
		nodal_centres = nc_response.text
		nodal_centre_dict = json.loads(nodal_centres)
		workshops = ws_response.text
		workshop_dict = json.loads(workshops)
		upcoming_workshops = upcoming_ws_response.text
		upcoming_workshop_dict = json.loads(upcoming_workshops)

		ws_usages = ws_usage_response.text
		ws_usage_dict = json.loads(ws_usages)
		op_anaytics_data = {"nodal_centres": len(nodal_centre_dict),
				 "workshops": len(workshop_dict),
				 "upcoming_workshops": len(upcoming_workshop_dict),                                               "usage": ws_usage_dict['usage'],
				 "participants_attended": ws_usage_dict['participants_attended'],
				    }
		return jsonify(op_anaytics_data)
	except Exception as err:
	    current_app.logger.error("Exception = %s" % str(err))
	    raise err

@api.route('/upload_reference_documents/<id>', methods=['GET', 'POST'])
def save_reference_documents(id):
    if request.method == 'GET':
	return '''
	<!doctype html>
	<title>Upload new File</title>
	<h1>Upload new File</h1>
	<form action="" method=post enctype=multipart/form-data>
	<p><input type=file name=file>
	<input type=submit value=Upload>
	</form>
	'''

    if request.method == 'POST':
	url = APP_URL + "/reference_documents/"\
	      + id
	response = requests.get(url)

	file = request.files['file']
	if response.ok:
	    file_path = upload_file(file, url)
	    return file_path
	else:
	    return "No entry for 'ReferenceDocuments' entity with given id"


@api.route('/upload_workshop_reports/<id>', methods=['GET', 'POST'])
def save_workshop_documents(id):
    if request.method == 'GET':
	return '''
	<!doctype html>
	<title>Upload new File</title>
	<h1>Upload new File</h1>
	<form action="" method=post enctype=multipart/form-data>
	<p><input type=file name=file>
	<input type=submit value=Upload>
	</form>
	'''
    if request.method == 'POST':
	url = APP_URL + "/workshop_reports/"\
	      + id
	response = requests.get(url)

	file = request.files['file']
	if response.ok:
	    file_path = upload_file(file, url)
	    return file_path
	else:
	    current_app.logger.debug("No entry for 'WorkshopReports' entity with given id, response code = %s" % response)
	    return "No entry for 'WorkshopReports' entity with given id"

def allowed_file(filename):
    return '.' in filename and \
	filename.rsplit('.', 1)[1] in set(ALLOWED_FILE_EXTENSIONS)


def upload_file(file, url):
    if file and allowed_file(file.filename):
	filename = secure_filename(file.filename)
	current_app.logger.debug("filename = %s" %
				 filename)
	outreach_directory_path = os.path.dirname(os.path.abspath(__file__))
	current_app.logger.debug("outreach_directory_path = %s" %
				 outreach_directory_path)
	dir_path = outreach_directory_path + UPLOAD_DIR_PATH
	current_app.logger.debug("dir_path = %s" %
				 dir_path)
	timestamp = datetime.utcnow().strftime("-%Y-%m-%d-%H-%M-%S.")
	file_name = filename.split(".")
	new_file_name = "%s%s%s" % (file_name[0], timestamp, file_name[1])    
	current_app.logger.debug("new_file_name = %s" %
				 new_file_name)

	file_path = "%s%s" % (dir_path, new_file_name)
	current_app.logger.debug("file_path = %s" %
				 file_path)

	db_path = "%s%s" % (UPLOAD_DIR_PATH, new_file_name)
	current_app.logger.debug("db_path = %s" %
				 db_path)
	try:
	    file.save(file_path)                   
	    current_app.logger.debug("file saved successfully")      
	except Exception, e:
	    response = requests.delete(url, headers= {'email' : session['email'], 'key' : session['key']})
	    current_app.logger.error("Error unable to save file: " + str(e))
	    abort(500, 'error is %s' % (str(e)))

	path = {'path': db_path}
	try:
	    response = requests.put(url, data=path)
	    if response.status_code == 200:
		current_app.logger.error("db path is set successfully")
	    else:
		current_app.logger.debug("Unable to save file path in database")
		response = requests.delete(url, headers= {'email' : session['email'], 'key' : session['key']}) # Delete the record in database

		if response.status_code == 200:
		    current_app.logger.error("Sucessfully deleted record from database")
		    ##delete the file
		    delete_file(file_path)
		    abort(500)
		else:
		    current_app.logger.error("Failed to delete record from database")
		    abort(500)
	except Exception, e:
	    abort(500, 'error is %s' % (str(e)))

	return file_path
    else:
	return "file format is not in Allowed Extensions"

def delete_file(file_path):
    try:
	if os.path.exists(file_path):
	    os.remove(file_path)
	    current_app.logger.debug("Successfully deleted file from filesystem")
    except Exception, e:
	current_app.logger.error(" IO Error: no such file or directory")
	abort(500, 'error is %s' % (str(e)))

# query an entity
# =/<:entity>s?query_param1=val1&query_param2=val2&..query_paramn=valn=
@api.route('/<entity>', methods=['GET'])
def query_an_entity(entity):
    if entity not in entity_pairs:
	current_app.logger.error("Entity %s is not valid " % entity)    
	abort(400, 'Entity %s is not valid.' % entity)

    curr_entity = entity_pairs[entity]['entity_class']
    arg_tuple_list = request.args.lists()
    if not arg_tuple_list:
	return jsonify_list([i.to_client() for i in curr_entity.get_all()])
    else:
	query = curr_entity.query
	filters = []
	for arg_tuple in arg_tuple_list:
	    args = arg_tuple[0].split('.')
	    values = arg_tuple[1][0].split(',')
	    filters.append(create_filters(entity_pairs[entity], \
					  curr_entity, args, values))
	for filter in filters:
	    query = query.filter(filter)
	entities = query.all()
	return jsonify_list([ent.to_client() for ent in entities])

def create_filters(entity_map, curr_entity, args, values):
    if len(args) == 1:
	try:
	    return getattr(curr_entity, args[0]).in_(values)
	except Exception, e:
	    current_app.logger.error("Error is %s" % (str(e)))          
	    abort(400, 'error is %s' % (str(e)))
    else:
	result = filter(lambda item: item['name'] == args[0],
			entity_map['attributes'])
	if not result:
	    current_app.logger.error("%s is not attribute of %s"  % (args[0], str(entity_map['entity_class'])))         
	    abort(400, '%s is not attribute of %s' %
		  (args[0], str(entity_map['entity_class'])))

	entity_map = args[0]
	if result[0]['relationship'] == 'one':
	    try:
		return getattr(curr_entity, args[0]).has(
		    create_filters(entity_map, result[0]['class'], \
				   args[1:], values))
	    except Exception, e:
		current_app.logger.error("Error is %s"  % (str(e)))             
		abort(400, 'error is %s' % (str(e)))
	else:
	    try:
		return getattr(curr_entity, args[0]).any(
		    create_filters(entity_map, result[0]['class'], \
				   args[1:], values))
	    except Exception, e:
		current_app.logger.error("Error is %s"  % (str(e)))             
		abort(400, 'error is %s' % (str(e)))

@api.route('/<entity>/<id>', methods=['GET'])
def get_specific_entity(entity, id):
    if entity not in entity_pairs:
	current_app.logger.error("Entity %s is not valid."  % entity)           
	abort(400, 'Entity %s is not valid.' % entity)
    curr_entity = entity_pairs[entity]['entity_class']
    record = curr_entity.get_by_id(id)
    if not record:
	current_app.logger.error("No entry for %s with id: %s found."  % (entity, id))          
	abort(404, "No entry for %s with id: %s found." % (entity, id))

    return jsonify(record.to_client())
    

entity_map_types = {
    'roles': {
        'entity': Role,
        'types': {
            'name': Name
        }
    },
    'users': {
        'entity': User,
        'types': {
            'name': Name,
            'email': Email,
            'institute_name': str,
            'role': Role,
            'last_active': str,
            'created': str
        }
    },
    'reference_documents': {
        'entity': ReferenceDocument,
        'types': {
            'name': str,
            'path': str,
            'user': User
        }
    },
    'status': {
        'entity': Status,
        'types': {
            'name': Name
        }
    },
    'workshops': {
        'entity': Workshop,
        'types': {
            'name': str,
            'location': str,
            'user': User,
            'participating_institutes': str,
            'no_of_participants_expected': int,
            'participants_attended': int,
            'no_of_sessions': int,
            'duration_of_sessions': str,
            'disciplines': str,
            'labs_planned': int,
            'experiments_conducted': int,
            'other_details': str,
            'cancellation_reason': str,
            'gateway_ip': str,
            'version': str,
            'not_approval_reason': str,
            'created': datetime,
            'last_updated': str,
            'status': Status,
            'date': str
        }
    },
   'nodal_centres': {
        'entity': NodalCentre,
        'types': {
            'created_by': User,
            'name': str,
            'location': str,
            'pincode': str,
            'longitude': str,
            'lattitude': str
        }
    },
 
   'nodal_coordinator_details': {
        'entity': NodalCoordinatorDetail,
        'types': {
            'user': User,
            'created_by': User,
            'nodal_centre':NodalCentre,
            'last_updated': str,
            'created': datetime,
            'target_workshops': int,
            'target_participants': int,
            'target_experiments': int
        }
    },
     'workshop_reports': {
        'entity': WorkshopReport,
        'types': {
            'name':str,
            'path': str,
            'workshop': Workshop
        }
    }

}


def delete_record(entity, id):
    record = entity.get_by_id(id)
    if not record:
        current_app.logger.debug("Record not found with id %s..." % id)
        abort(404, 'No %s exists with id %s' % (entity, id))
    else:
        try:
            if entity.__name__=="WorkshopReport" or entity.__name__=="ReferenceDocument":
                if record.path==None:
                    record.delete()
    	            current_app.logger.debug("The record of %s entity deleted sucessfully..." % entity)

                else:
                    dir_path=os.path.dirname(os.path.abspath(__file__))
                    file_loc=dir_path+record.path
                    os.remove(file_loc)
                    current_app.logger.debug("Deleted file from location %s:" % file_loc)

                    record.delete()
                    current_app.logger.debug("Deleted record of %s Entity with id: %s" % (entity, id))
            else:
                record.delete()
                current_app.logger.debug("Deleted record of %s Entity with id: %s" % (entity, id))

        except Exception, e:
	    current_app.logger.error("Error is %s"  % (str(e)))
            abort(500, str(e))

    return jsonify(id=id, status="success")


# take a constructor, and attr name and the actual attribute and convert the
# attribute value to its actual type
def typecast_compound_item(const, attr, val):
    if 'id' not in val:
        abort(400, "id attr has to be present in %s:%s" % (attr,
                                                           val))
    try:
        new_val = const.get_by_id(val['id'])
    except TypeError:
        current_app.logger.error("%s is not a valid %s"  % (val, attr))
        abort(400, '%s is not a valid %s' % (val, attr))

    if not new_val:
        current_app.logger.error("id %s of %s is not found"  % (val['id'], attr))
        abort(404, 'id %s of %s is not found' % (val['id'], attr))
    return new_val


# take a constructor, and attr name and the actual attribute and convert the
# attribute value to its actual type
def typecast_item(const, attr, val):
    if type(val) is dict:
        new_val = typecast_compound_item(const, attr, val)
        return new_val

    try:
        new_val = const(val)
    except TypeError:
        current_app.logger.error("%s is not a valid %s"  % (val, attr))
        abort(400, '%s is not a valid %s' % (val, attr))

    return new_val


def typecast_data(entity, data):
    updated_data = {}
    for attr, val in data.iteritems():
        if attr not in entity_map_types[entity]['types']:
            current_app.logger.debug("%s attribute not in %s"  % (attr, entity))
            abort(400, '%s attribute not in %s' % (attr, entity))
        const = entity_map_types[entity]['types'][attr]

        if type(val) is list:
            new_val = map(lambda item: typecast_item(const, attr, item), val)
        else:
            new_val = typecast_item(const, attr, val)

        updated_data[attr] = new_val

    return updated_data


def update_record(entity_name, entity, id):
    record = entity.get_by_id(id)

    if not record:
       	current_app.logger.debug("No %s with id %s"  % (entity_name, id))
        abort(404, "No %s with id %s" % (entity_name, id))

    data = parse_request(request)
    if not data or type(data) is not dict:
    	current_app.logger.debug("The data should be in JSON format")
        abort(400, "The data should be in JSON format")

    data = typecast_data(entity_name, data)

    try:
        record.update(**data)
    	current_app.logger.debug("The data of %s entity updated sucessfully..." % entity_name)
    except Exception, e:
	current_app.logger.error("Error is %s"  % (str(e)))
        abort(500, str(e))

    return jsonify(record.to_client())


@api.route('/<entity>/<id>', methods=['PUT', 'DELETE'])
def modify_entity(entity, id):
    email = str(request.headers.get('email'))
    key = str(request.headers.get('key'))
    if entity == "reference_documents" or entity == "workshop_reports":
        if email is None or key is None:
            abort(401, "Unauthorized Credentials")
    else:
        if 'email' not in session:
            abort(401, "Unauthorized Credentials")

    #email = str(request.headers.get('email'))
    #key = str(request.headers.get('key'))
    #if email is None or key is None:
    #    abort(401, "Unauthorized Credentials")
  
    #if 'email' not in session:
    #    abort(401, "Unauthorized Credentials")
    
    if entity not in entity_map_types:
        current_app.logger.debug("Entity %s not in entity map types"  % entity)
        abort(400, 'Entity %s is not valid.' % entity)

    curr_entity = entity_map_types[entity]['entity']

    if request.method == 'DELETE':
        status = delete_record(curr_entity, id)
        return status

    if request.method == 'PUT':
        current_app.logger.debug("Updating record of %s Entity with id: %s" % (curr_entity, id))
        status = update_record(entity, curr_entity, id)
        return status
    

def create_record(entity_name, entity):

    data = parse_request(request)
    if not data or type(data) is not dict:
        current_app.logger.debug("Unsupported data...The data should be in JSON format")
        abort(400, "The data should be in JSON format")

    data = typecast_data(entity_name, data)

    try:
        new_record = entity(**data)
        new_record.save()
    except Exception, e:
        current_app.logger.error("Error is %s" % (str(e)))
        abort(500, str(e))

    return jsonify(new_record.to_client())

@api.route('/<entity>', methods=['POST'])
def create_entity(entity):
    email = str(request.headers.get('email'))
    key = str(request.headers.get('key'))
    if entity == "reference_documents" or entity == "workshop_reports":
        if email is None or key is None:
            abort(401, "Unauthorized Credentials")
    else:
        if 'email' not in session:
            abort(401, "Unauthorized Credentials")
    #if email is None or key is None:
    #    abort(401, "Unauthorized Credentials")
    
    #if 'email' not in session:
    #    abort(401, "Unauthorized Credentials")
    
    if entity not in entity_map_types:
        current_app.logger.debug("Entity %s not present in entity map types"  % entity)
        abort(400, 'Entity %s is not valid.' % entity)

    curr_entity = entity_map_types[entity]['entity']
    current_app.logger.debug("current entity is %s"  % curr_entity)	

    status = create_record(entity, curr_entity)
    current_app.logger.debug("status is %s"  % status)	

    return status
