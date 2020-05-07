#!/usr/bin/env python

import setuptools


# configures that the local component of the version is constructed without commit hash
def local_scheme(version):
    return ""


setuptools.setup(use_scm_version={"local_scheme": local_scheme})
