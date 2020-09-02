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
mkdir -p csar-test
zip -r test.csar service-template.yaml modules TOSCA-Metadata
mv test.csar csar-test
mv inputs.yaml csar-test
cd csar-test
$opera_executable init -i inputs.yaml test.csar
$opera_executable deploy
$opera_executable outputs
$opera_executable undeploy
# number of created .opera folders should be 1
opera_count=$(ls -aR . | grep -c "^\.opera$")
if [ "$opera_count" -ne 1 ]; then exit 1; fi
