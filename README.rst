=======================
vSphere Reporting Utils
=======================

A set of reporting utilities to get information out of vSphere.

-----
Setup
-----

Currently the easiest way to run these is to do the following:

1. Have python 2.7 installed (tested with 2.7.12).
2. Run `virtualenv $(pwd)/env`.  If you don't have this install it with `pip install virtualenv`.
3. Run `. ./env/bin/activate`.
4. Run `pip install -r requirements.txt`.
5. Run any of the utilities.

---------
Utilities
---------

~~~~~~~~~~~~~~~
report_vm_du.py
~~~~~~~~~~~~~~~

This utility reports the disk usage for VMs and groups it by resource pool,
which is something that's difficult (impossible?) to do through the vSphere
client.

Example:  `python report_vm_du.py -S -H my-vsphere-server.exaple.com -u user@vsphere.local`

Usage:

::
    $ python report_vm_du.py -h
    usage: report_vm_du.py [-h] -H HOST [-o PORT] -u USER [-p PASSWORD] [-S] [-c]
                           [-s SORT]

    Standard Arguments for talking to vCenter

    optional arguments:
      -h, --help            show this help message and exit
      -H HOST, --host HOST  vSphere service to connect to
      -o PORT, --port PORT  Port to connect on
      -u USER, --user USER  User name to use when connecting to host
      -p PASSWORD, --password PASSWORD
                            Password to use when connecting to host
      -S, --disable_ssl_verification
                            Disable ssl host certificate verification
      -c, --cache           Cache results from vSphere
      -s SORT, --sort SORT  Sort order: resource_pool or size
