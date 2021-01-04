.. _SaaS:

***********
xOpera SaaS
***********

The Software as a Service edition of xOpera is available at https://xopera-radon.xlab.si/ui/_.

It is a multi-user multi-platform multi-deployment multifunctional service offering all capabilities of the
console-based ``opera``, providing all of its functionalities.

Please read the warnings below, as you accept some inherent risks when using xOpera-SaaS

Using the browser version is straightforward.

Using the xOpera SaaS API through ``curl``::

    csar_base64="$(base64 --wrap 0 test.csar)"
    api="https://xopera-radon.xlab.si/api"
    auth_base_url="https://openid-radon.xlab.si"
    secret_base64="$(echo 'hello!' | base64 -)"

    your_username=YOUR_USERNAME
    your_password=YOUR_PASSWORD

    alias cookiecurl="curl -sSL --cookie-jar cookiejar.txt --cookie cookiejar.txt"
    response_from_credentials_redirected_to_next_auth="$(cookiecurl $api/credential)"

    ### login flow - RADON auth ###
        redirect_url_to_radonauth="$(echo $response_from_credentials_redirected_to_next_auth | xmllint --html --xpath "string(//a[@id='zocial-keycloak-xlab-oidc-provider-to-keycloak-radon']/@href)" - 2>/dev/null)"
        response_radonauth="$(cookiecurl ${auth_base_url}${redirect_url_to_radonauth})"

        login_url_radonauth="$(echo $response_radonauth | xmllint --html --xpath "string(//form[@id='kc-form-login']/@action)" - 2>/dev/null)"
        cookiecurl "$login_url_radonauth" -d "username=$your_username" -d "password=$your_password" -d credentialId=""
        redirect_url="$redirect_url_radonauth"
    ### end RADON auth login flow ###

    ### login flow - internal auth ###
        redirect_url_internal="$(echo $response_from_credentials_redirected_to_next_auth | xmllint --html --xpath "string(//form[@id='kc-form-login']/@action)" - 2>/dev/null)"
        redirect_url="$redirect_url_internal"
    ### end internal auth login flow ###

    # final login step, sets cookies and automatically completes the /credential request
    cookiecurl "$redirect_url" -d "username=$your_username" -d "password=$your_password" -d credentialId=""

    # normal usage
    cookiecurl "$api/credential"
    cookiecurl "$api/credential" -XPOST -d "{\"name\": \"credential1\", \"path\": \"/tmp/credential.txt\", \"contents\": \"$secret_base64\"}"
    cookiecurl "$api/credential"
    cookiecurl "$api/credential/1"
    cookiecurl "$api/workspace"
    cookiecurl "$api/workspace" -XPOST -d '{"name": "workspace1"}'
    cookiecurl "$api/workspace/1/credential/1" -XPUT
    cookiecurl "$api/workspace/1/credential"
    cookiecurl "$api/credential/1"
    cookiecurl "$api/workspace/1"
    cookiecurl "$api/workspace/1/project" -XPOST -d "{\"name\": \"myproject\", \"csar\": \"$csar_base64\"}"
    cookiecurl "$api/workspace/1/project"
    cookiecurl "$api/workspace/1"
    cookiecurl "$api/workspace/1/project/1/creationStatus"
    cookiecurl "$api/workspace/1/project/1/debugPackage"

    # interaction with the project (identical to xopera-api), instructions copied from there
    project_url="$api/workspace/1/project/1"
    cookiecurl "$project_url/status"
    cookiecurl "$project_url/validate" -XPOST -H "Content-Type: application/json" -d @inputs-request.json
    cookiecurl "$project_url/deploy" -XPOST -H "Content-Type: application/json" -d @inputs-request.json
    cookiecurl "$project_url/status" | jq
    cookiecurl "$project_url/outputs"
    cookiecurl "$project_url/undeploy" -XPOST

For further interaction with each project, see
`the xopera-api specification <https://github.com/xlab-si/xopera-api/blob/master/openapi-spec.yml>`_


====================================================
Warnings about your credentials and general security
====================================================

Your credentials - not for xOpera-SaaS, but those you add for services you access in CSARs etc - are stored in
plaintext on the server xOpera-SaaS is running on.
All assigned workspaces have access to them, as they have control of the filesystem, therefore all users with access
to the workspace also have access to them.
You need to use caution with the credentials you submit.

If you request xOpera-SaaS server administrators to help you or access your project, they will also be in a position
to access the credentials.
Whenever possible, use temporary credentials with limited access to the smallest required set of capabilities
to improve you security.
