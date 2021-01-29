.. _opera api:

***********
xOpera API
***********

=================
Installation
=================

This section explains the installation of xOpera orchestrator API (available on GitHub in `xopera-api`_ repository).

**Prerequisites**

``opera`` requires python 3 and a virtual environment. In a typical modern
Linux environment, we should already be set. In Ubuntu, however, we might need
to run the following commands:

.. code-block:: console

   $ sudo apt update
   $ sudo apt install -y python3-venv python3-wheel python-wheel-common

**Install**

xOpera API is distributed as Python package that is regularly published on `PyPI`_.
So the simplest way to test ``opera-api`` is to install it into virtual environment:

.. code-block:: console

   mkdir ~/opera && cd ~/opera
   python3 -m venv .venv && . .venv/bin/activate
   (.venv) $ pip install opera-api

.. _xopera-api: https://github.com/xlab-si/xopera-api
.. _PyPI: https://pypi.org/project/opera-api/>
