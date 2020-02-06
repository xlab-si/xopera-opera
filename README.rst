Introduction
============

``opera`` aims to be a lightweight orchestrator compliant with `OASIS TOSCA`_.
The current compliance is with the `TOSCA Simple Profile in YAML v1.3`_.

.. _OASIS TOSCA: https://www.oasis-open.org/committees/tc_home.php?wg_abbrev=tosca
.. _TOSCA Simple Profile in YAML v1.3: https://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.3/TOSCA-Simple-Profile-YAML-v1.3.html


Quickstart
----------

The simplest way to test ``opera`` is to install it into virtual environment::

  $ mkdir ~/opera && cd ~/opera
  $ python3 -m venv .venv && . .venv/bin/activate
  (.venv) $ pip install opera

To test if everything is working as expected, we can now try to deploy a
hello-world service::

  (.venv) $ cd examples/hello
  (.venv) $ opera deploy service.yaml

If nothing went wrong, new empty file has been created at
``/tmp/playing-opera/hello/hello.txt``.

To delete the created directory, we can undeploy our stuff by running::

   (.venv) $ opera undeploy

And that is it.


Prerequisites
-------------

``opera`` requires python 3 and a virtual environment. In a typical modern
Linux environment, we should already be set. In Ubuntu, however, we might need
to run the following commands::

  $ sudo apt update
  $ sudo apt install -y python3-venv python3-wheel python-wheel-common


OpenStack client setup
----------------------

Because using OpenStack modules from Ansible playbooks is quite common, we can
install ``opera`` with all required OpenStack libraries by running::

  (.venv) $ pip install -U opera[openstack]

Before we can actually use the OpenStack functionality, we also need to obtain
the OpenStack credentials. If we log into OpenStack and navigate to the
``Access & Security`` -> ``API Access`` page, we can download the rc file with
all required information.

At the start of each session (e.g., when we open a new command line console),
we must source the rc file by running::

  (venv) $ . openstack.rc

After we enter the password, we are ready to start using the OpenStack modules
in playbooks that implement life cycle operations.

Acknowledgement
---------------

This project has received funding from the European Union’s `Horizon 2020`
research and innovation programme under Grant Agreement No. 825040 (RADON).
