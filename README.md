# xOpera TOSCA orchestrator
xOpera orchestration tool compliant with TOSCA YAML v1.3 in the making.

[![PyPI](https://img.shields.io/pypi/v/opera)](https://pypi.org/project/opera/)
[![Test PyPI](https://img.shields.io/badge/test%20pypi-dev%20version-blueviolet)](https://test.pypi.org/project/opera/)
[![CircleCI](https://img.shields.io/circleci/build/github/xlab-si/xopera-opera?label=circleci)](https://app.circleci.com/pipelines/github/xlab-si/xopera-opera)
[![Code Climate coverage](https://img.shields.io/codeclimate/coverage/xlab-si/xopera-opera)](https://codeclimate.com/github/xlab-si/xopera-opera)
[![GitHub contributors](https://img.shields.io/github/contributors/xlab-si/xopera-opera)](https://github.com/xlab-si/xopera-opera/graphs/contributors)
[![GitHub top language](https://img.shields.io/github/languages/top/xlab-si/xopera-opera)](https://github.com/xlab-si/xopera-opera)
[![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/xlab-si/xopera-opera)](https://github.com/xlab-si/xopera-opera)
[![PyPI - License](https://img.shields.io/pypi/l/opera)](https://github.com/xlab-si/xopera-opera/blob/master/LICENSE)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/opera)](https://pypi.org/project/opera/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/opera)](https://pypi.org/project/opera/)

<p align="center">
  <img src="https://raw.githubusercontent.com/xlab-si/xopera-docs/158ae10a3178e689a55ff2f993cf2d90c935c530/docs/images/xopera-black-text-side-mid.svg" width="60%" height="60%" title="xOpera logo">
</p>

| Aspect                         | Information                               |
| ------------------------------ |:-----------------------------------------:|
| Tool name                      | [opera]                                   |
| Documentation                  | [CLI documentation]                       |
| Orchestration standard         | [OASIS TOSCA Simple Profile in YAML v1.3] |
| Implementation tools           | [Ansible]                                 |
| Contact us                     | [xopera@xlab.si]                          |

## Table of Contents
  - [Introduction](#introduction)
  - [Prerequisites](#prerequisites)
  - [Installation and Quickstart](#installation-and-quickstart)
  - [License](#license)
  - [Contact](#contact)
  - [Acknowledgement](#acknowledgement)

## Introduction
`opera` aims to be a lightweight orchestrator compliant with [OASIS TOSCA]. 
The current compliance is with the [OASIS TOSCA Simple Profile in YAML v1.3]. 
The [xOpera documentation] for is available on GitHub pages. 
`opera` implements the TOSCA standard with [Ansible] automation tool where Ansible playbooks can be used as 
orchestration actuators within the TOSCA interface operations.

## Prerequisites
`opera` requires Python 3 and a virtual environment. 
In a typical modern Linux environment, we should already be set. 
In Ubuntu, however, we might need to run the following commands:

```console
$ sudo apt update
$ sudo apt install -y python3-venv python3-wheel python-wheel-common
```

## Installation and Quickstart
The orchestration tool is available on PyPI as a package named [opera]. 
Apart from the latest [PyPI production] version, you can also find the latest opera [PyPI development] version, which 
includes pre-releases so that you will be able to test the latest features before they are officially released.

The simplest way to test `opera` is to install it into Python virtual environment:

```console
$ mkdir ~/opera && cd ~/opera
$ python3 -m venv .venv && . .venv/bin/activate
(.venv) $ pip install opera
```

To test if everything is working as expected, we can now clone xOpera's
GitHub repository and try to deploy a hello-world service:

```console
(.venv) $ git clone git@github.com:xlab-si/xopera-opera.git
(.venv) $ cd xopera-opera/examples/hello
(.venv) $ opera deploy service.yaml
[Worker_0]   Deploying my-workstation_0
[Worker_0]   Deployment of my-workstation_0 complete
[Worker_0]   Deploying hello_0
[Worker_0]     Executing create on hello_0
[Worker_0]   Deployment of hello_0 complete
```

If nothing went wrong, new empty file has been created at `/tmp/playing-opera/hello/hello.txt`.

To delete the created directory, we can undeploy our stuff by running:

```console
(.venv) $ opera undeploy
[Worker_0]   Undeploying hello_0
[Worker_0]     Executing delete on hello_0
[Worker_0]   Undeployment of hello_0 complete
[Worker_0]   Undeploying my-workstation_0
[Worker_0]   Undeployment of my-workstation_0 complete
```

And that is it. 
For more startup examples please visit [examples folder], or go to [xopera-examples] repository if you wish to explore 
deeper with more complex xOpera examples. 
If you want to use opera commands from an API take a look at [xopera-api] repository. 
You can also take a look at the [xOpera SaaS] component, which is designed for business partners and enterprise users.
To find more about xOpera project visit our [xOpera documentation].

## License
This work is licensed under the [Apache License 2.0].

## Contact
You can contact the xOpera team by sending an email to [xopera@xlab.si].

## Acknowledgement
This project has received funding from the European Union’s Horizon 2020 research and innovation programme under Grant 
Agreements No. 825040 ([RADON]), No. 825480 ([SODALITE]) and No. 101000162 ([PIACERE]).

[opera]: https://pypi.org/project/opera/
[OASIS TOSCA Simple Profile in YAML v1.3]: https://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.3/TOSCA-Simple-Profile-YAML-v1.3.html
[xOpera documentation]: https://xlab-si.github.io/xopera-docs/
[CLI documentation]: https://xlab-si.github.io/xopera-docs/cli.html
[Ansible]: https://www.ansible.com/
[xopera@xlab.si]: mailto:xopera@xlab.si
[OASIS TOSCA]: https://www.oasis-open.org/committees/tc_home.php?wg_abbrev=tosca
[PyPI production]: https://pypi.org/project/opera/#history
[PyPI development]: https://test.pypi.org/project/opera/#history
[examples folder]: examples
[xopera-examples]: https://github.com/xlab-si/xopera-examples
[xopera-api]: https://github.com/xlab-si/xopera-api
[xOpera SaaS]: https://xlab-si.github.io/xopera-docs/saas.html
[Apache License 2.0]: https://www.apache.org/licenses/LICENSE-2.0
[RADON]: http://radon-h2020.eu
[SODALITE]: http://www.sodalite.eu/
[PIACERE]: https://www.piacere-project.eu/
