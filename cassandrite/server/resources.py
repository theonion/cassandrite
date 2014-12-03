# stdlib
import json

# pip
from twisted.web import resource

# local
from configurations import config_store
from helpers import get_floor, get_ceiling, datetime_to_unix
from models import Event


class EventResource(resource.Resource):
    isLeaf = True

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
            request.setResponseCode(400)
            request.setHeader('content-type', 'application/json')
            return json.dumps(errors)

        # get matching paths
        events = Event.objects.filter(path=path)
        if len(events):
            # get greatest floor
            event = sorted(events, key=lambda e: e.floor, reverse=True)[0]
        else:
            event = Event(path=path)

        # check floor/ceiling of event
        if (event.ceiling > time >= event.floor) is False:
            # create new event
            event = Event(path=path, data=data)

            # determine floor/ceiling from configs
            config = config_store.get(path)
            if not config:
                errors['config'] = ['no rules found for given path']
                request.setResponseCode(400)
                request.setHeader('content-type', 'application/json')
                return json.dumps(errors)
            rule = config.get_primary_rule()
            floor = get_floor(time, rule)
            ceiling = get_ceiling(floor, rule)

            # set times and data
            event.time = datetime_to_unix(floor)
            event.floor = datetime_to_unix(floor)
            event.ceiling = datetime_to_unix(ceiling)
            event.data = data

            # save
            event.save()

        else:
            # update event
            event.data += data
            event.update()

        # return
        request.setResponseCode(204)
        request.setHeader('content-type', 'application/json')
        return ''
