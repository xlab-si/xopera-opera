.. _Installation:

************
Installation
************

This section explains the installation of xOpera orchestrator.

Prerequisites
#############

``opera`` requires python 3 and a virtual environment. In a typical modern
Linux environment, we should already be set. In Ubuntu, however, we might need
to run the following commands::

  $ sudo apt update
  $ sudo apt install -y python3-venv python3-wheel python-wheel-common

Install
#######

xOpera is distributed as Python package that is regularly published on `PyPI <https://pypi.org/project/opera/>`_.
So the simplest way to test ``opera`` is to install it into virtual environment::

  $ mkdir ~/opera && cd ~/opera
  $ python3 -m venv .venv && . .venv/bin/activate
  (.venv) $ pip install opera

