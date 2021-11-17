#!/bin/bash
set -euo pipefail

# get opera executable
opera_executable="$1"

# perform integration test
$opera_executable validate service.yaml
$opera_executable deploy service.yaml
# scale down by calling scale_down_trigger with notification_scale_down.json notification file
$opera_executable notify -e scale_down_trigger -n files/notification_scale_down.json
# scale up by calling scale_up_trigger with notification_scale_up.json notification file
$opera_executable notify -e scale_up_trigger -n files/notification_scale_up.json
$opera_executable undeploy
