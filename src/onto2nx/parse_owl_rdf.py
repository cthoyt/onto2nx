# -*- coding: utf-8 -*-

import networkx as nx
from requests.compat import urldefrag

from .ontospy import Ontospy

__all__ = [
    'parse_owl_rdf'
]


def parse_owl_rdf(iri):
    """
    
    :param iri: 
    :type iri: str
    :return:
    :rtype: network.DiGraph
    """
    g = nx.DiGraph(IRI=iri)
    o = Ontospy(iri)

    for cls in o.classes:
        g.add_node(cls.locale, type='Class')

        for parent in cls.parents():
            g.add_edge(cls.locale, parent.locale, type='SubClassOf')

        for instance in cls.instances():
            _, frag = urldefrag(instance)
            g.add_edge(frag, cls.locale, type='ClassAssertion')

    return g
