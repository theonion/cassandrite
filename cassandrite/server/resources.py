# stdlib
import json

# pip
from twisted.web import resource

# local
from configurations import config_store
from helpers import get_floor, get_ceiling, get_ttl, datetime_to_unix
from models import Event


class EventResource(resource.Resource):
    isLeaf = True

    def __init__(self, session):
        self.session = session
        self.prepped_query = session.prepare(
            'SELECT * FROM event WHERE path=? AND ceiling=? AND floor=? LIMIT 1 ALLOW FILTERING;')

    def render_GET(self, request):
        events = Event.objects.all()
        count = len(events)
        response = {'meta': {'count': count}, 'objects': []}
        for event in events:
            response['objects'].append(
                {
                    'path': event.path,
                    'time': event.time,
                    'data': event.data,
                    'ceiling': event.ceiling,
                    'floor': event.floor,
                }
            )
        request.setResponseCode(200)
        request.setHeader('content-type', 'application/json')
        return json.dumps(response)

    def render_POST(self, request):
        # set response headers
        request.setHeader('content-type', 'application/json')
        request.setResponseCode(400)

        # parse payload
        payload = json.loads(request.content.getvalue())
        path = payload.get('path')
        time = payload.get('time')
        data = payload.get('data')

        # validate payload
        errors = {}
        if not path:
            errors.setdefault('path', [])
            errors['path'].append('missing value')
        if not time:
            errors.setdefault('time', [])
            errors['time'].append('missing value')
        try:
            time = int(time)
        except (TypeError, ValueError):
            errors.setdefault('time', [])
            errors['time'].append('cannot parse to int')
        if not data:
            errors.setdefault('data', [])
            errors['data'].append('missing value')
        try:
            data = int(data)
        except (TypeError, ValueError):
            errors.setdefault('data', [])
            errors['data'].append('cannot parse to int')

        # bounce here if errors
        if len(errors):
            return json.dumps(errors)

        # get config
        config = config_store.get(path)

        # check config
        if not config:
            errors['config'] = ['no config found matching given path']
            return json.dumps(errors)

        # get rules
        for rule in config.retention_rules:
            # get floor and ceiling for payload
            floor = get_floor(time, rule)
            ceiling = get_ceiling(floor, rule)
            ttl = get_ttl(ceiling, rule)
            print('floor={} ceiling={} ttl={}'.format(floor, ceiling, ttl))

            # format times
            floor = datetime_to_unix(floor)
            ceiling = datetime_to_unix(ceiling)

            # get matching event
            events = Event.objects.filter(path=path)
            events = filter(lambda e: e.floor == floor and e.ceiling == ceiling, [e for e in events])

            if len(events):
                event = events[0]
                event.data += data
                try:
                    event.update()
                except Exception, e:
                    errors['update procedure'] = [str(e)]
                    return json.dumps(errors)

            else:
                # create new
                event = Event.create(path=path, time=ceiling, ceiling=ceiling, floor=floor, data=data)
                try:
                    event.ttl(ttl).save()
                except Exception, e:
                    errors['save procedure'] = [str(e)]
                    return json.dumps(errors)

        # override response code and return
        request.setResponseCode(204)
        return ''
