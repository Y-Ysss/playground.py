from lxml import etree

parser = etree.XMLParser( remove_blank_text=True)
tree = etree.parse('data/xml/data.xml', parser)

for addr in tree.xpath('//PurchaseOrder'):
    ver_el = etree.Element('version')
    ver_el.text = 'xxxx'
    addr.insert(0, ver_el)

etree.indent(tree, space='    ')

with open('data/xml/test.xml', "wb") as f:
    # tree.write(f, xml_declaration=True, encoding='utf-8')
    f.write(etree.tostring(tree, encoding=None, method="xml",
             xml_declaration=None, pretty_print=False, with_tail=True, 
             standalone=None, doctype='<?xml version="1.0" encoding="UTF-8"?>', exclusive=False, 
             inclusive_ns_prefixes=None, with_comments=True, strip_text=False))
