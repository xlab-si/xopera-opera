#!/bin/bash
set -euo pipefail

# get opera executable
opera_executable="$1"

# perform integration test with service template
$opera_executable validate -i inputs.yaml service-template.yaml
$opera_executable deploy -i inputs.yaml service-template.yaml
$opera_executable outputs
$opera_executable undeploy

# integration test with compressed CSAR
rm -rf .opera
zip -r test.csar service-template.yaml modules TOSCA-Metadata
$opera_executable init -i inputs.yaml test.csar
$opera_executable deploy
$opera_executable outputs
$opera_executable undeploy
