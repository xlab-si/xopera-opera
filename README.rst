Introduction
============

``opera`` aims to be a lightweight orchestrator compliant with `OASIS TOSCA`_.
The initial compliance is with the `TOSCA Simple Profile YAML v1.2`_.

.. _OASIS TOSCA: https://www.oasis-open.org/committees/tc_home.php?wg_abbrev=tosca
.. _TOSCA Simple Profile YAML v1.2: https://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.2/os/TOSCA-Simple-Profile-YAML-v1.2-os.html

Prerequisites
-------------

``opera`` works in Python 3, preferably in a virtual environment. In a typical
modern Linux environment, we should already be set. In Ubuntu, however, we might
need to run the following commands:

::

  $ sudo apt update
  $ sudo apt install -y python3-venv python3-wheel python-wheel-common

Installation
------------

Initiate an environment for the `opera` orchestrator and for exploring the
orchestration. E.g.::

  $ mkdir xOpera
  $ cd xOpera

Obtain the latest version of the opera orchestrator::

  xOpera $ git clone https://github.com/xlab-si/xopera-opera.git

Start the Python 3 virtual environment::

  xOpera $ python3 -m venv venv
  xOpera $ . venv/bin/activate
  (venv) xOpera $ pip install wheel
  (venv) xOpera $ pip install -e git+https://github.com/ansible/ansible.git@devel#egg=ansible
  (venv) xOpera $ pip install -e xopera-opera

OpenStack client setup
----------------------

The service template in the ``examples/`` folder require the OpenStack client
to be installed and the environment properly configured. To install the
client, issue the following commands in our active virtual environment::

  (venv) xOpera $ pip install openstacksdk python-openstackclient

Log into OpenStack and download rc file content form the ``Access & Security``
-> ``API Access`` page and place it into ``openstack.rc`` file.

At the start of each session (e.g., when we open a new command line console),
source the ``openstack.rc`` file::

  (venv) xOpera $ ./openstack.rc

We need to supply our OpenStack password when prompted. To test credentils that
we just entered, we can run::

  (venv) xOpera $ openstack image list

If this produced something reasonable on the output, credentials are valid and
we can deploy our first TOSCA service template. If the command failed, we can
set our password again by running::

  (venv) xOpera $ ./openstack.rc

Before we can use ``opera``, we must import ssh key into our OpenStack under
``Access & Security`` -> ``Key Pairs`` -> ``Import Key Pair``. We must make sure
we use the correct name as instructed in the message.

Using opera
-----------

To see the usage of the ``opera`` tool, call the tool without parameters::

  (venv) xOpera $ opera
  (venv) xOpera $ opera deploy

Use the blueprint in the ``examples/`` to test the orchestrator::

  (venv) xOpera $ cd xopera-opera/examples
  (venv) examples $ opera deploy example-deployment service.yaml
