.. _Opera CLI:

******************
xOpera CLI (opera)
******************

.. _Opera CLI install:

=================
Installation
=================

This section explains the installation of xOpera orchestrator.

**Prerequisites**


``opera`` requires python 3 and a virtual environment. In a typical modern
Linux environment, we should already be set. In Ubuntu, however, we might need
to run the following commands::

  $ sudo apt update
  $ sudo apt install -y python3-venv python3-wheel python-wheel-common

**Install**


xOpera is distributed as Python package that is regularly published on `PyPI <https://pypi.org/project/opera/>`_.
So the simplest way to test ``opera`` is to install it into virtual environment::

  $ mkdir ~/opera && cd ~/opera
  $ python3 -m venv .venv && . .venv/bin/activate
  (.venv) $ pip install opera


====================================
Secrets and Environment variables
====================================



You can use the following environment variables:

+-----------------------------------+--------------------------------+---------------------------+
| Environment variable              | Description                    | Example value             |
+===================================+================================+===========================+
| | ``OPERA_SSH_USER``              | | Username for the Ansible ssh | | ``ubuntu``              |
| |                                 | | connection to a remote VM    | | (default is ``centos``) |
+-----------------------------------+--------------------------------+---------------------------+
| | ``OPERA_SSH_IDENTITY_FILE``     | | Path to the file containing  | | ``~/.ssh/id_ed25519``   |
| |                                 | | your private ssh key that    | |                         |
| |                                 | | will be used for a           | |                         |
| |                                 | | connection to a remote VM    | |                         |
+-----------------------------------+--------------------------------+---------------------------+
| | ``OPERA_SSH_HOST_KEY_CHECKING`` | | Disable Ansible host key     | | ``false`` or ``f``      |
| |                                 | | checking (not recommended)   | | (not case sensitive)    |
+-----------------------------------+--------------------------------+---------------------------+

.. danger::

   Be very careful with your orchestration secrets (such as SSH private keys,
   cloud credentials, passwords ans so on) that are stored as opera inputs.
   To avoid exposing them don't share the inputs file and the created opera
   storage folder with anyone.

.. tip::

   If you have any problems have a look at the existing issues here: https://github.com/xlab-si/xopera-opera/issues
   or open a new one yourself.



.. _CLI Reference:

===========================
CLI reference and examples 
===========================

``opera`` was  originally meant to be used in a terminal as a client and it
currently allows users to execute the following commands:

+---------------------+----------------------------------------------+
| CLI command         | Purpose and description                      |
+=====================+==============================================+
| ``opera deploy``    | deploy TOSCA service template or CSAR        |
+---------------------+----------------------------------------------+
| ``opera undeploy``  | undeploy TOSCA service template or CSAR      |
+---------------------+----------------------------------------------+
| ``opera validate``  | validate TOSCA service template or CSAR      |
+---------------------+----------------------------------------------+
| ``opera outputs``   | retrieve outputs from service template       |
+---------------------+----------------------------------------------+
| ``opera info``      | show information about the current project   |
+---------------------+----------------------------------------------+
| ``opera package``   | retrieve outputs from service template       |
+---------------------+----------------------------------------------+
| ``opera unpackage`` | retrieve outputs from service template       |
+---------------------+----------------------------------------------+
| ``opera init``      | initialize the service template or CSAR      |
+---------------------+----------------------------------------------+

The commands can be executed in a random order and the orchestrator will warn  and the orchestrator will warn you in case if any problems. Each CLI command is described more in detail in the following sections.


deploy
######

**Name**

``deploy`` - used to deploy and control deployment of the application described in YAML or CSAR.

**Usage**

      .. argparse::
         :filename: src/opera/cli.py
         :func: create_parser
         :prog: opera
         :path: deploy

         The ``--resume/-r`` and ``--clean-state/-c`` options are mutually exclusive.


.. tabs::

   .. tab:: Example

      A simple deployment of TOSCA service template is shown on the next image (:numref:`opera_deploy_service_template_svg`).

      .. _opera_deploy_service_template_svg:

      .. figure:: /images/opera_deploy_service_template.svg
         :target: _images/opera_deploy_service_template.svg
         :width: 100%
         :align: center

         Example of `hello world <https://github.com/xlab-si/xopera-opera/tree/master/examples/hello>`_ template opera deployment.

      Another example (:numref:`opera_deploy_csar_svg`) is below and shows a more
      complex usage of ``opera deploy`` command, deploying the compressed TOSCA
      CSAR with inputs and additional CLI flags. The CSAR is first deployed with
      the supplied `YAML inputs <https://github.com/xlab-si/xopera-opera/tree/master/docs/files/csars/big/inputs.yaml>`_
      (using ``--inputs/-i`` flag) and with two workers (``--workers/-w`` switch)
      that can run two Ansible playbook operations simultaneously. Then the CSAR
      is deployed again (using the ``--clean-state/-c`` option) from the beginning,
      but the execution gets interrupted. Therefore the third deployment is used
      to resume the deployment process from where it was interrupted (using the
      ``--resume/-r`` flag, we also used ``--force/-f`` flag here to skip all
      yes/no prompts).

      .. _opera_deploy_csar_svg:

      .. figure:: /images/opera_deploy_csar.svg
         :target: _images/opera_deploy_csar.svg
         :width: 100%
         :align: center

         The `big CSAR <https://github.com/xlab-si/xopera-opera/tree/master/docs/files/csars/big/big.csar>`_ example deployment.

   .. tab:: Source

   		CLI instructions for example

   		.. code-block:: bash 
   		
   			cd xopera-opera/examples/hello
   			opera deploy service.yaml
   			opera undeploy

   		.. hint:: 
   			Instead of ``service.yaml`` you can deploy a compressed TOSCA CSAR directly with ``deploy`` command.




   .. tab:: Details

      The ``opera deploy`` command is used to initiate the deployment
      orchestration process using the supplied TOSCA service template or the
      compressed TOSCA CSAR. Within this CLI command the xOpera orchestrator
      invokes multiple `TOSCA interface operations <https://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.3/cos01/TOSCA-Simple-Profile-YAML-v1.3-cos01.html#_Toc26969470>`_
      (TOSCA `Standard interface` node operations and also TOSCA `Configure interface`
      relationship operations). The operations are executed in the following order:

      1. ``create``
      2. ``pre_configure_source``
      3. ``pre_configure_target``
      4. ``configure``
      5. ``post_configure_source``
      6. ``post_configure_target``
      7. ``start``

      The operation gets executed if it is defined within the TOSCA service template
      and has a link to the corresponding Ansible playbook.

      After the deployment the following files and folders will be created in
      your opera storage directory (by default that is ``.opera`` and can be
      changed using the ``--instance-path`` flag):

      - ``root_file`` file - contains the path to the service template or CSAR
      - ``inputs`` file - JSON file with the supplied inputs
      - ``instances`` folder - includes JSON files that carry the information about the status of TOSCA node and relationship instances
      - ``csars`` folder contains the extracted copy of your CSAR (created only if you deployed the compressed TOSCA CSAR)






undeploy
#########

**Name**


``undeploy`` - undeploys application; removes all application instances and components.

**Usage**

      .. argparse::
         :filename: src/opera/cli.py
         :func: create_parser
         :prog: opera
         :path: undeploy

         The ``opera undeploy`` command does not take any positional arguments.


.. tabs::

   .. tab:: Example

      A simple undeployment process of TOSCA service template is shown on the
      next image (:numref:`opera_undeploy_svg`). The service template should
      be deployed first and the you can undeploy the solution.

      .. _opera_undeploy_svg:

      .. figure:: /images/opera_cli.svg
         :target: _images/opera_cli.svg
         :width: 100%
         :align: center

         Example showing `hello <https://github.com/xlab-si/xopera-opera/tree/master/examples/hello>`_ template opera undeployment.

      Another example (:numref:`opera_undeploy_csar_svg`) is below and shows a more
      complex usage of ``opera undeploy`` command, undeploying the compressed TOSCA
      CSAR with additional CLI flags. The CSAR was first deployed with the supplied
      `inputs file <https://github.com/xlab-si/xopera-opera/tree/master/docs/files/csars/big/inputs.yaml>`_
      Then the CSAR is undeployed, but the execution gets interrupted. To resume
      the undeployment process from where it was interrupted the ``--resume/-r``
      flag is used.

      .. _opera_undeploy_csar_svg:

      .. figure:: /images/opera_undeploy_csar.svg
         :target: _images/opera_undeploy_csar.svg
         :width: 100%
         :align: center

         The undeployment of the `big CSAR example <https://github.com/xlab-si/xopera-opera/tree/master/docs/files/csars/big/big.csar>`_.

   .. tab:: Source

   		CLI instructions for example

   		.. code-block:: bash 
   		
   			cd xopera-opera/examples/hello
   			opera deploy service.yaml
   			opera undeploy
   			# If undeploy was interrupted
   			opera undeploy -r

   		.. hint:: 
   			Instead of ``service.yaml`` you can deploy a compressed TOSCA CSAR directly with ``deploy`` command.


   .. tab:: Details

      The ``opera undeploy`` command is used to tear down the deployed blueprint.
      Within the undeployment process the xOpera orchestrator invokes two TOSCA
      Standard interface node operations in the following order:

      1. ``stop``
      2. ``delete``

      The operation gets executed if it is defined within the TOSCA service template
      and has a link to the corresponding Ansible playbook.



validate
########

**Name**

Validates the structure of TOSCA template or CSAR

**Usage**
      .. argparse::
         :filename: src/opera/cli.py
         :func: create_parser
         :prog: opera
         :path: validate


.. tabs::

   .. tab:: Example

      The first image below (:numref:`opera_validate_service_template_svg`) shows an example of
      TOSCA service template validation.

      .. _opera_validate_service_template_svg:

      .. figure:: /images/opera_validate_service_template.svg
         :target: _images/opera_validate_service_template.svg
         :width: 100%
         :align: center

         Example showing `attribute mapping <https://github.com/xlab-si/xopera-opera/tree/master/examples/attribute_mapping>`_ template validation.

      The second image (:numref:`opera_validate_csar_svg`) shows an example of
      TOSCA zipped CSAR validation where orchestration YAML inputs file is also supplied.

      .. _opera_validate_csar_svg:

      .. figure:: /images/opera_validate_csar.svg
         :target: _images/opera_validate_csar.svg
         :width: 100%
         :align: center

         Example showing `big <https://github.com/xlab-si/xopera-opera/tree/master/docs/files/csars/big/big.csar>`_ CSAR validation.

   .. tab:: Source

   		CLI instructions for example

   		.. code-block:: bash 
   		
   			cd xopera-opera/examples/attribute_mapping
   			opera validate service yaml

   			opera validate -i inputs.yaml big.csar

   		.. hint:: 
   			Instead of ``service.yaml`` you can deploy a compressed TOSCA CSAR directly with ``deploy`` command.


   .. tab:: Overview

      With ``opera validate`` you can validate any TOSCA template or CSAR and
      find out whether it's properly structured and deployable by opera. At the
      end of this operation you will receive the validation result where opera
      will warn you about TOSCA template inconsistencies if there was any.

   
outputs
#######


**Name**

``outputs`` Print the outputs of the deploy/undeploy.

**Usage**


      .. argparse::
         :filename: src/opera/cli.py
         :func: create_parser
         :prog: opera
         :path: outputs

.. tabs::

   .. tab:: Example

      The image below (:numref:`opera_outputs_service_template_svg`) shows an
      example of retrieving the orchestration outputs after the deployment process.

      .. _opera_outputs_service_template_svg:

      .. figure:: /images/opera_outputs_service_template.svg
         :target: _images/opera_outputs_service_template.svg
         :width: 100%
         :align: center

         Example showing `orchestration outputs <https://github.com/xlab-si/xopera-opera/tree/master/examples/outputs>`_ retrieval.

      Another example in the figure below (:numref:`opera_outputs_csar_svg`)
      shows deploying the TOSCA CSAR with the supplied
      `JSON inputs file <https://github.com/xlab-si/xopera-opera/tree/master/docs/files/csars/small/inputs.json>`_.
      After that the outputs are retrieved and formatted in JSON (using ``--format/-f`` option).

      .. _opera_outputs_csar_svg:

      .. figure:: /images/opera_outputs_csar.svg
         :target: _images/opera_outputs_csar.svg
         :width: 100%
         :align: center

         Example showing `small CSAR <https://github.com/xlab-si/xopera-opera/tree/master/docs/files/csars/small/small.csar>`_ deployment and outputs retrieval.

   .. tab:: Details

      The ``opera outputs`` command lets you access the orchestration outputs
      defined in the TOSCA service template and print them out to the console
      in JSON or YAML format.

  


info
#######

**Name**

``info`` - print the details of current deployment project

**Usage**

      .. argparse::
         :filename: src/opera/cli.py
         :func: create_parser
         :prog: opera
         :path: info


.. tabs::

   .. tab:: Example

      A minimal ``opera info`` example is shown on the image below (:numref:`opera_info_minimal_svg`).
      The service template is deployed first with the debug mode turned on
      (``--verbose/-v`` flag is used, which prints out the inputs and the
      Ansible playbook tasks outputs). Then ``opera info`` command is used to
      print out the information about the current opera project.

      .. _opera_info_minimal_svg:

      .. figure:: /images/opera_info_minimal.svg
         :target: _images/opera_info_minimal.svg
         :width: 100%
         :align: center

         Testing opera info on the `capability_attributes_properties example <https://github.com/xlab-si/xopera-opera/tree/master/examples/capability_attributes_properties>`_.

      A more complex example (:numref:`opera_info_full_svg`) is below and shows a
      combined usage of init, deploy and undeploy commands on the zipped TOSCA
      CSAR with additional CLI flags. After every operation ``opera info`` CLI
      command is called to explore the current status of the project.

      The CSAR was first initialized without the inputs. Those (in `inputs.json file <https://github.com/xlab-si/xopera-opera/tree/master/docs/files/csars/small/inputs.json>`_)
      were supplied within the second deployment step, which gets interrupted
      and this affects the current project state. To resume the deployment
      process from where it was interrupted the ``--resume/-r`` flag is used.
      Then the CSAR is undeployed. The ``opera info`` output is printed
      out in both YAML and JSON formats (here ``--format/-f`` is used).

      .. _opera_info_full_svg:

      .. figure:: /images/opera_info_full.svg
         :target: _images/opera_info_full.svg
         :width: 100%
         :align: center

         The opera info testing on the `small TOSCA CSAR example <https://github.com/xlab-si/xopera-opera/tree/master/docs/files/csars/smal/small.csar>`_.

   .. tab:: Details

      With ``opera info`` user can get the information about the current opera
      project and can access its storage and state. This included printing out
      the path to TOSCA service template entrypoint, extracted CSAR location,
      path to the storage inputs and status/state of the deployment. The output
      can be formatted in YAML or JSON. The created json object looks like this:

      .. code-block:: json

         {
         "service_template":  "string | null",
         "content_root":      "string | null",
         "inputs":            "string | null",
         "status":            "initialized | deployed | undeployed | interrupted | null"
         }


package
#######


**Name**

``package`` create compressed CSAR from the service template represeted with YAML-s.

**Usage**

      .. argparse::
         :filename: src/opera/cli.py
         :func: create_parser
         :prog: opera
         :path: package

.. tabs::

   .. tab:: Example

      A minimal ``opera package`` example is shown on the image below
      (:numref:`opera_package_minimal_svg`). The CSAR is created without any
      optional params and current folder (.) is passed as a source dir. Opera
      then looks for the root level yaml (``service.yaml``) and takes it as
      the entrypoint for ``TOSCA.meta`` (``Entry-Definitions`` YAML keyname).
      Since the output is not specified a random UUID (with the length of 6
      chars) is created and the default zip format is used for the compression.
      The example also has another scenario which features creating a CSAR
      tarball (``tar`` compression format is specified using the
      ``--format/-f`` CLI switch).

      .. _opera_package_minimal_svg:

      .. figure:: /images/opera_package_minimal.svg
         :target: _images/opera_package_minimal.svg
         :width: 100%
         :align: center

         Testing opera package on `intrinsic_functions <https://github.com/xlab-si/xopera-opera/tree/master/examples/intrinsic_functions>`_ and `policy_triggers <https://github.com/xlab-si/xopera-opera/tree/master/examples/policy_triggers>`_ example.

      A more complex example (:numref:`opera_package_full_svg`) is below and
      shows usage of packaging command with additional CLI flags. First a
      zipped CSAR is created from already prepared extracted CSAR structure.
      This CSAR is then validated with ``opera validate`` to show that the
      created CSAR structure is deployable by the opera orchestrator. The
      second part shows the creation of tar compressed TOSCA CSAR. The flags
      ``--service-template/-t``, ``--output/-o`` and ``--format/-f`` are used
      both times.

      .. _opera_package_full_svg:

      .. figure:: /images/opera_package_full.svg
         :target: _images/opera_package_full.svg
         :width: 100%
         :align: center

         Running opera package on the `opera integration tests CSAR examples <https://github.com/xlab-si/xopera-opera/tree/master/tests/integration>`_.


   .. tab:: Details

      The ``opera package`` command is used to create a valid TOSCA CSAR - a
      deployable zip (or tar) compressed archive file. TOSCA CSARs contain the
      blueprint of the application that we want to deploy. The process includes
      packaging together the TOSCA service template and all the accompanying
      files.

      In general, ``opera package`` receives a directory (where user's TOSCA
      templates and other files are located) and produces a compressed
      CSAR file. The command can create the CSAR if there is at least one
      TOSCA YAML file in the input folder. If the CSAR structure is already
      present (if `TOSCA-Metadata/TOSCA.meta` exists and all other TOSCA CSAR
      constraints are satisfied) the CSAR is created without an additional
      temporary directory. And if not, the files are copied to the tempdir,
      where the CSAR structure is created and at the end the tempdir is
      compressed. The input folder is the mandatory positional argument, but
      there are also other command flags that can be used.


unpackage
##########

**Name**

``unpackage`` uncompress CSAR.

**Usage**
      .. argparse::
         :filename: src/opera/cli.py
         :func: create_parser
         :prog: opera
         :path: unpackage

.. tabs::

   .. tab:: Example

      A minimal example of ``opera unpackage`` is shown on the image below
      (:numref:`opera_unpackage_minimal_svg`). The CSAR is unpacked without any
      of the available optional params. The CSAR format is automatically
      detected and the radon dirname with UUID is created for the destionation
      folder where the extracted files reside.

      .. _opera_unpackage_minimal_svg:

      .. figure:: /images/opera_unpackage_minimal.svg
         :target: _images/opera_unpackage_minimal.svg
         :width: 100%
         :align: center

         Testing opera unpackage on the `prepared small CSAR example <https://github.com/xlab-si/xopera-opera/tree/master/docs/files/csars/smal/small.csar>`_.

      A more complex example (:numref:`opera_unpackage_full_svg`) is below and
      shows usage of unpackaging command with additional CLI flags and in
      combination with ``opera package`` command. Therefore, the zip CSAR file
      is created first and is later unpacked to a specified location
      (the ``--destionation/-d`` switch is used here). Then the original folder
      that the CSAR was created from with ``upera pcakge`` is compared to the
      extracted folder which is a result of ``opera unpackage``. The folders
      are almost identical, whereas the latter contains `TOSCA-Metadata/TOSCA.meta`
      file which is specific for the TOSCA CSARs.

      .. _opera_unpackage_full_svg:

      .. figure:: /images/opera_unpackage_full.svg
         :target: _images/opera_unpackage_full.svg
         :width: 100%
         :align: center

         Running opera unpackage on the `hello world example <https://github.com/xlab-si/xopera-opera/tree/master/examples/hello>`_.


   .. tab:: Details

      The ``opera unpackage`` has the opposite function of the ``opera package``
      command. It  serves for unpacking (i.e. validating and extracting) the
      compressed TOSCA CSAR files. The opera unpackage command receives a
      compressed CSAR as a positional argument. It then validates and extracts
      the CSAR to a given location.

      There's no ``--format/-f`` option. Rather than that, the compressed file
      format (that will be used to extract the CSAR) is determined
      automatically. Currently, the compressed CSARs can be supplied in two
      different compression formats - `zip` or `tar`.


init (deprecated since 0.6.1)
#############################

      .. argparse::
         :filename: src/opera/cli.py
         :func: create_parser
         :prog: opera
         :path: init

.. tabs::

   .. tab:: Example

      The image below (:numref:`opera_init_service_template_svg`) shows an
      example of initializing the TOSCA service template and then deploying it.
      To save the orchestration data we created a custom folder (using the
      ``--instance-path/-p option``) instead of the default ``.opera``.

      .. _opera_init_service_template_svg:

      .. figure:: /images/opera_init_service_template.svg
         :target: _images/opera_init_service_template.svg
         :width: 100%
         :align: center

         Initialization and deployment of `artifacts example <https://github.com/xlab-si/xopera-opera/tree/master/examples/artifacts>`_.

      Another example in the figure below (:numref:`opera_init_csar_svg`)
      shows the initialization and deployment of the compressed TOSCA CSAR
      along with its `JSON inputs <https://github.com/xlab-si/xopera-opera/tree/master/docs/files/csars/small/inputs.json>`_.

      .. _opera_init_csar_svg:

      .. figure:: /images/opera_init_csar.svg
         :target: _images/opera_init_csar.svg
         :width: 100%
         :align: center

         Initialization and deployment of `small CSAR example <https://github.com/xlab-si/xopera-opera/tree/master/docs/files/csars/small/small.csar>`_.


   .. tab:: Details

      The deprecated ``opera init`` command is used to initialize the
      deployment. It either takes a TOSCA template file or a compressed (zipped
      CSAR) file (and an optional YAML file with inputs).

      When the compressed CSAR is provided to the ``opera init`` command it is
      then validated to be sure that the CSAR is compliant with TOSCA.

      After the initialization the following files and folders will be created
      in your opera storage directory (by default that is ``.opera`` and can be
      changed using the ``--instance-path`` flag):

      - ``root_file`` file - contains the path to the service template or CSAR
      - ``inputs`` file - JSON file with the supplied inputs
      - ``csars`` folder contains the extracted copy of your CSAR (created only if you deployed the compressed TOSCA CSAR)

      After running ``opera init`` you will be able to initiate the deployment
      process using just the ``opera deploy`` command without any positional
      arguments (however, you can still supply inputs or override TOSCA service
      template/CSAR).

      .. deprecated:: 0.6.1



.. note::

   The ``opera init`` command is deprecated and will probably be removed
   within one of the next releases. Please use ``opera deploy`` to initialize
   and deploy service templates or compressed CSARs.

.. hint::

   Every CLI command is equipped with ``--help/-h`` switch that displays the
   information about it and its arguments, and with ``--verbose/-v`` switch
   which turns on debug mode and prints out the orchestration parameters and
   the results from the executed Ansible playbooks.
