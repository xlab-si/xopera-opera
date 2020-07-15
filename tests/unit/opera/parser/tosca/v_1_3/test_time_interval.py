from opera.parser.tosca.v_1_3.time_interval import TimeInterval


class TestParse:
    def test_minimal(self, yaml_ast):
        TimeInterval.parse(yaml_ast(
            """
            start_time: 2020-04-08T21:59:43.10-06:00
            end_time: 2022-04-08T21:59:43.10-06:00
            """
        ))
