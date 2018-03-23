from flask import Flask, url_for, redirect, request, render_template, Markup
from .nbapi import NBReal, NBMock, RequestError
import os
import json
import sys
from traceback import format_tb

app = Flask(__name__)

if os.getenv('NB_MOCK', default='false').lower() == 'true':
    api = NBMock()
else:
    api = NBReal(os.environ.get('NATION'), os.environ.get('API_KEY'))

@app.route('/')
def root():
    menu_items = [
        {'name': 'People', 'url': url_for('people_base')},
        {'name': 'Webhooks', 'url': url_for('webhooks_base')},
        {'name': 'Contact', 'url': url_for('contact_base')},
    ]
    return render_template('root.html', links=menu_items)

@app.route('/contact/', methods=['GET'])
def contact_base():
    people = api.sample_people()
    types = api.sample_contact_types()
    return render_template('contact.html', people=people, types=types)

@app.route('/contact/create/', methods=['POST'])
def contact_create():
    contact = {
        'type_id': int(request.form['type_id']),
        'person_id': int(request.form['person_id']),
    }
    try:
        result = api.create_contact(contact)
        pretty_json = json.dumps(result, sort_keys=True, indent=4)
        return render_template('contact_result.html', contact=result, pretty_json=pretty_json)
    except RequestError:
        return _error_page(return_url=url_for('contact_base'))

@app.route('/people/', methods=['GET'])
def people_base():
    return render_template('people.html', people=api.sample_people())

def _error_page(return_url):
    (_, error, stack) = sys.exc_info()
    traceback = ''.join(format_tb(stack))
    return render_template('error.html', error_message=error.message, error_raw=traceback, return_url=return_url)

@app.route('/people/create/', methods=['POST'])
def people_create():
    person = {
        'first_name': request.form['first'],
        'last_name': request.form['last'],
        'email': request.form['email']
    }
    try:
        result = api.create_person(person)
        pretty_json = json.dumps(result, sort_keys=True, indent=4)
        return render_template('person.html', person=result, pretty_json=pretty_json)
    except RequestError:
        return _error_page(return_url=url_for('people_base'))

@app.route('/people/update/', methods=['POST'])
def people_update():
    person = {
        'id': int(request.form['id']),
        'note': request.form['note']
    }
    try:
        result = api.update_person(person)
        pretty_json = json.dumps(result, sort_keys=True, indent=4)
        return render_template('person.html', person=result, pretty_json=pretty_json)
    except RequestError:
        return _error_page(return_url=url_for('people_base'))

@app.route('/people/delete/', methods=['POST'])
def people_delete():
    person_id = int(request.form['id'])
    try:
        api.delete_person(person_id)
        return redirect(url_for('people_base'))
    except RequestError:
        return _error_page(return_url=url_for('people_base'))

@app.route('/webhooks/', methods=['GET'])
def webhooks_base():
    return render_template('webhooks.html', webhooks=api.sample_webhooks())

@app.route('/webhooks/create/', methods=['POST'])
def webhooks_create():
    hook = {
        'version': 4,
        'url': request.form['url'],
        'event': request.form['event'],
    }
    try:
        result = api.create_webhook(hook)
        pretty_json = json.dumps(result, sort_keys=True, indent=4)
        return render_template('wehbook.html', hook=result, pretty_json=pretty_json)
    except RequestError:
        return _error_page(return_url=url_for('webhooks_base'))
