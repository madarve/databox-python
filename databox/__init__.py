import requests
from requests.auth import HTTPBasicAuth
from os import getenv
from json import dumps as json_dumps


class Client(object):
    push_token = None
    push_host = 'https://push2new.databox.com'

    class MissingToken(Exception):
        pass

    class KPIValidationException(Exception):
        pass

    def __init__(self, token=None):
        self.push_token = token
        if self.push_token is None:
            self.push_token = getenv('DATABOX_PUSH_TOKEN', None)

        if self.push_token is None:
            raise self.MissingToken('Push token is missing!')

        self.push_host = getenv('DATABOX_PUSH_HOST', self.push_host)

    def process_kpi(self, **args):
        key = args.get('key', None)
        if key is None:
            raise self.KPIValidationException('Missing "key"')

        value = args.get('value', None)
        if value is None:
            raise self.KPIValidationException('Missing "value"')

        item = {("$%s" % args['key']): args['value']}

        date = args.get('date', None)
        if date is not None:
            item['date'] = date

        attributes = args.get('attributes', None)
        if attributes is not None:
            item = dict(item.items() + attributes.items())

        return item

    def _push_json(self, data=None, path="/"):
        if data is not None:
            data = json_dumps(data)

        response = requests.post(
            self.push_host + path,
            auth=HTTPBasicAuth(self.push_token, ''),
            headers={'Content-Type': 'application/json'},
            data=data
        )

        return response.json()

    def push(self, key, value, date=None):
        return self._push_json({
            'data': [self.process_kpi(key=key, value=value, date=date)]
        })['status'] == 'ok'

    def insert_all(self, rows):
        return self._push_json({
            'data': [self.process_kpi(**row) for row in rows]
        })['status'] == 'ok'

    def last_push(self, number=1):
        return self._push_json(path='/lastpushes/{n}'.format(**{'n': number}))


def push(key, value, date=None, token=None):
    return Client(token).push(key, value, date)


def insert_all(rows=[], token=None):
    return Client(token).insert_all(rows)


def last_push(token=None):
    return Client(token).last_push()