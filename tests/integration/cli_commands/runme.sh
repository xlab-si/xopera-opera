#!/bin/bash
set -euo pipefail

# get opera executable
opera_executable="$1"

# perform an integration test for most important opera CLI commands and their options
# prepare the CSAR zip file
zip -r test.csar service.yaml playbooks TOSCA-Metadata

# test opera info contents before everything
info_out="$($opera_executable info --format json)"
test "$(echo "$info_out" | jq -r .status)" = "null"

# validate service template and CSAR (with YAML inputs)
$opera_executable validate --inputs inputs.yaml service.yaml
$opera_executable validate --inputs inputs.yaml test.csar

# test opera info status after validate
info_out="$($opera_executable info --format json)"
test "$(echo "$info_out" | jq -r .status)" = "null"

# test opera commands on TOSCA service template
# deploy service template with inputs
$opera_executable deploy --inputs inputs.yaml service.yaml

# test opera info status after deploy
info_out="$($opera_executable info --format json)"
test "$(echo "$info_out" | jq -r .status)" = "deployed"

# deploy service template again (with clean state and without yes/no prompts)
$opera_executable deploy --clean-state --force

# test opera info status after deploy
info_out="$($opera_executable info --format json)"
test "$(echo "$info_out" | jq -r .status)" = "deployed"

# deploy service template again (with clean state and without yes/no prompts)
# use YAML inputs
$opera_executable deploy --inputs inputs.yaml -c -f service.yaml

# test opera info status after deploy
info_out="$($opera_executable info --format json)"
test "$(echo "$info_out" | jq -r .status)" = "deployed"

# deploy service template again (with clean state and without yes/no prompts)
# use JSON inputs this time
$opera_executable deploy --inputs inputs.json -c -f service.yaml

# test opera info status after deploy
info_out="$($opera_executable info --format json)"
test "$(echo "$info_out" | jq -r .status)" = "deployed"

# deploy service template again
$opera_executable deploy

# test opera info status after deploy
info_out="$($opera_executable info --format json)"
test "$(echo "$info_out" | jq -r .status)" = "deployed"

# get deployment outputs
$opera_executable outputs

# test opera info status after outputs
info_out="$($opera_executable info --format json)"
test "$(echo "$info_out" | jq -r .status)" = "deployed"

# undeploy service template (with two workers and verbose option)
$opera_executable undeploy --workers 2 --verbose

# test opera info status after undeploy
info_out="$($opera_executable info --format json)"
test "$(echo "$info_out" | jq -r .status)" = "undeployed"

# run opera info with YAML format
$opera_executable info --format yaml

# unpack the created CSAR to the destination folder with opera unpackage
$opera_executable unpackage -d unpacked-csar test.csar

# test opera info status after unpackage
info_out="$($opera_executable info --format json)"
test "$(echo "$info_out" | jq -r .status)" = "undeployed"

# move to the root of the extracted CSAR and
# deploy the extracted service template with inputs
(
    cd unpacked-csar
    set -euo pipefail
    $opera_executable deploy --inputs ../inputs.yaml service.yaml

    # test opera info status after deploy
    info_out="$($opera_executable info --format json)"
    test "$(echo "$info_out" | jq -r .status)" = "deployed"
)

rm -rf unpacked-csar

# test opera commands on CSAR
# prepare new opera storage folder
mkdir -p ./csar-test-dir

# deploy the CSAR (with four workers and with verbose option)
$opera_executable deploy -i inputs.yaml --instance-path ./csar-test-dir --clean test.csar -w 4 -v

# test opera info status after deploy
info_out="$($opera_executable info -p ./csar-test-dir -f json)"
test "$(echo "$info_out" | jq -r .status)" = "deployed"

# deploy the CSAR again (with clean state and without yes/no prompts)
$opera_executable deploy -p ./csar-test-dir -c -f

# test opera info status after deploy
info_out="$($opera_executable info -p ./csar-test-dir -f json)"
test "$(echo "$info_out" | jq -r .status)" = "deployed"

# take a look at opera outputs
$opera_executable outputs -p ./csar-test-dir

# test opera info status after outputs
info_out="$($opera_executable info -p ./csar-test-dir -f json)"
test "$(echo "$info_out" | jq -r .status)" = "deployed"

# deploy the compressed CSAR again, now directly without deprecated opera init
# use clean state and disable yes/no prompts
$opera_executable deploy -i inputs.yaml --instance-path ./csar-test-dir --clean --force test.csar

# test opera info status after deploy
info_out="$($opera_executable info -p ./csar-test-dir -f json)"
test "$(echo "$info_out" | jq -r .status)" = "deployed"

# deploy the compressed CSAR again, now directly without deprecated opera init
# use clean state and disable yes/no prompts, use JSON inputs
$opera_executable deploy -i inputs.json -p ./csar-test-dir -c -f test.csar

# test opera info status after deploy
info_out="$($opera_executable info -p ./csar-test-dir -f json)"
test "$(echo "$info_out" | jq -r .status)" = "deployed"

# take a look at opera outputs
$opera_executable outputs -p ./csar-test-dir

# test opera info status after outputs
info_out="$($opera_executable info -p ./csar-test-dir -f json)"
test "$(echo "$info_out" | jq -r .status)" = "deployed"

# undeploy the CSAR
$opera_executable undeploy -p ./csar-test-dir

# test opera info status after undeploy
info_out="$($opera_executable info -p ./csar-test-dir -f json)"
test "$(echo "$info_out" | jq -r .status)" = "undeployed"

# run opera info without specified format (defaults to YAML format)
$opera_executable info -p ./csar-test-dir
