#!/bin/bash

set -eu

# 1: cd dir
# 2: args and code dir
run_pylint() {
    # we use the column command to format data, but not all shells/distributions have it
    # so just make a passthrough alias
    if ! command -v column >/dev/null; then
        column() {
            cat
        }
    fi

    cd_dir="$1"
    shift
    args_and_code_dir="$*"

    cd "$cd_dir"
    set +e
    # shellcheck disable=SC2086
    output=$(pylint --rcfile ../.sanity-config.ini $args_and_code_dir)
    exit_code="$?"
    set -e
    # shellcheck disable=SC2103
    cd ..

    echo "$output" \
        | jq -r '.[] | .path + "|" + (.line|tostring) + ":" + (.column|tostring) + "|" + .obj + " |" + ."message-id" + "|" + .symbol + "|" + .message' \
        | sort --unique \
        | column -t -s "|"

    return "$exit_code"
}

run_shellcheck() {
    files="$(find . -type f -name "*.sh" -not -path "*.venv*")"

    aggregate_exit_code="0"
    while read -r line; do
        set +e
        shellcheck --format tty "$line"
        exit_code="$?"
        set -e

        aggregate_exit_code="$((aggregate_exit_code + exit_code))"
    done <<< "$files"

    return "$aggregate_exit_code"
}

run_sanity() {
    set +e

    echo "Running pylint (source)"
    output_pylint_src=$(run_pylint src/ opera/)
    code_pylint_src="$?"

    echo "Running pylint (tests)"
    output_pylint_test=$(run_pylint tests/ --disable no-self-use --disable expression-not-assigned unit/)
    code_pylint_test="$?"

    echo "Running flake8"
    output_flake8=$(flake8 --statistics --config .sanity-config.ini)
    code_flake8="$?"

    echo "Running mypy"
    output_mypy=$(mypy --config-file .sanity-config.ini src/opera/ tests/unit/)
    code_mypy="$?"

    echo "Running bandit"
    output_bandit=$(bandit --recursive --aggregate file --format txt src/opera/ 2>&1)
    code_bandit="$?"

    echo "Running doc8"
    output_doc8=$(doc8 --config .sanity-config.ini docs/)
    code_doc8="$?"

    echo "Running pydocstyle"
    output_pydocstyle=$(pydocstyle --count --explain --config .sanity-config.ini src/opera/)
    code_pydocstyle="$?"

    echo "Running shellcheck"
    output_shellcheck=$(run_shellcheck)
    code_shellcheck="$?"

    set -e

    echo "pylint (src) output"
    echo "$code_pylint_src"
    echo "$output_pylint_src"
    echo "### pylint (tests) output ###"
    echo "exit code: $code_pylint_test"
    echo "$output_pylint_test"
    echo "### flake8 output ###"
    echo "exit code: $code_flake8"
    echo "$output_flake8"
    echo "### shellcheck output ###"
    echo "exit code: $code_shellcheck"
    echo "$output_shellcheck"
    echo "### mypy output ###"
    echo "exit code: $code_mypy"
    echo "$output_mypy"
    echo "### bandit output ###"
    echo "exit code: $code_bandit"
    echo "$output_bandit"
    echo "### doc8 output ###"
    echo "exit code: $code_doc8"
    echo "$output_doc8"
    echo "### pydocstyle output ###"
    echo "exit code: $code_pydocstyle"
    echo "$output_pydocstyle"
    echo "### shellcheck output ###"
    echo "exit code: $code_shellcheck"
    echo "$output_shellcheck"

    echo "Applied overrides:"
    grep -rinEe "noqa:|pylint:|nosec|# shellcheck" \
        --exclude-dir ".venv/" \
        --exclude-dir ".eggs/" \
        --exclude-dir ".git/" \
        --exclude-dir ".mypy_cache/" \
        --exclude-dir ".pytest_cache/" \
        .

    combined_exit_code="$((
        code_pylint_src
        + code_pylint_test
        + code_flake8
        + code_mypy
        + code_bandit
        + code_doc8
        + code_pydocstyle
        + code_shellcheck
    ))"
    exit "$combined_exit_code"
}

run_unit() {
    pytest tests/unit/
}

build_local_ci_container() {
    docker build -t xopera-opera-test --file - . <<EOF
FROM circleci/python:3.8
USER root
WORKDIR /test/
RUN sudo apt-get install -y \
    shellcheck
COPY Pipfile /test/Pipfile-complete
RUN head -n -3 Pipfile-complete > Pipfile \
    && pipenv install --dev

COPY . /test/
RUN pipenv install
EOF
}

command="$1"
shift

case "$command" in
    sanity)
        run_sanity
        ;;
    unit)
        run_unit
        ;;
    integration)
        build_local_ci_container
        ;;
    *)
        echo "Help."
        ;;
esac
