#
# Nation Builder developer exercise: People
# Based on https://gist.github.com/speg/29906676dfcad63732f3

import os
import requests

API_KEY = os.environ.get('API_KEY')
NATION = os.environ.get('NATION')

if API_KEY is None:
	raise SystemExit("Missing API_KEY environment variable. Please set your NationBuilder API key.")
if NATION is None:
	raise SystemExit("Missing NATION environment variable. Please set your NationBuilder slug.")

PARAMS = {"access_token": API_KEY}
ENDPOINT = 'https://{}.nationbuilder.com/api/v1/{}'.format(NATION, 'people')

request = {
    'person': {
        'first_name': 'Nathaniel',
        'last_name': 'Waisbrot',
        'email': 'nathaniel@waisbrot.net'
    }
}

def assert_response_ok(response, expected_code, action):
    if response.status_code != expected_code:
        raise SystemExit("Failed to {}. Server sent {}: {}".format(action, response.status_code, response.text))

print "Create person"

response = requests.post(ENDPOINT, params=PARAMS, json=request)
assert_response_ok(response, 201, "create person")

print "Update person"

person_id = repr(response.json().get('person').get('id'))
request = {'person': {'mobile': '4103698043'}}
response = requests.put(ENDPOINT+'/'+id, params=PARAMS, json=request)
assert_response_ok(response, 200, "update person")

print "Delete person"

response = requests.delete(ENDPOINT+'/'+id, params=params)
assert_response_ok(response, 204, "delete person")
