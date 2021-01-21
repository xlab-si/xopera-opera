.. _Examples:

********
Examples
********

In this section we show some simple examples of orchestrating with xOpera.

=============
Private cloud
=============

OpenStack client setup
######################

This subsection describes `OpenStack and Nginx example <https://github.com/xlab-si/xopera-opera/tree/master/examples/nginx_openstack>`_.
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

.. warning::

    If you want to deploy on a remote VM you should use `OPERA_SSH_USER` env var to tell xOpera as which user you want
    to connect.


============
Public cloud
============

TBD


==========
Serverless
==========


Screencast video
################

This video will help you to get started with xOpera. It also shows an example of deploying a simple image resize
solution to AWS Lambda:

.. raw:: html

    <div style="text-align: center; margin-bottom: 2em;">
    <iframe width="100%" height="350" src="https://www.youtube.com/embed/cb1efi3wnpw" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
    </div>


===
HPC
===


=============================
More tempaltes and blueprints
=============================


TOSCA CSAR
##########

TBD.

This example shows a deployment of the compressed TOSCA CSAR
(available here: :download:`big.csar </files/csars/big/big.csar>`).
The result of the example consisting of deploy, outputs and undeploy operations is shown below.

.. code-block:: console

    (.venv) $ cd xopera-opera/docs/files/csars/big/
    (.venv) $ opera deploy -i inputs.yaml big.csar
    [Worker_0]   Deploying my-workstation1_0
    [Worker_0]   Deployment of my-workstation1_0 complete
    [Worker_0]   Deploying my-workstation2_0
    [Worker_0]   Deployment of my-workstation2_0 complete
    [Worker_0]   Deploying file_0
    [Worker_0]     Executing create on file_0
    [Worker_0]   Deployment of file_0 complete
    [Worker_0]   Deploying hello_0
    [Worker_0]     Executing create on hello_0
    [Worker_0]   Deployment of hello_0 complete
    [Worker_0]   Deploying interfaces_0
    [Worker_0]     Executing configure on interfaces_0
    [Worker_0]     Executing start on interfaces_0
    [Worker_0]   Deployment of interfaces_0 complete
    [Worker_0]   Deploying noimpl_0
    [Worker_0]   Deployment of noimpl_0 complete
    [Worker_0]   Deploying setter_0
    [Worker_0]     Executing create on setter_0
    [Worker_0]   Deployment of setter_0 complete
    [Worker_0]   Deploying test_0
    [Worker_0]     Executing create on test_0
    [Worker_0]   Deployment of test_0 complete
    (.venv) $ opera outputs
    node_output_attr:
      description: Example of attribute output
      value: my_custom_attribute_value
    node_output_prop:
      description: Example of property output
      value: 123
    relationship_output_attr:
      description: Example of attribute output
      value: rel_attr_test123
    relationship_output_prop:
      description: Example of attribute output
      value: rel_prop_test123

    (.venv) $ opera undeploy
    [Worker_0]   Undeploying my-workstation2_0
    [Worker_0]   Undeployment of my-workstation2_0 complete
    [Worker_0]   Undeploying file_0
    [Worker_0]     Executing delete on file_0
    [Worker_0]   Undeployment of file_0 complete
    [Worker_0]   Undeploying interfaces_0
    [Worker_0]     Executing stop on interfaces_0
    [Worker_0]     Executing delete on interfaces_0
    [Worker_0]   Undeployment of interfaces_0 complete
    [Worker_0]   Undeploying noimpl_0
    [Worker_0]   Undeployment of noimpl_0 complete
    [Worker_0]   Undeploying setter_0
    [Worker_0]   Undeployment of setter_0 complete
    [Worker_0]   Undeploying hello_0
    [Worker_0]   Undeployment of hello_0 complete
    [Worker_0]   Undeploying my-workstation1_0
    [Worker_0]   Undeployment of my-workstation1_0 complete
    [Worker_0]   Undeploying test_0
    [Worker_0]   Undeployment of test_0 complete

.. hint::

    You don't need to initialize the CSAR with before the deployment anymore.
    The ``opera init`` command is deprecated since ``opera deploy`` can be used
    directly with both service templates and compressed CSARs.
