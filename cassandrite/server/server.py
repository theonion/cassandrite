# stdlib
import sys

# third party
from cassandra.cluster import Cluster
from cqlengine import connection
from cqlengine.management import sync_table
from twisted.internet import reactor, endpoints
from twisted.python import log
from twisted.web import server

# local modules
from models import Event
from resources import EventResource


# logging - to stdout
log.startLogging(sys.stdout)

# connect to cassandra
connection.setup(['127.0.0.1'], 'oniontv')
sync_table(Event)
cluster = Cluster()
session = cluster.connect('oniontv')

# run server
endpoints.serverFromString(reactor, 'tcp:8080').listen(server.Site(EventResource()))
reactor.run()
