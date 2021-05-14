#!/bin/bash
set -euo pipefail

# get opera executable
opera_executable="$1"

# perform an integration test when execution gets interrupted

# deploy service template, but interrupt after 2 seconds
$opera_executable deploy service.yaml &
DEPLOY_TIMEOUT_PID=$!
sleep 2s && kill -SIGKILL $DEPLOY_TIMEOUT_PID

# test opera info status after interruption
info_out="$($opera_executable info -f json)"
test "$(echo "$info_out" | jq -r .status)" = "deploying"

# resume service template deploy (with force option to skip prompts)
$opera_executable deploy --resume --force

# test opera info status after deploy
info_out="$($opera_executable info -f json)"
test "$(echo "$info_out" | jq -r .status)" = "deployed"

# undeploy the CSAR, but interrupt after 2 seconds
$opera_executable undeploy &
UNDEPLOY_TIMEOUT_PID=$!
sleep 2s && kill -SIGKILL $UNDEPLOY_TIMEOUT_PID

# test opera info status after interruption
info_out="$($opera_executable info -f json)"
test "$(echo "$info_out" | jq -r .status)" = "undeploying"

# resume service template undeploy (with force option to skip prompts)
$opera_executable undeploy -r -f

# test opera info status after undeploy
info_out="$($opera_executable info -f json)"
test "$(echo "$info_out" | jq -r .status)" = "undeployed"
