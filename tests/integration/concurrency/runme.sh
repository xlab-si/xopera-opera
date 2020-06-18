#!/bin/bash
set -euo pipefail

# get opera executable
opera_executable="$1"

# perform integration test
$opera_executable deploy -w 10 service.yaml
$opera_executable undeploy -w 10
