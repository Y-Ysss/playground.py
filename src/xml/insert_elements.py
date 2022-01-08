import argparse
import sys
from pathlib import Path

import yaml
from lxml import etree


def resource_path(*args:str) -> Path:
    base_path = ''
    try:
        sys._MEIPASS
        base_path = Path(sys.argv[0]).absolute().parent
    except AttributeError:
        base_path = Path.cwd()
    return base_path.joinpath(*args)

def insert(tree, opt, pos=0):
    
    for addr in tree.xpath(opt.get('search')):
        ver_el = etree.Element(opt.get('tag'))
        ver_el.text = opt.get('body')
        addr.insert(pos, ver_el)
    return tree

def append(tree, opt):
    for addr in tree.xpath(opt.get('search')):
        ver_el = etree.Element(opt.get('tag'))
        ver_el.text = opt.get('body')
        addr.append(ver_el)
    return tree

if __name__ == '__main__':
    # config_file = resource_path('config.yaml')
    # with config_file.open('r', encoding='utf-8') as f:
    #     config = yaml.safe_load(f)
    s = """
    insert_top:
        - {'search':'//PurchaseOrder', 'tag':'ver', 'body':'xxx'}
    insert_tail:
        - {'search':'//PurchaseOrder', 'tag':'verx', 'body':'xxx'}
    
    """
    config = yaml.load(s)
    print(config.get("insert_top"))


    parser = etree.XMLParser( remove_blank_text=True)
    tree = etree.parse('data/xml/data.xml', parser)
    
    insert(tree, config.get('insert_top')[0])
    append(tree, config.get('insert_tail')[0])

    
    etree.indent(tree, space='    ')

    with open('data/xml/test.xml', "wb") as f:
        # tree.write(f, xml_declaration=True, encoding='utf-8')
        f.write(etree.tostring(tree, encoding='utf-8', method="xml", doctype='<?xml version="1.0" encoding="UTF-8"?>'))