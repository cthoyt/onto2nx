# -*- coding: utf-8 -*-

from .owl_rdf import parse_owl_rdf
from .owl_xml import parse_owl_xml

__all__ = ['parse_owl']


def parse_owl(url):
    """Downloads and parses an OWL resource in OWL/XML or any format supported by onto2nx/ontospy package.
    Is a thin wrapper around :func:`parse_owl_pybel` and :func:`parse_owl_rdf`.

    :param url: The URL to the OWL resource
    :type url: str
    :return: A directional graph representing the OWL document's hierarchy
    :rtype: networkx.DiGraph
    """
    try:
        return parse_owl_xml(url)
    except:
        return parse_owl_rdf(url)
