"""
Skeleton implementation of NB API class plus mocking
"""

from abc import ABC, abstractmethod
import logging
from uuid import uuid1 as uuid
import datetime

log = logging.getLogger(__name__)

class RequestError(Exception):
    def __init__(self, message):
        self.message = message

class NBAPI(ABC):
    '''
    ABC to assert that the mock and real implementations are compatible
    '''
    @abstractmethod
    def sample_people(self):
        pass

    @abstractmethod
    def create_person(self, data):
        pass

    @abstractmethod
    def update_person(self, data):
        pass

    @abstractmethod
    def delete_person(self, pid):
        pass

    @abstractmethod
    def sample_webhooks(self):
        pass

    @abstractmethod
    def create_webook(self, data):
        pass

    @abstractmethod
    def create_contact(self, data):
        pass

    @abstractmethod
    def sample_contact_types(self):
        pass


class NBReal(NBAPI):
    '''
    Actual API that makes live requests
    '''
    def __init__(self, nation, api_key):
        self.base_url = 'https://{}.nationbuilder.com/api/v1'.format(nation)
        self.params = {'access_token': api_key}

    @staticmethod
    def _assert_response_ok(response):
        if response.status_code >= 300 or response.status_code < 200:
            raise RequestError('Request failed. Server sent {}: {}'.format(action, response.status_code, response.text))

    def _post(self, ep, data):
        response = requests.post(base_url + ep, params=self.params, json=data)
        self._assert_response_ok(response)
        return response

    def _put(self, ep, data):
        response = requests.put(base_url + ep, params=self.params, json=data)
        self._assert_response_ok(response)
        return response

    def _delete(self, ep):
        response = requests.delete(base_url + ep, params=self.params)
        self._assert_response_ok(response)

    def sample_people(self):
        response = self._get('/people?limit=10')
        return response['results']  # no paging; this is just a sample

    def create_person(self, data):
        response = self._post('/people', {'person': data})
        return response['person']

    def update_person(self, data):
        response = self._put('/people/{}'.format(data['id']), {'person': data})
        return response['person']

    def delete_person(self, pid):
        self._delete('/people/{}'.format(pid))

    def sample_webhooks(self):
        response = self._get('/webhooks?limit=10')
        return response['results']  # no paging; this is just a sample

    def create_webook(self, data):
        response = self._post('/webooks', {'webhook': data})
        return response['webhook']

    def create_contact(self, data):
        response = self._post('/people/{}/contacts'.format(data['person_id'], {'contact': data}))
        return response['contact']

    def sample_contact_types(self):
        response = self._get('/settings/contact_types?limit=10')
        return response['results']  # no paging; this is just a sample

class NBMock(NBAPI):
    '''
    Mock API that does not make requests
    '''
    def __init__(self):
        self.people = {}
        self.last_people_id = 0
        self.webhooks = {}
        self.contact_types = [
            {'id': 1, 'name': 'Initial outreach'},
            {'id': 2, 'name': 'Final outreach'},
        ]

    def sample_people(self):
        return self.people.values()

    def sample_webhooks(self):
        return self.webhooks.values()

    def create_person(self, data):
        self.last_people_id = self.last_people_id + 1
        data['id'] = self.last_people_id
        data['contacts'] = {}
        data['last_call_id'] = -1
        data['last_contacted_at'] = None
        self.people[self.last_people_id] = data
        return data

    def create_webook(self, data):
        webhook_id = uuid()  # NB id doesn't actually appear to be a UUID
        data['id'] = webhook_id
        self.webhooks[webhook_id] = data
        return data

    def update_person(self, data):
        pid = data['id']
        if pid in self.people:
            self.people[pid].update(data)
            return self.people[pid]
        else:
            raise RequestError('No such person id {}. IDs: {}'.format(pid, self.people.keys()))

    def delete_person(self, pid):
        if pid in self.people:
            del self.people[pid]
        else:
            raise RequestError('No such person id {}'.format(pid))

    def create_contact(self, data):
        pid = data['person_id']
        if pid in self.people:
            person_data = self.people[pid]
            cid = person_data['last_call_id'] + 1
            data['contact_id'] = cid
            data['created_at'] = datetime.datetime.utcnow().isoformat(u'T', 'seconds') + 'Z'
            person_data['last_call_id'] = cid
            person_data['last_contacted_at'] = data['created_at']
            person_data['contacts'][cid] = data
            return data
        else:
            raise RequestError('No such person id {}'. format(pid))

    def sample_contact_types(self):
        return self.contact_types
