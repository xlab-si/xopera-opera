#!/bin/bash
set -euo pipefail

# This is the script that is used to test the examples with the CI/CD.
# You can also run it manually with: ./runme.sh opera

# get opera executable
opera_executable="$1"

# test an example from ./artifacts
echo "Testing an example from ./artifacts ..."
mkdir artifacts/.opera
$opera_executable deploy --instance-path artifacts/.opera artifacts/service.yaml
$opera_executable outputs --instance-path artifacts/.opera

# test an example from ./attribute_mapping
echo "Testing an example from ./attribute_mapping ..."
mkdir attribute_mapping/.opera
$opera_executable deploy -p attribute_mapping/.opera attribute_mapping/service.yaml
$opera_executable outputs -p attribute_mapping/.opera

# test an example from ./capability_attributes_properties
echo "Testing an example from ./capability_attributes_properties ..."
mkdir capability_attributes_properties/.opera
$opera_executable deploy -p capability_attributes_properties/.opera capability_attributes_properties/service.yaml
$opera_executable outputs -p capability_attributes_properties/.opera

# test an example from ./hello
echo "Testing an example from ./hello ..."
mkdir hello/.opera
$opera_executable deploy -p hello/.opera hello/service.yaml
$opera_executable undeploy -p hello/.opera

# test an example from ./intrinsic_functions
echo "Testing an example from ./intrinsic_functions ..."
mkdir intrinsic_functions/.opera
$opera_executable deploy -p intrinsic_functions/.opera intrinsic_functions/service.yaml
$opera_executable outputs -p intrinsic_functions/.opera

# test an example from ./outputs
echo "Testing an example from ./outputs ..."
mkdir outputs/.opera
$opera_executable deploy -p outputs/.opera outputs/service.yaml
$opera_executable outputs -p intrinsic_functions/.opera

# test an example from ./policy_triggers
echo "Testing an example from ./policy_triggers ..."
mkdir policy_triggers/.opera
$opera_executable deploy -p policy_triggers/.opera policy_triggers/service.yaml

# test an example from ./relationship_outputs
echo "Testing an example from ./relationship_outputs ..."
mkdir relationship_outputs/.opera
$opera_executable deploy -p relationship_outputs/.opera relationship_outputs/service.yaml
$opera_executable outputs -p relationship_outputs/.opera

echo "All tests have finished successfully."

# an end-to-end example from ./nginx_openstack cannot be deployed directly
# with CI/CD because it requires special resources