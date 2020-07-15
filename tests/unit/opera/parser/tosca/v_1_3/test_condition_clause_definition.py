import pytest

from opera.error import ParseError
from opera.parser.tosca.v_1_3.condition_clause_definition import ConditionClauseDefinition


class TestParseValidate:
    def test_valid_clause_direct_assertion(self, yaml_ast):
        test_yaml = yaml_ast(
            """
            my_attribute: [ { equal: 42 } ]
            """
        )
        ConditionClauseDefinition.parse(test_yaml)
        ConditionClauseDefinition.validate(test_yaml)

    def test_valid_clause_direct_assertion_list(self, yaml_ast):
        test_yaml = yaml_ast(
            """
            my_attribute: [ { min_length: 1 }, { min_length: 11 } ]
            """
        )
        ConditionClauseDefinition.parse(test_yaml)
        ConditionClauseDefinition.validate(test_yaml)

    def test_valid_clause_not(self, yaml_ast):
        test_yaml = yaml_ast(
            """
            not:
              - my_attribute: [{equal: my_value}]
              - my_other_attribute: [{equal: my_other_value}]
            """
        )
        ConditionClauseDefinition.parse(test_yaml)
        ConditionClauseDefinition.validate(test_yaml)

    def test_valid_clause_and(self, yaml_ast):
        test_yaml = yaml_ast(
            """
            and:
              - my_attribute: [{equal: my_value}]
              - my_other_attribute: [{equal: my_other_value}]
            """
        )
        ConditionClauseDefinition.parse(test_yaml)
        ConditionClauseDefinition.validate(test_yaml)

    def test_valid_clause_not_and(self, yaml_ast):
        test_yaml = yaml_ast(
            """
            not:
              - and:
                - my_attribute: [ { greater_than: 42 } ]
                - my_other_attribute: [ { less_than: 1000 } ]
            """
        )
        ConditionClauseDefinition.parse(test_yaml)
        ConditionClauseDefinition.validate(test_yaml)

    def test_valid_clause_or(self, yaml_ast):
        test_yaml = yaml_ast(
            """
            or:
              - my_attribute: [{equal: my_value}]
              - my_other_attribute: [{equal: my_other_value}]
            """
        )
        ConditionClauseDefinition.parse(test_yaml)
        ConditionClauseDefinition.validate(test_yaml)

    def test_valid_clause_or_not(self, yaml_ast):
        test_yaml = yaml_ast(
            """
            or:
              - not:
                - my_attribute1: [{equal: value1}]
              - not:
                - my_attribute2: [{equal: value1}]
            """
        )
        ConditionClauseDefinition.parse(test_yaml)
        ConditionClauseDefinition.validate(test_yaml)

    def test_valid_clause_or_and_not(self, yaml_ast):
        test_yaml = yaml_ast(
            """
            or:
              - and:
                - protocol: { equal: http }
                - port: { equal: 80 }
              - and:
                - protocol: { equal: https }
                - port: { equal: 431 }
            """
        )
        ConditionClauseDefinition.parse(test_yaml)
        ConditionClauseDefinition.validate(test_yaml)

    def test_valid_clause_nested(self, yaml_ast):
        test_yaml = yaml_ast(
            """
            or:
              - not:
                - my_attribute1: [{equal: value1}]
              - and:
                - my_attribute2: { equal: value2 }
                - and:
                  - my_attribute3: { equal: value3 }
                - and:
                  - my_attribute4: { equal: value4 }
                  - my_attribute5: { equal: value5 }
                - or:
                  - my_attribute6: { equal: value6 }
                  - my_attribute7: { equal: value7 }
                  - or:
                    - not:
                      - my_attribute8: { equal: value8 }
                      - my_attribute9: { equal: value9 }
                    - and:
                      - not:
                        - or:
                          - my_attribute10: { equal: value10 }
                        - my_attribute11: { equal: value11 }
              - and:
                - my_attribute12: { equal: value12 }
                - my_attribute13: { equal: value13 }
            """
        )
        ConditionClauseDefinition.parse(test_yaml)
        ConditionClauseDefinition.validate(test_yaml)

    def test_invalid_clause_not(self, yaml_ast):
        test_yaml = yaml_ast(
            """
            nott:
              - my_attribute: [{equal: my_value}]
              - my_other_attribute: [{equal: my_other_value}]
            """
        )
        with pytest.raises(ParseError):
            ConditionClauseDefinition.parse(test_yaml)
            ConditionClauseDefinition.validate(test_yaml)

    def test_invalid_clause_nested(self, yaml_ast):
        test_yaml = yaml_ast(
            """
            or:
              - not:
              - and:
                - my_attribute2: { equals: value2 }
                - and:
                  - my_attribute3: { equal: value3 }
                - and:
                  - my_attribute4: { equal: value4 }
                  - my_attribute5: { equal: value5 }
                - or:
                  - my_attribute6: { equal: value6 }
                  - my_attribute7: { equal: value7 }
                  - or:
                    - not:
                      - my_attribute8: { equal: value8 }
                      - my_attribute9: { equal: value9 }
                    - and:
                      - not:
                        - or:
                          - my_attribute10: { equal: value10 }
                        - my_attribute11: { equal: value11 }
              - and:
                - my_attribute12: { equal: value12 }
                - my_attribute13: { equal: value13 }
            """
        )
        with pytest.raises(ParseError):
            ConditionClauseDefinition.parse(test_yaml)
            ConditionClauseDefinition.validate(test_yaml)

    def test_invalid_clause_assert(self, yaml_ast):
        test_yaml = yaml_ast(
            """
            assert:
              - my_attribute: [{equal: my_value}]
              - my_other_attribute: [{in_range: [1, 10]}]
            """
        )
        with pytest.raises(ParseError):
            ConditionClauseDefinition.parse(test_yaml)
            ConditionClauseDefinition.validate(test_yaml)
