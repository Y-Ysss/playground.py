import re
from dataclasses import dataclass
raw = """person
    address
        street1 123 Bar St
        street2
        city Madison
        state WI
        zip 55555
    web
        email boo@baz.com
"""
ll = [{'name': 'person', 'value': '', 'level': 0},
 {'name': 'address', 'value': '', 'level': 1},
 {'name': 'street1', 'value': '123 Bar St', 'level': 2},
 {'name': 'street2', 'value': '', 'level': 2},
 {'name': 'city', 'value': 'Madison', 'level': 2},
 {'name': 'state', 'value': 'WI', 'level': 2},
 {'name': 'zip', 'value': 55555, 'level': 2},
 {'name': 'web', 'value': '', 'level': 1},
 {'name': 'email', 'value': 'boo@baz.com', 'level': 2}]


@dataclass
class IndentationObject():
    level: int = None
    name: str = None
    text: str = None
    raw_text:str = None
    childrens:list = None

    def __init__(self, line:str) -> None:
        self.level = indentatione_level(line)
        self.name = re.split('[\s\n]', line.strip())[0]
        self.text = line.strip()
        self.raw_text = line
        self.childrens = []


def indentatione_level(astr):
    return len(astr) - len(astr.lstrip())


def tt(nodes:list[IndentationObject], node:IndentationObject, level=0):
    # print(node.level)
    if node.level == level:
        nodes.append(node)
    elif level < node.level:
        # nodes[-1].childrens.append()
        tt(nodes[-1].childrens, node, node.level)
    elif node.level <= level:
        # nodes[-1].childrens.append()
        tt(nodes[-1], node, node.level)

import pprint
if __name__ == '__main__':
    nodes = []
    for line in iter(raw.splitlines()):
        tt(nodes, IndentationObject(line),)
    
        print(IndentationObject(line))
    #     nodes.append(IndentationObject(line))

    # for item in nodes:
    #     print(item)

    # print('----')
    # r = ttree_to_json(nodes)

    # print(r)