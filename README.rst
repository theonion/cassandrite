cassandrite
===========

a pure python cassandra storage daemon and carbon replacement for graphite


python version
--------------

see `runtime.txt`


requirements
------------

this project requires a working version of cassandra: `$ brew install cassandra`

all other requirements can be installed with pip: `$ pip install -r requirements.txt`

i would highly suggest using virtualenv


running the server
------------------

you can use the bin file to run it with one **required** argument with a python runtime: `$ ./bin/cassandrite-server /path/to/venv/bin/python`
