#!/bin/bash
set -euo pipefail

# get opera executable
opera_executable="$1"

# perform integration test with TOSCA service template
# test opera info contents before everything
$opera_executable info --format json
$opera_executable validate -i inputs.yaml service-template.yaml
$opera_executable info --format yaml
$opera_executable init service-template.yaml
$opera_executable info -f json
$opera_executable deploy -i inputs.yaml
$opera_executable info -f yaml
$opera_executable outputs
$opera_executable info -f json
$opera_executable undeploy
$opera_executable info

# integration test with compressed CSAR
# warning: opera init is deprecated and could be removed in the future
rm -rf .opera
mkdir -p csar-test
zip -r test.csar service-template.yaml modules TOSCA-Metadata
mv test.csar csar-test
cp inputs.yaml csar-test
cd csar-test
$opera_executable info -f yaml
# deploy compressed CSAR (with opera init)
$opera_executable init -i inputs.yaml test.csar
$opera_executable info -f json
$opera_executable deploy
$opera_executable info -f yaml
$opera_executable outputs
$opera_executable info -f json
$opera_executable undeploy
$opera_executable info
# deploy compressed CSAR again (without opera init)
$opera_executable deploy -i inputs.yaml -c -f test.csar
$opera_executable info -f json
$opera_executable outputs
$opera_executable info -f json
$opera_executable undeploy
$opera_executable info
# use opera unpackage and unpack the CSAR and deploy the extracted TOSCA files
$opera_executable unpackage -d unpacked-csar test.csar
$opera_executable info
cp inputs.yaml unpacked-csar
cd unpacked-csar
$opera_executable deploy -i inputs.yaml service-template.yaml
$opera_executable info
# number of created .opera folders should be 1
opera_count=$(ls -aR . | grep -c "^\.opera$")
if [ "$opera_count" -ne 1 ]; then exit 1; fi
