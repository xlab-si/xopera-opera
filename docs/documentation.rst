.. _Documentation:

*************
Documentation
*************

This part further explains the structure and usage of xOpera orchestrator.

.. Background:

Background
##########

xOpera is a TOSCA standard compliant orchestrator that is following the paradigm of having a minimal set of
features and is currently focusing on Ansible. xOpera is following the traditional UNIX philosophy of having a tool that
does one thing, and does it right. So, with a minimal set of features xOpera will do just the orchestration, and do it well.
xOpera is available on GitHub under Apache License 2.0.

TOSCA stands for the OASIS Topology and Orchestration Specification for Cloud Applications (TOSCA) standard.
It's an industry-developed and supported standard, still lively and fast to adopt new technologies, approaches and
paradigms. It's however mostly backwards compatible, so staying within the realm of TOSCA is currently a sound and,
from the longevity perspective, a wise decision.

Using the TOSCA as the system-defining language for the xOpera means that we have an overarching declarative way that
manages the actual deployment. The Ansible playbooks are now in the role of the actuators, tools that concretise the
declared system, its topology and contextualisation of the components and networking.

This design takes the best of both worlds. TOSCA service template is a system definition, written in proverbial stone,
while the qualities of the individual Ansible playbooks are now shining. Within the playbooks, we can now entirely focus
on particular elements of the overall system, such as provisioning virtual machines at the cloud provider, installing
and configuring a service on a target node, etc. xOpera, in its capacity, takes care of all the untidy inter-playbook
coordination, state of the deployment and so on.

.. note::

    More about xOpera's background, its origins and goals can be found here: `xOpera: an agile orchestrator <https://www.sodalite.eu/content/xopera-agile-orchestrator>`_

.. Parser:

Parser
######

xOpera orchestrator has its own YAML and TOSCA parser which is shown on the image below :ref:`opera_parser_structure`.

.. _opera_parser_structure:

.. figure:: /images/opera_parser_structure.png
    :target: _images/opera_parser_structure.png
    :width: 50%
    :align: center

    xOpera parser and executor

.. Usage:

Usage
#####

``opera`` is meant to be used in a terminal as a client and it currently allows users to execute the following commands:

+---------------+------------------+----------------------------------------------+
| Command       | Command options  | Purpose and description                      |
+===============+==================+==============================================+
| deploy        | -i, --inputs     | deploy TOSCA service template                |
+---------------+------------------+----------------------------------------------+
| undeploy      | /                | un-deploy the deployed solution              |
+---------------+------------------+----------------------------------------------+
| validate      | -i, --inputs     | verify if TOSCA service template is correct  |
+---------------+------------------+----------------------------------------------+
| outputs       | -f, --format     | retrieve deployment outputs                  |
+---------------+------------------+----------------------------------------------+


.. tip::

    If you have any problems have a look at existing issues here: https://github.com/xlab-si/xopera-opera/issues or open
    a new one yourself.
