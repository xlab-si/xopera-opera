# xOpera TOSCA orchestrator
xOpera orchestration tool compliant with TOSCA YAML v1.3 in the making.

![CircleCI](https://img.shields.io/circleci/build/github/xlab-si/xopera-opera?label=circleci)
![GitHub deployments](https://img.shields.io/github/deployments/xlab-si/xopera-opera/github-pages?label=documentation)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/xlab-si/xopera-opera)
![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/xlab-si/xopera-opera)
![GitHub pull requests](https://img.shields.io/github/issues-pr/xlab-si/xopera-opera)
![GitHub issues](https://img.shields.io/github/issues/xlab-si/xopera-opera)
![GitHub contributors](https://img.shields.io/github/contributors/xlab-si/xopera-opera)
![GitHub top language](https://img.shields.io/github/languages/top/xlab-si/xopera-opera)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/xlab-si/xopera-opera)
![PyPI](https://img.shields.io/pypi/v/opera)
![PyPI - Status](https://img.shields.io/pypi/status/opera)
![PyPI - Implementation](https://img.shields.io/pypi/implementation/opera)
![PyPI - Format](https://img.shields.io/pypi/format/opera)
![PyPI - License](https://img.shields.io/pypi/l/opera)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/opera)
![PyPI - Wheel](https://img.shields.io/pypi/wheel/opera)
![PyPI - Downloads](https://img.shields.io/pypi/dm/opera)

| Aspect                         | Information                            |
| ------------------------------ |:--------------------------------------:|
| Tool name                      | opera                                  |
| Read the docs (Sphinx)         | https://xlab-si.github.io/xopera-docs/ |
| Orchestration standard         | OASIS TOSCA v1.3                       |
| Automation tools and actuators | Ansible                                |

## Table of Contents
  - [Introduction](#introduction)
  - [Prerequisites](#prerequisites)
  - [Installation and Quickstart](#installation-and-quickstart)
  - [Common examples](#common-examples)
    - [OpenStack client setup](#openstack-client-setup)
  - [Connected resources](#other-resources-and-services)
  - [Acknowledgement](#acknowledgement)

## Introduction
`opera` aims to be a lightweight orchestrator compliant with 
[OASIS TOSCA](https://www.oasis-open.org/committees/tc_home.php?wg_abbrev=tosca).
The current compliance is with the 
[TOSCA Simple Profile in YAML v1.3](https://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.3/TOSCA-Simple-Profile-YAML-v1.3.html).
The documentation for the tool is available on [GitHub pages](https://xlab-si.github.io/xopera-docs/).
Opera implements TOSCA standard with [Ansible automation tool](https://www.ansible.com/) 
where Ansible playbooks can be used as orchestration actuators.

## Prerequisites
`opera` requires python 3 and a virtual environment. In a typical modern
Linux environment, we should already be set. In Ubuntu, however, we
might need to run the following commands:

    $ sudo apt update
    $ sudo apt install -y python3-venv python3-wheel python-wheel-common

## Installation and Quickstart
<p align="center">
  <img src="https://raw.githubusercontent.com/xlab-si/xopera-opera/refactor-readme/docs/images/opera_cli.svg?sanitize=true" alt="opera in action">
</p>

The orchestration tool is available on PyPI as a package named [`opera`](https://pypi.org/project/opera/).
Apart from the latest [production](https://pypi.org/project/opera/#history) 
version, you can also find the latest opera [develop](https://test.pypi.org/project/opera/#history) 
version (available on Test PyPI instance), which includes pre-releases so that 
you will be able to test the latest features before they are officially released.

The simplest way to test `opera` is to install it into virtual
environment:

    $ mkdir ~/opera && cd ~/opera
    $ python3 -m venv .venv && . .venv/bin/activate
    (.venv) $ pip install opera

To test if everything is working as expected, we can now clone xOpera's
GitHub repository and try to deploy a hello-world service:

    (.venv) $ git clone git@github.com:xlab-si/xopera-opera.git
    (.venv) $ cd xopera-opera/examples/hello
    (.venv) $ opera deploy service.yaml

If nothing went wrong, new empty file has been created at
`/tmp/playing-opera/hello/hello.txt`.

To delete the created directory, we can undeploy our stuff by running:

    (.venv) $ opera undeploy

And that is it.

## Common examples
This part focuses on different common ways of usage for opera orchestration tool. 

### OpenStack client setup
Because using OpenStack modules from Ansible playbooks is quite common,
we can install `opera` with all required OpenStack libraries by running:

    (.venv) $ pip install -U opera[openstack]

Before we can actually use the OpenStack functionality, we also need to
obtain the OpenStack credentials. If we log into OpenStack and navigate
to the `Access & Security` -\> `API Access` page, we can download the rc
file with all required information.

At the start of each session (e.g., when we open a new command line
console), we must source the rc file by running:

    (venv) $ . openstack.rc

After we enter the password, we are ready to start using the OpenStack
modules in playbooks that implement life cycle operations.

## Other resources and services
The table below show other important resources that are connected to `opera`.

| Resource                 | Link                                                    |
| ------------------------ |:-------------------------------------------------------:|
| xopera-api               | https://github.com/xlab-si/xopera-api/                  |
| radon-xopera-saas-plugin | https://github.com/radon-h2020/radon-xopera-saas-plugin |

## Acknowledgement
This project has received funding from the European Union’s Horizon 2020
research and innovation programme under Grant Agreements No. 825040 
([RADON](http://radon-h2020.eu/)) and No. 825480 ([SODALITE](http://www.sodalite.eu/)).
