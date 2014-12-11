# cassandrite

a pure python cassandra storage daemon and carbon replacement for graphite


## deprecation warning!

this project is no longer being actively developed. it has a couple decent ideas, which is why i'm 
keeping this open. we have decided to continue moving with [InfluxDB](http://influxdb.com) to store 
our events and metrics data.


## python version

see `runtime.txt`


## requirements

* this project requires a working version on cassndra >= 1.0
* all python requirements can be installed from the requirements file
* as usual, i advise using virtualenv

```bash
$ brew install cassandra
$ pip install -r requirements.txt
```


## running the server

you can use the bin file to run it with the on __required__ argument: a python runtime

```bash
$ ./bin/cassandrite-server /path/to/python
```
