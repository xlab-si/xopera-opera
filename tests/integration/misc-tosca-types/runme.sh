#!/bin/bash
set -euo pipefail

# get opera executable
opera_executable="$1"

# perform integration test with TOSCA service template
# test opera info contents before everything
info_out="$($opera_executable info --format json)"
test "$(echo "$info_out" | jq -r .status)" = "null"

# validate
$opera_executable validate -i inputs.yaml service-template.yaml
# test opera info status after validate
info_out="$($opera_executable info --format json)"
test "$(echo "$info_out" | jq -r .status)" = "null"

# init
$opera_executable init service-template.yaml
# test opera info status after init
info_out="$($opera_executable info --format json)"
test "$(echo "$info_out" | jq -r .status)" = "initialized"

# deploy
$opera_executable deploy -i inputs.yaml
# test opera info status after deploy
info_out="$($opera_executable info --format json)"
test "$(echo "$info_out" | jq -r .status)" = "deployed"

# outputs
$opera_executable outputs
# test opera info status after outputs
info_out="$($opera_executable info --format json)"
test "$(echo "$info_out" | jq -r .status)" = "deployed"

# undeploy
$opera_executable undeploy
# test opera info status after undeploy
info_out="$($opera_executable info --format json)"
test "$(echo "$info_out" | jq -r .status)" = "undeployed"

# integration test with compressed CSAR
rm -rf .opera
mkdir -p csar-test
zip -r test.csar service-template.yaml modules TOSCA-Metadata
mv test.csar csar-test
mv inputs.yaml csar-test
cd csar-test
$opera_executable info --format yaml
$opera_executable init -i inputs.yaml test.csar
$opera_executable info -f json
$opera_executable deploy
$opera_executable info -f yaml
$opera_executable outputs
$opera_executable info -f json
$opera_executable undeploy
$opera_executable info
# number of created .opera folders should be 1
opera_count=$(ls -aR . | grep -c "^\.opera$")
if [ "$opera_count" -ne 1 ]; then exit 1; fi
