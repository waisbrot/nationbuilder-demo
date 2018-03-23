#
# Nation Builder developer exercise: Webhooks+Contact


import os
import requests
from flask import Flask, url_for, redirect, request

API_KEY = os.environ.get('API_KEY')
NATION = os.environ.get('NATION')

if API_KEY is None:
	raise SystemExit("Missing API_KEY environment variable. Please set your NationBuilder API key.")
if NATION is None:
	raise SystemExit("Missing NATION environment variable. Please set your NationBuilder slug.")

PARAMS = {"access_token": API_KEY}
API = 'https://{}.nationbuilder.com/api/v1'

app = Flask(__name__)

class NoPersonError(Exception):
    pass

@app.route('/')
def root():
    return redirect(url_for('contact_form'))

@app.route('/contact', methods=['GET'])
def contact_form():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Record a contact</title>
    </head>
    <body>
        <form id="contact_form" method="POST" action="/contact">
            <label for="contact_email">Contact's email</label>
            <input id="contact_email" name="contact_email" type="text">

            <label for="contact_result">Result of the contact</label>
            <select id="contact_result" name="contact_result">
                <option value="MC">Mind-control successfull</option>
                <option value="TF">Subject was wearing foil hat</option>
            </select>
            <input class="submit-button" value="Inform the elders" type="submit">
        </form>
    </body>
    </html>
    '''

@app.route('/contact', methods=['POST'])
def submit_contact():
    return str(request.form['contact_result'])


def lookup_by_email(email):
    result = requests.get(API+'/people/match?email='+email, params=PARAMS)
    if result.status_code >= 200 and result.status_code < 300:
        return result.json()['person']['id']
    else:
        raise NoPersonError(email)
