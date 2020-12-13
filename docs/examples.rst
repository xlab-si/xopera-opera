.. _Examples:

********
Examples
********

In this section we show some simple examples of orchestrating with xOpera.

Screencast video
################

This video will help you to get started with xOpera. It also shows an example of deploying a simple image resize
solution to AWS:

.. raw:: html

    <div style="text-align: center; margin-bottom: 2em;">
    <iframe width="100%" height="350" src="https://www.youtube.com/embed/cb1efi3wnpw" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
    </div>

Quickstart and hello world
##########################

After you installed xOpera into virtual environment you can test if everything is working as expected. We can now try to
deploy an example `hello-world service <https://github.com/xlab-si/xopera-opera/tree/master/examples/hello>`_ that is
accessible on GitHub.::

  (.venv) $ git clone git@github.com:xlab-si/xopera-opera.git
  (.venv) $ cd examples/hello
  (.venv) $ opera deploy service.yaml

If nothing went wrong, new empty file has been created at ``/tmp/playing-opera/hello/hello.txt``.

To delete the created directory, we can undeploy our stuff by running::

   (.venv) $ opera undeploy


If you want to try out one fast and easy xOpera example you can copy the hello world service template below.

.. code-block:: yaml

    ---
    tosca_definitions_version: tosca_simple_yaml_1_3

    node_types:
      hello_type:
        derived_from: tosca.nodes.SoftwareComponent
        interfaces:
          Standard:
            inputs:
              content:
                default: { get_input: content }
                type: string
            operations:
              create: playbooks/create.yml
              delete: playbooks/delete.yml

    topology_template:
      inputs:
        content:
          type: string
          default: "Hello from Ansible and xOpera!\n"

      node_templates:
        my-workstation:
          type: tosca.nodes.Compute
          attributes:
            private_address: localhost
            public_address: localhost

        hello:
          type: hello_type
          requirements:
            - host: my-workstation
    ...

As you can see it is has only one node type defined. This `hello_type` here has two linked implementations that are actually
two TOSCA operations (create and delete) that are implemented in a form of Ansible playbooks. The Ansible playbook for
creation is shown below and it is used to create a new folder and hello world file in `/tmp` directory.

.. code-block:: yaml

    ---
    - hosts: all
      gather_facts: false

      tasks:
        - name: Create the new folder structure
          file:
            path: /tmp/opera-test/hello
            recurse: true
            state: directory

        - name: Create hello.txt and add content
          copy:
            dest: /tmp/opera-test/hello/hello.txt
            content: "{{ content }}"
    ...

And the playbook for destroying the service is below.

.. code-block:: yaml

    ---
    - hosts: all
      gather_facts: false

      tasks:
        - name: Remove the location
          file:
            path: /tmp/opera-test
            state: absent
    ...

You can initiate xOpera orchestration service with ``opera deploy tosca-template.yml`` in order to start the deployment
and then also ``opera undeploy`` to un-deploy the solution (see image below :ref:`opera_deploy_cli`).

.. _opera_deploy_cli:

.. figure:: /images/opera_deploy_cli.png
    :target: _images/opera_deploy_cli.png
    :width: 80%
    :align: center

    xOpera CLI deployment

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

Outputs
#######

Another example is for `opera outputs <https://github.com/xlab-si/xopera-opera/tree/master/examples/outputs>`_ and
can be tested using the commands below. ::

  (.venv) $ cd examples/outputs
  (.venv) $ opera deploy service.yaml
  (.venv) $ opera outputs

.. tip::

    Take a closer look at more examples here: https://github.com/xlab-si/xopera-opera/tree/master/examples.
    There are also `integration tests <https://github.com/xlab-si/xopera-opera/tree/master/tests/integration>`_
    within opera's GitHub repository which you can also try to run.

TOSCA CSAR
##########

This example shows a deployment of the compressed TOSCA CSAR (available here: :download:`big.csar </files/csars/big/big.csar>`).
The result of the example consisting of deploy, outputs and undeploy operations
is shown below.

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
