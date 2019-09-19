from pathlib import PurePath, Path

from opera.parser.tosca.parser import ToscaParser
from opera.parser.yaml import Node
from .service_template import ServiceTemplate


# TODO: generify this across different top level documents and parser versions
class ServiceTemplateParser(ToscaParser):
    @classmethod
    def parse(cls, yaml_node: Node, base_path: Path, csar_path: PurePath) -> ServiceTemplate:
        service = ServiceTemplate.parse(yaml_node)
        service.visit("prefix_path", csar_path)
        service.merge_imports(ServiceTemplateParser, base_path)
        return service


Parser = ServiceTemplateParser
