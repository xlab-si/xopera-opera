#!/bin/bash
set -euo pipefail

# get opera executable
opera_executable="$1"

# perform integration test
$opera_executable validate -i inputs.yaml service-template.yaml
$opera_executable deploy -i inputs.yaml service-template.yaml
$opera_executable outputs
$opera_executable undeploy
