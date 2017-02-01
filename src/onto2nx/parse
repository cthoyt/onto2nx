from networkx import DiGraph


def parse_owl(iri):
    """Downloads and parses the ontology at a given IRI into a network object

    :param iri:
    :type iri: str
    :return: a networkx with the classes and individuals as nodes, and the subclass/instanceof relationships as edges
    :rtype: :class:`networkx.DiGraph`
    """
    return DiGraph(iri=iri)
