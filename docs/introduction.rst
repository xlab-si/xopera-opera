.. _Introduction:

************
Introduction
************

``xOpera project`` includes a set of tools for advanced orchestration
with an orchestration tool ``xOpera orchestrator`` or shorter ``opera``.

``opera`` aims to be a lightweight orchestrator compliant with `OASIS TOSCA`_.and the current compliance is with the
`TOSCA Simple Profile in YAML v1.3`_. ``opera`` is by following TOSCA primarily a (TOSCA) cloud orchestrator which
enables orchestration of automated tasks within cloud applications for different cloud providers such as Amazon Web
Services (AWS), Microsoft Azure, Google Cloud Platform (GCP), OpenFaaS, OpenStack and so on. Apart from that this tool
can be used and integrated to other infrastructures in order to orchestrate services or applications and therefore
reduce human factor.

xOpera orchestrator engine - called xOpera library - xOpera CLI and xOpera API are an open-source project which
currently reside on GitHub inside `xopera-opera`_ and `xopera-api`_ repositories.
As an orchestration tool xOpera uses `Ansible`_ automation tool to implement the the TOSCA standard and to run its
interface operations via Ansible playbook actuators which again opens a lot of new possibilities.

.. _xopera_architecture:

.. figure:: /images/xopera-architecture.png
    :target: _images/xopera-architecture.png
    :width: 95%
    :align: center

    The xOpera components.

Currently a set of components is presented in figure :numref:`xopera_architecture`, where we can point out:


 - Opera CLI is a command line interface to the **xOpera library** for deploying TOSCA templates and CSARs
 - Opera API allows integration of **xOpera library**.
 - xOpera SaaS is a standalone service for application lifecycle management with xOpera orchestrator
   through GUI and API.
 - TPS or Template Publishing Service is a library of published TOSCA templates and CSARs

Each component is covered by corresponding This documentation will cover all xOpera components.

================
Background
================

xOpera is a TOSCA standard compliant orchestrator that is following the paradigm of having a minimal set of
features and is currently focusing on Ansible.
xOpera is following the traditional UNIX philosophy of having a tool that does one thing, and does it right.
So, with a minimal set of features xOpera will do just the orchestration, and do it well.

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

    More about xOpera's background, its origins and goals can be found here: `xOpera - an agile orchestrator`_

.. _Parser:

================
Parser
================

.. note::

   *TBD*: This part of the documentation will be improved in the future.

xOpera orchestrator has its own YAML and TOSCA parser which is shown on the image below
(:numref:`opera_parser_structure`.)

.. _opera_parser_structure:

.. figure:: /images/opera_parser_structure.png
   :target: _images/opera_parser_structure.png
   :width: 50%
   :align: center

   xOpera parser and executor

.. _OASIS TOSCA: https://www.oasis-open.org/committees/tc_home.php?wg_abbrev=tosca
.. _TOSCA Simple Profile in YAML v1.3: https://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.3/TOSCA-Simple-Profile-YAML-v1.3.html
.. _xopera-opera: https://github.com/xlab-si/xopera-opera
.. _xopera-api: https://github.com/xlab-si/xopera-api
.. _Ansible: https://www.ansible.com/
.. _xOpera - an agile orchestrator: https://www.sodalite.eu/content/xopera-agile-orchestrator
