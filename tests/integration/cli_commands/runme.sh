#!/bin/bash
set -euo pipefail

# get opera executable
opera_executable="$1"

# perform an integration test for all of opera commands and their options
# prepare the CSAR zip file
zip -r test.csar service.yaml playbooks TOSCA-Metadata

# test opera info contents before everything
info_out="$($opera_executable info --format json)"
test "$(echo "$info_out" | jq -r .status)" = "null"

# validate service template and CSAR
$opera_executable validate --inputs inputs.yaml service.yaml
$opera_executable validate --inputs inputs.yaml test.csar

# test opera info status after validate
info_out="$($opera_executable info --format json)"
test "$(echo "$info_out" | jq -r .status)" = "null"

# test opera commands on TOSCA service template
# init service template without inputs
$opera_executable init service.yaml

# test opera info status after init
info_out="$($opera_executable info --format json)"
test "$(echo "$info_out" | jq -r .status)" = "initialized"

# deploy service template with inputs
$opera_executable deploy --inputs inputs.yaml

# test opera info status after deploy
info_out="$($opera_executable info --format json)"
test "$(echo "$info_out" | jq -r .status)" = "deployed"

# deploy service template again (with clean state and without yes/no prompts)
$opera_executable deploy --clean-state --force

# test opera info status after deploy
info_out="$($opera_executable info --format json)"
test "$(echo "$info_out" | jq -r .status)" = "deployed"

# init service template again (with clean option and with inputs)
$opera_executable init --clean service.yaml

# test opera info status after init
info_out="$($opera_executable info --format json)"
test "$(echo "$info_out" | jq -r .status)" = "initialized"

# deploy service template, but interrupt after 1 second
$opera_executable deploy &
DEPLOY_TIMEOUT_PID=$!
sleep 1s && kill -SIGKILL $DEPLOY_TIMEOUT_PID

# test opera info status after deploy
info_out="$($opera_executable info --format json)"
test "$(echo "$info_out" | jq -r .status)" = "interrupted"

# resume service template deploy (with force option to skip prompts)
$opera_executable deploy --resume --force

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


# test opera commands on CSAR
# prepare new opera storage folder
mkdir -p ./csar-test-dir

# initialize the CSAR (from the prepared compressed CSAR file)
# also provide inputs and relocate opera storage to some other folder
$opera_executable init -i inputs.yaml --instance-path ./csar-test-dir --clean test.csar

# test opera info status after init
info_out="$($opera_executable info --instance-path ./csar-test-dir --format json)"
test "$(echo "$info_out" | jq -r .status)" = "initialized"

# deploy the initialized CSAR (with four workers and with verbose option)
$opera_executable deploy -p ./csar-test-dir -w 4 -v

# test opera info status after deploy
info_out="$($opera_executable info -p ./csar-test-dir -f json)"
test "$(echo "$info_out" | jq -r .status)" = "deployed"

# deploy the initialized CSAR again (with clean state and without yes/no prompts)
$opera_executable deploy -p ./csar-test-dir -c -f

# test opera info status after deploy
info_out="$($opera_executable info -p ./csar-test-dir -f json)"
test "$(echo "$info_out" | jq -r .status)" = "deployed"

# take a look at opera outputs
$opera_executable outputs -p ./csar-test-dir

# test opera info status after outputs
info_out="$($opera_executable info -p ./csar-test-dir -f json)"
test "$(echo "$info_out" | jq -r .status)" = "deployed"

# undeploy the CSAR, but interrupt after 1 second
$opera_executable undeploy -p ./csar-test-dir &
UNDEPLOY_TIMEOUT_PID=$!
sleep 1s && kill -SIGKILL $UNDEPLOY_TIMEOUT_PID

# test opera info status after undeploy
info_out="$($opera_executable info -p ./csar-test-dir -f json)"
test "$(echo "$info_out" | jq -r .status)" = "interrupted"

# resume service template undeploy (with force option to skip prompts)
$opera_executable undeploy -p ./csar-test-dir -r -f

# test opera info status after undeploy
info_out="$($opera_executable info -p ./csar-test-dir -f json)"
test "$(echo "$info_out" | jq -r .status)" = "undeployed"

# run opera info without specified format (defaults to YAML format)
$opera_executable info -p ./csar-test-dir
