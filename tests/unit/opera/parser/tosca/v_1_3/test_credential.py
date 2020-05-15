from opera.parser.tosca.v_1_3.credential import Credential


class TestParse:
    def test_full(self, yaml_ast):
        Credential.parse(yaml_ast(
            """
            protocol: tcp
            token_type: password
            token: my_password
            keys:
              first: key
              yet: another key
            user: my_user
            """
        ))

    def test_minimal(self, yaml_ast):
        Credential.parse(yaml_ast(
            """
            token: my_password
            """
        ))
