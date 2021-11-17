#!/bin/bash
set -euo pipefail

# get opera executable
opera_executable="$1"

# perform an integration test with compressed CSAR
# prepare the TOSCA CSAR zip file manually
rm -rf .opera
mkdir -p csar-test
zip -r test.csar service.yaml modules TOSCA-Metadata
mv test.csar csar-test
cp inputs.yaml csar-test
cd csar-test

# deploy the compressed TOSCA CSAR
$opera_executable info
$opera_executable validate -i inputs.yaml test.csar
$opera_executable info --format yaml
$opera_executable deploy -i inputs.yaml test.csar
$opera_executable info -f yaml
$opera_executable outputs
$opera_executable info -f json
$opera_executable undeploy
$opera_executable info

# number of created .opera folders should be 1
# shellcheck disable=SC1117,SC2010
opera_count=$(ls -aR . | grep -c "^\.opera$")
if [ "$opera_count" -ne 1 ]; then
    exit 1
fi
