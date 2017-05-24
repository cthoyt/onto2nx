# -*- coding: utf-8 -*-

from xml.etree import ElementTree as ET

import networkx as nx

__all__ = [
    'parse_owl',
    'OWLParser'
]

IRI = 'IRI'
AIRI = 'abbreviatedIRI'
OWL_NAMESPACES = {
    'owl': 'http://www.w3.org/2002/07/owl#',
    'dc': 'http://purl.org/dc/elements/1.1'
}


def parse_owl(iri):
    """Downloads and parses the ontology at a given IRI into a network object

    :param iri:
    :type iri: str
    :return: a networkx with the classes and individuals as nodes, and the subclass/instanceof relationships as edges
    :rtype: :class:`networkx.DiGraph`
    """
    return nx.DiGraph(iri=iri)


class OWLParser(nx.DiGraph):
    """A model of an OWL ontology in OWL/XML document using a NetworkX graph"""

    def __init__(self, content=None, file=None, **kwargs):
        """
        :param str content: The content of an XML file as a string
        :param file: input OWL file path or file-like object
        :type file: file or str
        """
        super(OWLParser, self).__init__(**kwargs)

        if file is not None:
            self.tree = ET.parse(file)
        elif content is not None:
            self.tree = ET.ElementTree(ET.fromstring(content))
        else:
            raise ValueError('Missing data source (file/content)')

        self.root = self.tree.getroot()
        self.graph['IRI'] = self.root.attrib['ontologyIRI']

        for el in self.root.findall('./owl:Declaration/owl:Class', OWL_NAMESPACES):
            self.add_node(self.get_iri(el.attrib), type="Class")

        for el in self.root.findall('./owl:Declaration/owl:NamedIndividual', OWL_NAMESPACES):
            self.add_node(self.get_iri(el.attrib), type="NamedIndividual")

        for el in self.root.findall('./owl:SubClassOf', OWL_NAMESPACES):
            if len(el) != 2:
                raise ValueError('something weird with SubClassOf: {} {}'.format(el, el.attrib))

            child = self.get_iri(el[0].attrib)

            if any(x in el[1].attrib for x in {IRI, AIRI}):
                parent = self.get_iri(el[1].attrib)
                self.add_edge(child, parent, type='SubClassOf')
            elif el[1].tag == '{http://www.w3.org/2002/07/owl#}ObjectSomeValuesFrom':  # check if ObjectSomeValuesFrom?
                object_property, parent = el[1]
                parent = self.get_iri(parent.attrib)
                relation = self.get_iri(object_property.attrib)
                self.add_edge(child, parent, type=relation)

        for el in self.root.findall('./owl:ClassAssertion', OWL_NAMESPACES):
            a = el.find('./owl:Class', OWL_NAMESPACES)
            if not self.has_iri(a.attrib):
                continue
            a = self.get_iri(a.attrib)

            b = el.find('./owl:NamedIndividual', OWL_NAMESPACES)
            if not self.has_iri(b.attrib):
                continue
            b = self.get_iri(b.attrib)
            self.add_edge(b, a, type="ClassAssertion")

    @property
    def iri(self):
        return self.graph['IRI']

    def has_iri(self, attribs):
        return any(key in {IRI, AIRI} for key in attribs)

    def strip_iri(self, iri):
        return iri.lstrip(self.graph[IRI]).lstrip('#').strip()

    def strip_airi(self, airi):
        l, r = airi.split(':')
        return r

    def get_iri(self, attribs):
        if IRI in attribs:
            return self.strip_iri(attribs[IRI])
        elif AIRI in attribs:
            return self.strip_airi(attribs[AIRI])
