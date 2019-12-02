# -*- coding: utf-8 -*-

"""This module contains tools for parsing OWL/XML"""

from xml.etree import ElementTree as ET

import networkx as nx
from .utils import download

__all__ = [
    'parse_owl_xml',
    'OWLParser',
]

IRI = 'IRI'
AIRI = 'abbreviatedIRI'

OWL_NAMESPACES = {
    'owl': 'http://www.w3.org/2002/07/owl#',
    'dc': 'http://purl.org/dc/elements/1.1'
}


def parse_owl_xml(url):
    """Downloads and parses an OWL resource in OWL/XML format using the :class:`OWLParser`.

    :param str url: The URL to the OWL resource
    :return: A directional graph representing the OWL document's hierarchy
    :rtype: networkx.DiGraph
    """
    res = download(url)
    owl = OWLParser(content=res.content)
    return owl


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

        self.graph['IRI'] = self.root.attrib.get('ontologyIRI')

        for el in self.root.findall('./owl:Declaration/owl:Class', OWL_NAMESPACES):
            self.add_node(
                self.get_iri(el.attrib),
                type='Class', label=self.get_label(el.attrib))

        for el in self.root.findall('./owl:Declaration/owl:NamedIndividual', OWL_NAMESPACES):
            self.add_node(
                self.get_iri(el.attrib),
                type='NamedIndividual', label=self.get_label(el.attrib))

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

    def get_label(self, attribs):
        # TODO: implement this
        return ''
