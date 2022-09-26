#!/bin/bash
set -euo pipefail

# get opera executable
opera_executable="$1"

# perform integration test
$opera_executable info
$opera_executable validate service.yaml
$opera_executable info
$opera_executable deploy service.yaml
$opera_executable info
$opera_executable undeploy
$opera_executable info
