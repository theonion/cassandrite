from server.helpers import unix_to_datetime
from server.models import Event

from graphite_api.intervals import Interval, IntervalSet
from graphite_api.node import LeafNode

from cqlengine import connection
from cqlengine.management import sync_table
connection.setup(['127.0.0.1'], 'oniontv')
sync_table(Event)


class CassandriteLeafNode(LeafNode):
    __fetch_multi__ = 'cassandrite'


class CassandriteReader(object):
    __slots__ = ('path', )

    def __init__(self, path):
        """

        :param path:
        """
        self.path = path

    def fetch(self, start, end):
        """

        :param start:
        :param end:
        :return:
        """
        # get all matching events (by path)
        events = Event.objects.filter(path=self.path)
        events = [e for e in events]
        print('events (all): {}'.format(events))

        # filter events by start/stop
        events = sorted(filter(lambda e: end > e.time >= start, [e for e in events]), key=lambda e: e.time)
        print('events (filtered): {}'.format(events))
        _events = dict(((e.floor, e.ceiling), e) for e in events)
        print('_events: {}'.format(_events))

        # get time info
        floor, ceiling = events[0].get_interval()
        floor = unix_to_datetime(floor)
        ceiling = unix_to_datetime(ceiling)
        diff = ceiling - floor
        print('floor: {}'.format(floor))
        print('ceiling: {}'.format(ceiling))
        print('diff: {}'.format(diff))
        events_floor = events[0].floor
        events_ceiling = events[-1].ceiling
        step = diff.total_seconds()
        time_info = (events_floor, events_ceiling, step)
        events_ceiling = unix_to_datetime(events_ceiling)

        # get data from events
        datapoints = []
        print('floor: {}'.format(floor))
        print('eceil: {}'.format(events_ceiling))
        while floor < events_ceiling:
            event = _events.get((floor, ceiling))
            if not event:
                datapoints.append(None)
            else:
                datapoints.append(event.data)
            floor += diff
            ceiling += diff
            print('  floor: {}'.format(floor))

        # return time info and data
        print('time info: {}'.format(time_info))
        print('datapoints: {}'.format(datapoints))
        return time_info, datapoints

    def get_intervals(self, events):
        return IntervalSet(Interval(*events[0].get_interval()))


class CassandriteFinder(object):
    __fetch_multi__ = 'cassandrite'

    def find_nodes(self, query):
        pass

    def fetch_multi(self, nodes, start, end):
        pass
