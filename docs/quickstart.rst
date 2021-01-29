.. _Quickstart:

**********
Quickstart
**********

====================
Opera CLI Quickstart
====================

After you `installed xOpera CLI <Opera CLI install>`_ into virtual environment you can test if everything is working
as expected. We can now explain how to deploy the `hello-world`_ example.

The hello world TOSCA service template is below.

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

As you can see it is has only one node type defined. This `hello_type` here has two linked implementations that are
actually two TOSCA operations (create and delete) that are implemented in a form of Ansible playbooks. The Ansible
playbook for creation is shown below and it is used to create a new folder and hello world file in `/tmp` directory.

The deployment operation returns the following output:

.. code-block:: console

   (.venv) $ git clone git@github.com:xlab-si/xopera-opera.git
   (.venv) $ cd examples/hello
   (.venv) examples/hello$ opera deploy service.yaml
   [Worker_0]   Deploying my-workstation_0
   [Worker_0]   Deployment of my-workstation_0 complete
   [Worker_0]   Deploying hello_0
   [Worker_0]     Executing create on hello_0
   [Worker_0]   Deployment of hello_0 complete

If nothing went wrong, new empty file has been created at ``/tmp/playing-opera/hello/hello.txt``.

.. code-block:: console

   (venv) examples/hello$ ls -lh /tmp/playing-opera/hello/
   total 0
   -rw-rw-rw- 1 user user 0 Feb 20 16:02 hello.txt

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

To delete the created directory, we can undeploy our stuff by running:

.. code-block:: console

   (venv) examples/hello$ opera undeploy
   [Worker_0]   Undeploying hello_0
   [Worker_0]     Executing delete on hello_0
   [Worker_0]   Undeployment of hello_0 complete
   [Worker_0]   Undeploying my-workstation_0
   [Worker_0]   Undeployment of my-workstation_0 complete

After that the created directory and file are deleted:

.. code-block:: console

   (venv) examples/hello$ ls -lh /tmp/playing-opera/hello/
   ls: cannot access '/tmp/playing-opera/hello/': No such file or directory

.. _hello-world: https://github.com/xlab-si/xopera-opera/tree/master/examples/hello>

======================
xOpera SaaS Quickstart
======================

