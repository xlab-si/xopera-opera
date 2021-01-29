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
to run the following commands:

.. code-block:: console

   $ sudo apt update
   $ sudo apt install -y python3-venv python3-wheel python-wheel-common

**Install**

xOpera is distributed as Python package that is regularly published on `PyPI`_.
So the simplest way to test ``opera`` is to install it into virtual environment:

.. code-block:: console

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

.. _CLI Reference:

==========================
CLI reference and examples
==========================

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

The commands can be executed in a random order and the orchestrator will warn and the orchestrator will warn you
in case if any problems.
Each CLI command is described more in detail in the following sections.

------------------------------------------------------------------------------------------------------------------------

deploy
######

**Name**

``opera deploy`` - used to deploy and control deployment of the application described in YAML or CSAR.

**Usage**

      .. argparse::
         :filename: src/opera/cli.py
         :func: create_parser
         :prog: opera
         :path: deploy

         The ``--resume/-r`` and ``--clean-state/-c`` options are mutually exclusive.

.. tabs::

   .. tab:: Details

      The ``opera deploy`` command is used to initiate the deployment
      orchestration process using the supplied TOSCA service template or the
      compressed TOSCA CSAR. Within this CLI command the xOpera orchestrator
      invokes multiple `TOSCA interface operations`_ (TOSCA `Standard interface`
      node operations and also TOSCA `Configure interface` relationship operations).
      The operations are executed in the following order:

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

   .. tab:: Example

      Follow the next CLI instructions and results for the `hello-world`_ example.

      .. code-block:: console
         :emphasize-lines: 2

         (venv) $ cd misc/hello-world
         (venv) misc/hello-world$ opera deploy service.yaml
         [Worker_0]   Deploying my-workstation_0
         [Worker_0]   Deployment of my-workstation_0 complete
         [Worker_0]   Deploying hello_0
         [Worker_0]     Executing create on hello_0
         [Worker_0]   Deployment of hello_0 complete

   .. tab:: Screencast

      A simple deployment of TOSCA service template is shown on the next image (:numref:`opera_deploy_service_template_svg`).

      .. _opera_deploy_service_template_svg:

      .. figure:: /images/opera_deploy_service_template.svg
         :target: _images/opera_deploy_service_template.svg
         :width: 100%
         :align: center

         Example of `hello-world`_ template opera deployment.

      Another example (:numref:`opera_deploy_csar_svg`) is below and shows a more
      complex usage of ``opera deploy`` command, deploying the compressed TOSCA
      CSAR with inputs and additional CLI flags. The CSAR is first deployed with
      the supplied YAML inputs (using ``--inputs/-i`` flag) and with two workers
      (``--workers/-w`` switch) that can run two Ansible playbook operations simultaneously.
      Then the CSAR is deployed again (using the ``--clean-state/-c`` option) from
      the beginning, but the execution gets interrupted. Therefore the third deployment
      is used to resume the deployment process from where it was interrupted (using the
      ``--resume/-r`` flag, we also used ``--force/-f`` flag here to skip all
      yes/no prompts).

      .. _opera_deploy_csar_svg:

      .. figure:: /images/opera_deploy_csar.svg
         :target: _images/opera_deploy_csar.svg
         :width: 100%
         :align: center

         The `misc-tosca-types-csar`_ example deployment.

------------------------------------------------------------------------------------------------------------------------

undeploy
#########

**Name**

``opera undeploy`` - undeploys application; removes all application instances and components.

**Usage**

      .. argparse::
         :filename: src/opera/cli.py
         :func: create_parser
         :prog: opera
         :path: undeploy

         The ``opera undeploy`` command does not take any positional arguments.

.. tabs::

   .. tab:: Details

      The ``opera undeploy`` command is used to tear down the deployed blueprint.
      Within the undeployment process the xOpera orchestrator invokes two TOSCA
      Standard interface node operations in the following order:

      1. ``stop``
      2. ``delete``

      The operation gets executed if it is defined within the TOSCA service template
      and has a link to the corresponding Ansible playbook.

   .. tab:: Example

      Follow the next CLI instructions and results for the `hello-world`_ example.

      .. code-block:: console
         :emphasize-lines: 8

         (venv) $ cd misc/hello-world
         (venv) misc/hello-world$ opera deploy service.yaml
         [Worker_0]   Deploying my-workstation_0
         [Worker_0]   Deployment of my-workstation_0 complete
         [Worker_0]   Deploying hello_0
         [Worker_0]     Executing create on hello_0
         [Worker_0]   Deployment of hello_0 complete
         (venv) misc/hello-world$ opera undeploy
         [Worker_0]   Undeploying hello_0
         [Worker_0]     Executing delete on hello_0
         [Worker_0]   Undeployment of hello_0 complete
         [Worker_0]   Undeploying my-workstation_0
         [Worker_0]   Undeployment of my-workstation_0 complete

   .. tab:: Screencast

      A simple undeployment process of TOSCA service template is shown on the
      next image (:numref:`opera_undeploy_svg`). The service template should
      be deployed first and the you can undeploy the solution.

      .. _opera_undeploy_svg:

      .. figure:: /images/opera_cli.svg
         :target: _images/opera_cli.svg
         :width: 100%
         :align: center

         Example showing `hello-world`_ template opera undeployment.

      Another example (:numref:`opera_undeploy_csar_svg`) is below and shows a more
      complex usage of ``opera undeploy`` command, undeploying the compressed TOSCA
      CSAR with additional CLI flags. The CSAR was first deployed with the supplied
      YAML inputs file. Then the CSAR is undeployed, but the execution gets interrupted.
      To resume the undeployment process from where it was interrupted the ``--resume/-r``
      flag is used.

      .. _opera_undeploy_csar_svg:

      .. figure:: /images/opera_undeploy_csar.svg
         :target: _images/opera_undeploy_csar.svg
         :width: 100%
         :align: center

         The undeployment of the `misc-tosca-types-csar`_.

------------------------------------------------------------------------------------------------------------------------

validate
########

**Name**

``opera validate`` - validates the structure of TOSCA template or CSAR.

**Usage**
      .. argparse::
         :filename: src/opera/cli.py
         :func: create_parser
         :prog: opera
         :path: validate

.. tabs::

   .. tab:: Details

      With ``opera validate`` you can validate any TOSCA template or CSAR (including its inputs)
      and find out whether it's properly structured and deployable by opera. At the
      end of this operation you will receive the validation result where opera
      will warn you about TOSCA template inconsistencies if there was any. Since validation
      can be successful or unsuccessful the `opera validate` commands has corresponding
      return codes - 0 for success and 1 for failure. If the validation succeeds this means
      that your TOSCA templates are valid and that all their implementations (e.g. Ansible playbooks)
      can be invoked. However, this doesn't mean that these operations will succeed.

   .. tab:: Example

      Follow the next CLI instructions and results for the `misc-tosca-types-csar`_ example.

      .. code-block:: console
         :emphasize-lines: 2

         (venv) $ cd misc/hello-world
         (venv) csars/misc-tosca-types$ opera validate -i inputs.yaml service.yaml
         Validating service template...
         Done.

   .. tab:: Screencast

      The first image below (:numref:`opera_validate_service_template_svg`) shows an example of
      TOSCA service template validation.

      .. _opera_validate_service_template_svg:

      .. figure:: /images/opera_validate_service_template.svg
         :target: _images/opera_validate_service_template.svg
         :width: 100%
         :align: center

         Example showing `attribute-mapping`_ template validation.

      The second image (:numref:`opera_validate_csar_svg`) shows an example of
      TOSCA zipped CSAR validation where orchestration YAML inputs file is also supplied.

      .. _opera_validate_csar_svg:

      .. figure:: /images/opera_validate_csar.svg
         :target: _images/opera_validate_csar.svg
         :width: 100%
         :align: center

         Example showing `misc-tosca-types-csar`_ CSAR validation.

------------------------------------------------------------------------------------------------------------------------

outputs
#######

**Name**

``opera outputs`` - print the outputs of the deploy/undeploy.

**Usage**

      .. argparse::
         :filename: src/opera/cli.py
         :func: create_parser
         :prog: opera
         :path: outputs

.. tabs::

   .. tab:: Details

      The ``opera outputs`` command lets you access the orchestration outputs
      defined in the TOSCA service template and print them out to the console
      in JSON or YAML format (used by default).

   .. tab:: Example

      Follow the next CLI instructions and results for the `outputs`_ example.

      .. code-block:: console
         :emphasize-lines: 7

         (venv) $ cd tosca/outputs
         (venv) tosca/outputs$ opera deploy service.yaml
         [Worker_0]   Deploying my_node_0
         [Worker_0]     Executing create on my_node_0
         [Worker_0]   Deployment of my_node_0 complete

         (venv) tosca/outputs$ opera outputs
         output_attr:
           description: Example of attribute output
           value: my_custom_attribute_value
         output_prop:
           description: Example of property output
           value: 123

   .. tab:: Screencast

      The image below (:numref:`opera_outputs_service_template_svg`) shows an
      example of retrieving the orchestration outputs after the deployment process.

      .. _opera_outputs_service_template_svg:

      .. figure:: /images/opera_outputs_service_template.svg
         :target: _images/opera_outputs_service_template.svg
         :width: 100%
         :align: center

         Example showing `outputs`_ retrieval.

      Another example in the figure below (:numref:`opera_outputs_csar_svg`)
      shows deploying the TOSCA CSAR with the supplied JSON inputs file.
      After that the outputs are retrieved and formatted in JSON (using ``--format/-f`` option).

      .. _opera_outputs_csar_svg:

      .. figure:: /images/opera_outputs_csar.svg
         :target: _images/opera_outputs_csar.svg
         :width: 100%
         :align: center

         Example showing `small-csar`_ deployment and outputs retrieval.

------------------------------------------------------------------------------------------------------------------------

info
#######

**Name**

``opera info`` - print the details of current deployment project.

**Usage**

      .. argparse::
         :filename: src/opera/cli.py
         :func: create_parser
         :prog: opera
         :path: info

.. tabs::

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

   .. tab:: Example

      Follow the next CLI instructions and results for the `misc-tosca-types-csar`_ example.

      .. code-block:: console
         :emphasize-lines: 2, 12, 34, 56, 84

         (venv) $ cd csars/misc-tosca-types
         (venv) csars/misc-tosca-types$ opera info
         content_root: null
         inputs: null
         service_template: null
         status: null

         (venv) csars/misc-tosca-types$ opera init -i inputs.yaml service.yaml
         Warning: 'opera init' command is deprecated and will probably be removed within one of the next releases. Please use 'opera deploy' to initialize and deploy service templates or compressed CSARs.
         Service template was initialized

         (venv) csars/misc-tosca-types$ opera info
         content_root: null
         inputs: /home/user/Desktop/xopera-examples/csars/misc-tosca-types/.opera/inputs
         service_template: service.yaml
         status: initialized

         (venv) csars/misc-tosca-types$ opera deploy
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
         [Worker_0]     Executing create on interfaces_0
         ^C[Worker_0] ------------
         KeyboardInterrupt

         (venv) csars/misc-tosca-types$ opera info

         content_root: null
         inputs: /home/user/Desktop/xopera-examples/csars/misc-tosca-types/.opera/inputs
         service_template: service.yaml
         status: interrupted

         (venv) csars/misc-tosca-types$ opera deploy -r -f
         [Worker_0]   Deploying interfaces_0
         [Worker_0]     Executing create on interfaces_0
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

         (venv) csars/misc-tosca-types$ opera info

         content_root: null
         inputs: /home/user/Desktop/xopera-examples/csars/misc-tosca-types/.opera/inputs
         service_template: service.yaml
         status: deployed

         (venv) csars/misc-tosca-types$ opera undeploy
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

         (venv) csars/misc-tosca-types$ opera info

         content_root: null
         inputs: /home/user/Desktop/xopera-examples/csars/misc-tosca-types/.opera/inputs
         service_template: service.yaml
         status: undeployed

   .. tab:: Screencast

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

         Testing opera info on the `capability-attributes-properties`_.

      A more complex example (:numref:`opera_info_full_svg`) is below and shows a
      combined usage of init, deploy and undeploy commands on the zipped TOSCA
      CSAR with additional CLI flags. After every operation ``opera info`` CLI
      command is called to explore the current status of the project.

      The CSAR was first initialized without the JSON inputs file.
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

         The opera info testing on the `small-csar`_.

------------------------------------------------------------------------------------------------------------------------

package
#######

**Name**

``opera package`` - package TOSCA YAML templates and their accompanying files to a compressed TOSCA CSAR.

**Usage**

      .. argparse::
         :filename: src/opera/cli.py
         :func: create_parser
         :prog: opera
         :path: package

.. tabs::

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

   .. tab:: Example

      Follow the next CLI instructions and results for the `hello-world`_ and `misc-tosca-types-csar`_ examples.

      .. code-block:: console
         :emphasize-lines: 2, 6

         (venv) $ cd misc/hello-world
         (venv) misc/hello-world$ opera package .
         CSAR was created and packed to '/home/user/Desktop/xopera-examples/misc/hello-world/opera-package-45045f.zip'.

         (venv) misc/hello-world$ cd ../../csars
         (venv) csars$ opera package -t service.yaml -o misc-tosca-types  misc-tosca-types/
         CSAR was created and packed to '/home/user/Desktop/xopera-examples/csars/misc-tosca-types.zip'.

   .. tab:: Screencast

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

         Testing opera package on `intrinsic-functions`_ and `policy-triggers`_ example.

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

         Running opera package on the `opera integration tests CSAR examples`_.

------------------------------------------------------------------------------------------------------------------------

unpackage
##########

**Name**

``opera unpackage`` - uncompress TOSCA CSAR.

**Usage**
      .. argparse::
         :filename: src/opera/cli.py
         :func: create_parser
         :prog: opera
         :path: unpackage

.. tabs::

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

   .. tab:: Example

      Follow the next CLI instructions and results for the `misc-tosca-types-csar`_ and `small-csar`_ examples.

      .. code-block:: console
         :emphasize-lines: 5, 11

         (venv) $ cd csars
         (venv) csars$ opera package -t service.yaml -o misc-tosca-types misc-tosca-types/
         CSAR was created and packed to '/home/user/Desktop/xopera-examples/csars/misc-tosca-types.zip'.

         (venv) csars$ opera unpackage misc-tosca-types.zip
         The CSAR was unpackaged to '/home/user/Desktop/xopera-examples/csars/opera-unpackage-1cabf6'.

         (venv) csars$ opera package -t service.yaml -o small small/
         CSAR was created and packed to '/home/user/Desktop/xopera-examples/csars/small.zip'.

         (venv) csars$ opera unpackage -d small-extracted small.zip
         The CSAR was unpackaged to '/home/user/Desktop/xopera-examples/csars/small-extracted'.

   .. tab:: Screencast

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

         Testing opera unpackage on the `small-csar`_.

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

         Running opera unpackage on the `hello-world`_ example.

------------------------------------------------------------------------------------------------------------------------

diff
####

**Name**

``opera diff`` - compare TOSCA service templates and instances.

**Usage**
      .. argparse::
         :filename: src/opera/cli.py
         :func: create_parser
         :prog: opera
         :path: diff

.. tabs::

   .. tab:: Details

      The ``opera diff`` CLI command holds the functionality to find the differences between the deployed TOSCA service
      template and the updated TOSCA service template that you wish to redeploy. Moreover, this operation compares the
      desired TOSCA service template to the one from the opera project storage (by default this one is located in
      ``.opera``) and print out their differences.

      The command includes two sub-operations that invoke template and instance comparers. The template comparer allows
      the comparison of changed blueprint (and changed inputs) in a folder containing the existing TOSCA service
      template that was deployed before. The instance comparer looks for changes in instance states and also traverses
      the dependency graph in order to propagate changes from parent to child nodes. If a parent node is marked as
      changed, then child node is also considered changed.

      The output of ``opera diff`` is a human readable representation of templates differences, is formatted either as
      JSON or YAML (default) and can be optionally saved in a file.

   .. tab:: Example

      Follow the next CLI instructions and results for the `compare-templates`_ example.

      .. code-block:: console
         :emphasize-lines: 21

         (venv) $ cd tosca/compare-templates
         (venv) misc/compare-templates$ opera deploy -i inputs1.yaml service1.yaml
         [Worker_0]   Deploying my-workstation_0
         [Worker_0]   Deployment of my-workstation_0 complete
         [Worker_0]   Deploying hello-1_0
         [Worker_0]     Executing create on hello-1_0
         [Worker_0]   Deployment of hello-1_0 complete
         [Worker_0]   Deploying hello-2_0
         [Worker_0]     Executing create on hello-2_0
         [Worker_0]   Deployment of hello-2_0 complete
         [Worker_0]   Deploying hello-3_0
         [Worker_0]     Executing create on hello-3_0
         [Worker_0]   Deployment of hello-3_0 complete
         [Worker_0]   Deploying hello-4_0
         [Worker_0]     Executing create on hello-4_0
         [Worker_0]   Deployment of hello-4_0 complete
         [Worker_0]   Deploying hello-6_0
         [Worker_0]     Executing create on hello-6_0
         [Worker_0]   Deployment of hello-6_0 complete

         (venv) misc/compare-templates$ opera diff -i inputs2.yaml service2.yaml
         nodes:
           added:
           - hello-5
           changed:
             hello-1:
               capabilities:
                 deleted:
                 - test
               interfaces:
                 Standard:
                   operations:
                     create:
                       artifacts:
                         added:
                         - lib/files/file1_2.yaml
                         deleted:
                         - lib/files/file1_1.yaml
                       inputs:
                         marker:
                         - marker1
                         - marker2
                         time:
                         - '0'
                         - '1'
                     delete:
                       artifacts:
                         added:
                         - lib/files/file1_2.yaml
                         deleted:
                         - lib/files/file1_1.yaml
                       inputs:
                         marker:
                         - marker1
                         - marker2
                         time:
                         - '0'
                         - '1'
               properties:
                 time:
                 - '0'
                 - '1'
             hello-2:
               capabilities:
                 test:
                   properties:
                     test1:
                     - '2'
                     - '3'
                     test2:
                     - '2'
                     - '3'
               dependencies:
               - hello-2
               interfaces:
                 Standard:
                   operations:
                     create:
                       artifacts:
                         added:
                         - lib/files/file2.yaml
                         deleted:
                         - lib/files/file1_1.yaml
                       inputs:
                         marker:
                         - marker1
                         - marker2
                     delete:
                       artifacts:
                         added:
                         - lib/files/file2.yaml
                         deleted:
                         - lib/files/file1_1.yaml
                       inputs:
                         marker:
                         - marker1
                         - marker2
               properties:
                 day:
                 - '1'
                 - '2'
               requirements:
                 added:
                 - dependency
               types:
               - hello_type_old
               - hello_type_new
             hello-3:
               interfaces:
                 Standard:
                   operations:
                     create:
                       inputs:
                         marker:
                         - marker1
                         - marker2
                     delete:
                       inputs:
                         marker:
                         - marker1
                         - marker2
             hello-6:
               dependencies:
               - hello-6
               interfaces:
                 Standard:
                   operations:
                     create:
                       inputs:
                         marker:
                         - marker1
                         - marker2
                     delete:
                       inputs:
                         marker:
                         - marker1
                         - marker2
               requirements:
                 dependency:
                   target:
                   - hello-1
                   - hello-2
           deleted:
           - hello-4

------------------------------------------------------------------------------------------------------------------------

update
######

**Name**

``opera update`` - update the deployed TOSCA service template and redeploy it according to the discovered template diff.

**Usage**
      .. argparse::
         :filename: src/opera/cli.py
         :func: create_parser
         :prog: opera
         :path: update

.. tabs::

   .. tab:: Details

      The ``opera update`` command extends the usage of ``opera diff`` and is able to redeploy the update TOSCA service
      template according to the changes that were made to the previously deployed template. This means that
      ``opera update`` will first compare the two templates and instances with and then redeploy.

      The user is able to run update command providing a changed blueprint and inputs in a folder containing existing
      service template that was deployed before. The result of the execution would be undeployment of the nodes that
      were removed from the service template, deployment of the nodes that were added to the service template and
      consequential undeployment/deployment of changed nodes.

   .. tab:: Example

      Follow the next CLI instructions and results for the `compare-templates`_ example.

      .. code-block:: console
         :emphasize-lines: 21

         (venv) $ cd tosca/compare-templates
         (venv) misc/compare-templates$ opera deploy -i inputs1.yaml service1.yaml
         [Worker_0]   Deploying my-workstation_0
         [Worker_0]   Deployment of my-workstation_0 complete
         [Worker_0]   Deploying hello-1_0
         [Worker_0]     Executing create on hello-1_0
         [Worker_0]   Deployment of hello-1_0 complete
         [Worker_0]   Deploying hello-2_0
         [Worker_0]     Executing create on hello-2_0
         [Worker_0]   Deployment of hello-2_0 complete
         [Worker_0]   Deploying hello-3_0
         [Worker_0]     Executing create on hello-3_0
         [Worker_0]   Deployment of hello-3_0 complete
         [Worker_0]   Deploying hello-4_0
         [Worker_0]     Executing create on hello-4_0
         [Worker_0]   Deployment of hello-4_0 complete
         [Worker_0]   Deploying hello-6_0
         [Worker_0]     Executing create on hello-6_0
         [Worker_0]   Deployment of hello-6_0 complete

         (venv) misc/compare-templates$ opera update -i inputs2.yaml service2.yaml
         [Worker_0]   Undeploying hello-2_0
         [Worker_0]     Executing delete on hello-2_0
         [Worker_0]   Undeployment of hello-2_0 complete
         [Worker_0]   Undeploying hello-3_0
         [Worker_0]     Executing delete on hello-3_0
         [Worker_0]   Undeployment of hello-3_0 complete
         [Worker_0]   Undeploying hello-4_0
         [Worker_0]     Executing delete on hello-4_0
         [Worker_0]   Undeployment of hello-4_0 complete
         [Worker_0]   Undeploying hello-6_0
         [Worker_0]     Executing delete on hello-6_0
         [Worker_0]   Undeployment of hello-6_0 complete
         [Worker_0]   Undeploying hello-1_0
         [Worker_0]     Executing delete on hello-1_0
         [Worker_0]   Undeployment of hello-1_0 complete
         [Worker_0]   Deploying hello-1_0
         [Worker_0]     Executing create on hello-1_0
         [Worker_0]   Deployment of hello-1_0 complete
         [Worker_0]   Deploying hello-2_0
         [Worker_0]     Executing create on hello-2_0
         [Worker_0]   Deployment of hello-2_0 complete
         [Worker_0]   Deploying hello-3_0
         [Worker_0]     Executing create on hello-3_0
         [Worker_0]   Deployment of hello-3_0 complete
         [Worker_0]   Deploying hello-5_0
         [Worker_0]     Executing create on hello-5_0
         [Worker_0]   Deployment of hello-5_0 complete
         [Worker_0]   Deploying hello-6_0
         [Worker_0]     Executing create on hello-6_0
         [Worker_0]   Deployment of hello-6_0 complete

------------------------------------------------------------------------------------------------------------------------

init (deprecated since 0.6.1)
#############################

**Name**

``opera init`` - initialize TOSCA CSAR or service template.

**Usage**

      .. argparse::
         :filename: src/opera/cli.py
         :func: create_parser
         :prog: opera
         :path: init

.. tabs::

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

   .. tab:: Example

      Follow the next CLI instructions and results for the `misc-tosca-types-csar`_ example.

      .. code-block:: console
         :emphasize-lines: 2

         (venv) $ cd csars/misc-tosca-types
         (venv) csars/misc-tosca-types$ opera init -i inputs.yaml service.yaml
         Warning: 'opera init' command is deprecated and will probably be removed within one of the next releases. Please use 'opera deploy' to initialize and deploy service templates or compressed CSARs.
         Service template was initialized

   .. tab:: Screencast

      The image below (:numref:`opera_init_service_template_svg`) shows an
      example of initializing the TOSCA service template and then deploying it.
      To save the orchestration data we created a custom folder (using the
      ``--instance-path/-p option``) instead of the default ``.opera``.

      .. _opera_init_service_template_svg:

      .. figure:: /images/opera_init_service_template.svg
         :target: _images/opera_init_service_template.svg
         :width: 100%
         :align: center

         Initialization and deployment of `artifacts`_.

      Another example in the figure below (:numref:`opera_init_csar_svg`)
      shows the initialization and deployment of the compressed TOSCA CSAR
      along with its JSON inputs.

      .. _opera_init_csar_svg:

      .. figure:: /images/opera_init_csar.svg
         :target: _images/opera_init_csar.svg
         :width: 100%
         :align: center

         Initialization and deployment of `small-csar`_.

.. note::

   The ``opera init`` command is deprecated and will probably be removed
   within one of the next releases. Please use ``opera deploy`` to initialize
   and deploy service templates or compressed CSARs.

------------------------------------------------------------------------------------------------------------------------

==========================
Troubleshooting
==========================

Every CLI command is equipped with ``--help/-h`` switch that displays the information about it and its arguments, and
with ``--verbose/-v`` switch which turns on debug mode and prints out the orchestration parameters and the results from
the executed Ansible playbooks. Consider using the two switches if you face any problems. If the issue persists please
have a look at the existing `opera issues`_ or open a new one yourself.

.. _PyPI: https://pypi.org/project/opera/
.. _opera issues: https://github.com/xlab-si/xopera-opera/issues
.. _TOSCA interface operations: https://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.3/cos01/TOSCA-Simple-Profile-YAML-v1.3-cos01.html#_Toc26969470
.. _misc-tosca-types-csar: https://github.com/xlab-si/xopera-examples/tree/master/csars/misc-tosca-types
.. _small-csar: https://github.com/xlab-si/xopera-examples/tree/master/csars/small
.. _hello-world: https://github.com/xlab-si/xopera-examples/tree/csar-examples/misc/hello-world
.. _outputs: https://github.com/xlab-si/xopera-examples/tree/master/tosca/outputs
.. _attribute-mapping: https://github.com/xlab-si/xopera-examples/tree/master/tosca/attribute-mapping
.. _capability-attributes-properties: https://github.com/xlab-si/xopera-examples/tree/master/tosca/capability-attributes-properties
.. _intrinsic-functions: https://github.com/xlab-si/xopera-examples/tree/master/tosca/intrinsic-functions
.. _policy-triggers: https://github.com/xlab-si/xopera-examples/tree/master/tosca/policy-triggers
.. _opera integration tests CSAR examples: https://github.com/xlab-si/xopera-opera/tree/master/tests/integration
.. _artifacts: https://github.com/xlab-si/xopera-examples/tree/master/tosca/artifacts
.. _compare-templates: https://github.com/xlab-si/xopera-examples/tree/csar-examples/misc/compare-templates
