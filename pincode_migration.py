
import requests
import json
import yaml

src_url = "http://outreach-map.base4.vlabs.ac.in/nodal_centres"
src_url_by_id = src_url+"/"
dest_url = "http://outreach-map-test.base4.vlabs.ac.in/nodal_centres/"
ncs = requests.get(src_url).json()

for nc in ncs:
     a_url = src_url_by_id + str(nc['id'])
     nc = requests.get(a_url).json()
     nc_x = yaml.safe_load(json.dumps(nc))
     name = nc_x['name']
     location = nc_x['location']
     pincode = nc_x['pincode']
     lattitude = nc_x['lattitude']
     longitude = nc_x['longitude']

     payload = {'name': name,
                'location': location,
                'pincode' : pincode,
                'lattitude': lattitude,
                'longitude': longitude
               }
     headers = {'email':'dummyuser@gmail.com', 'key':'vlead123'}
     b_url  = dest_url+str(nc['id'])
     response = requests.put(b_url, data=json.dumps(payload),
                                  headers=headers)
     print nc['id']
     print response.status_code
