from server.models import Event

from graphite_api.intervals import Interval, IntervalSet
from graphite_api.node import LeafNode


class CassandriteReader(object):
    __slots__ = ('path', )

    def __init__(self, path):
        self.path = path

    def fetch(self, start, end):
        events = Event.objects.filter(path=self.path)
        events = filter(lambda e: end > e.time >= start, [e for e in events])
        _from, _to = min([e.time for e in events]), max([e.time for e in events])
        _skip = _to - _from
        return (_from, _to, _skip), [e.data for e in events]

    def get_intervals(self, events):
        return IntervalSet([Interval(*event.get_interval()) for event in events])


class CassandriteFinder(object):
    __fetch_multi__ = 'cassandrite'

    def find_nodes(self, query):
        pass

    def fetch_multi(self, nodes, start, end):
        pass
