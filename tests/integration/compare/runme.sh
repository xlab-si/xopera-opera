#!/bin/bash
set -euo pipefail

# get opera executable
opera_executable="$1"

# perform integration test
$opera_executable deploy -i inputs1.yaml service1.yaml

# test opera info status after deploy
info_out="$($opera_executable info --format json)"
test "$(echo "$info_out" | jq -r .status)" = "deployed"

# test opera diff output
info_out="$($opera_executable diff -i inputs2.yaml service2.yaml --format json)"
test "$(echo "$info_out" | jq -r .nodes.added[0])" = "hello-5"
test "$(echo "$info_out" | jq -r .nodes.deleted[0])" = "hello-4"

$opera_executable update -i inputs2.yaml service2.yaml

info_out="$($opera_executable info --format json)"
test "$(echo "$info_out" | jq -r .status)" = "deployed"

$opera_executable update -i inputs2.yaml service2.yaml

info_out="$($opera_executable info --format json)"
test "$(echo "$info_out" | jq -r .status)" = "deployed"
