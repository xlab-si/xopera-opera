.. _Introduction:

************
Introduction
************

``xOpera`` or shorter ``opera`` is an orchestration tool or orchestrator.

``opera`` aims to be a lightweight orchestrator compliant with `OASIS TOSCA <https://www.oasis-open.org/committees/tc_home.php?wg_abbrev=tosca>`_.
and the current compliance is with the `TOSCA Simple Profile in YAML v1.3 <https://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.3/TOSCA-Simple-Profile-YAML-v1.3.html>`_.
``opera`` is by following TOSCA primarily a (TOSCA) cloud orchestrator which enables orchestration of automated tasks
within cloud applications for different cloud providers such as Amazon Web Services(AWS), Microsoft Azure, Google Cloud
Platform(GCP), OpenFaaS, OpenStack and so on. Apart from that this tool can be used and integrated to other infrastructures
in order to orchestrate services or applications and therefore reduce human factor.

xOpera tool is an open-source project which currently resides on GitHub inside `xopera-opera <https://github.com/xlab-si/xopera-opera>`_
repository. As an orchestration tool xOpera uses `Ansible automation tool <https://www.ansible.com/>`_ to implement the
TOSCA standard and to run its operations via Ansible playbook actuators which again opens a lot of new possibilities.
